"""
publisher.py — Public MQTT upstream publisher.

Key performance design:
  - Sensor data is BATCHED: DataModel calls on_sensor_update() to stage
    pending readings into a dict (O(1), no network I/O in MQTT callback).
  - A background flush thread wakes every sensor_upload_interval seconds,
    grabs a snapshot, and publishes each pending sensor — decoupled from
    the receive path entirely.
  - All network I/O happens in the flush/heartbeat/bind threads — the
    MQTT receive callback thread is never blocked.
  - Bind events and heartbeat still use their own timers (30s each).
"""

import json
import logging
import threading
import time
from datetime import datetime, timezone

log = logging.getLogger(__name__)

try:
    import psutil as _psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


def _utcnow() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


class Publisher:
    """
    Upstream publisher with batched sensor upload.

    sensor_upload_interval (seconds):
      How often to flush pending sensor readings to the public broker.
      Default 5s.  Set to 0 for immediate (use only on low-traffic setups).
    """

    HEARTBEAT_INTERVAL    = 30
    BIND_PERIODIC_INTERVAL = 30

    def __init__(self, mqtt_client, site_name: str, gateway_id: str,
                 sensor_upload_interval: float = 5.0):
        self._client   = mqtt_client
        self._site     = site_name
        self._gw       = gateway_id
        self._prefix   = f"cs/{site_name}/{gateway_id}"
        self._interval = max(0.5, float(sensor_upload_interval))

        self._lock     = threading.Lock()
        self._bind     = False
        self._start_ts = time.monotonic()
        self._tx_count = 0
        self._running  = False

        # Pending sensor readings: {key: payload_dict}
        # on_sensor_update() writes here; flush thread reads + clears
        self._pending: dict[str, dict] = {}

    # ── Topic properties ──────────────────────────────────────────────────────

    @property
    def topic_bind(self)      -> str: return f"{self._prefix}/bind"
    @property
    def topic_sensor(self)    -> str: return f"{self._prefix}/sensor"
    @property
    def topic_heartbeat(self) -> str: return f"{self._prefix}/heartbeat"

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> "Publisher":
        self._running = True
        for name, target in [
            ("sensor_flush",  self._flush_loop),
            ("heartbeat",     self._heartbeat_loop),
            ("bind_periodic", self._bind_periodic_loop),
        ]:
            t = threading.Thread(target=target, name=f"pub_{name}", daemon=True)
            t.start()
        log.info("Publisher started  prefix=%s  interval=%.1fs",
                 self._prefix, self._interval)
        return self

    def stop(self):
        self._running = False

    # ── Called by DataModel (MQTT receive thread) ─────────────────────────────

    def on_sensor_update(
        self,
        key:       str,
        meta:      dict,
        value,
        raw_value,
        device_id: str,
        node_id:   int,
        bind:      bool,
        battery:   int | None = None,
        signal:    int | None = None,
    ) -> None:
        """
        Stage a sensor reading for the next flush.
        O(1), no network I/O — safe to call from the MQTT receive thread.
        """
        level    = self._alarm_level(value, meta)
        is_alarm = level in ("LV1", "LV2")

        payload = {
            "site_name":    self._site,
            "gateway_id":   self._gw,
            "timestamp":    _utcnow(),
            "node_id":      node_id,
            "device_id":    int(device_id) if str(device_id).isdigit() else 0,
            "bind":         bind,
            "sensor_type":  key,
            "display_name": meta.get("name", key),
            "value":        raw_value,
            "unit":         meta.get("unit", ""),
            "battery":      battery,
            "signal":       signal,
            "alarm":        is_alarm,
            "alarm_level":  level,
            "lv1_range":    meta.get("lv1", []),
            "lv2_range":    meta.get("lv2", []),
        }

        with self._lock:
            # Overwrite previous pending value — only latest matters
            self._pending[key] = payload

    def on_bind_change(self, is_bound: bool) -> None:
        """Publish bind event immediately (state change = high priority)."""
        with self._lock:
            self._bind = is_bound
        # Publish in a short-lived thread to avoid blocking MQTT receive
        t = threading.Thread(
            target=self._publish_bind,
            args=("changed",),
            daemon=True
        )
        t.start()
        log.info("Bind changed → %s", "bind" if is_bound else "unbind")

    # ── Flush loop (sensor data) ──────────────────────────────────────────────

    def _flush_loop(self):
        """Wake every sensor_upload_interval, publish all pending readings."""
        time.sleep(2)   # brief startup delay
        while self._running:
            start = time.monotonic()
            self._flush_pending()
            elapsed = time.monotonic() - start
            sleep_for = max(0.0, self._interval - elapsed)
            time.sleep(sleep_for)

    def _flush_pending(self):
        with self._lock:
            if not self._pending:
                return
            batch = dict(self._pending)
            self._pending.clear()

        published = 0
        for key, payload in batch.items():
            if self._publish(self.topic_sensor, payload):
                published += 1

        if published:
            log.debug("Flushed %d sensor readings to %s", published, self.topic_sensor)

    # ── Heartbeat loop ────────────────────────────────────────────────────────

    def _heartbeat_loop(self):
        time.sleep(3)
        while self._running:
            try:
                self._publish_heartbeat()
            except Exception as exc:
                log.error("Heartbeat error: %s", exc)
            time.sleep(self.HEARTBEAT_INTERVAL)

    # ── Bind periodic loop ────────────────────────────────────────────────────

    def _bind_periodic_loop(self):
        time.sleep(6)
        while self._running:
            try:
                self._publish_bind("periodic")
            except Exception as exc:
                log.error("Bind periodic error: %s", exc)
            time.sleep(self.BIND_PERIODIC_INTERVAL)

    # ── Publish helpers ───────────────────────────────────────────────────────

    def _publish_bind(self, event: str) -> None:
        with self._lock:
            is_bound = self._bind
        payload = {
            "site_name":   self._site,
            "gateway_id":  self._gw,
            "timestamp":   _utcnow(),
            "type":        "bind_event",
            "bind":        is_bound,
            "bind_status": "bind" if is_bound else "unbind",
            "event":       event,
        }
        self._publish(self.topic_bind, payload)

    def _publish_heartbeat(self) -> None:
        with self._lock:
            is_bound = self._bind
            tx       = self._tx_count

        uptime_sec = int(time.monotonic() - self._start_ts)
        h, rem     = divmod(uptime_sec, 3600)
        m, s       = divmod(rem, 60)

        cpu_pct = mem_mb = mem_pct = cpu_temp = threads = None
        if _HAS_PSUTIL:
            try:
                cpu_pct = _psutil.cpu_percent(interval=None)
                mi      = _psutil.Process().memory_info()
                mem_mb  = round(mi.rss / 1024 / 1024, 1)
                vm      = _psutil.virtual_memory()
                mem_pct = vm.percent
                threads = _psutil.Process().num_threads()
                temps   = getattr(_psutil, "sensors_temperatures", lambda: {})()
                if temps:
                    for k in ("coretemp", "cpu_thermal", "k10temp"):
                        if k in temps and temps[k]:
                            cpu_temp = round(temps[k][0].current, 1)
                            break
            except Exception:
                pass

        payload = {
            "site_name":      self._site,
            "gateway_id":     self._gw,
            "timestamp":      _utcnow(),
            "type":           "heartbeat",
            "bind":           is_bound,
            "bind_status":    "bind" if is_bound else "unbind",
            "uptime":         f"{h:02d}:{m:02d}:{s:02d}",
            "cpu_percent":    cpu_pct,
            "cpu_temp_c":     cpu_temp,
            "memory_mb":      mem_mb,
            "sys_memory_pct": mem_pct,
            "thread_count":   threads,
            "mqtt_tx_count":  tx,
            "network": {
                "private_connected": self._net_status("private"),
                "public_connected":  self._net_status("public"),
            },
            "active_alarms": [],
            "alarm_count":   0,
        }
        self._publish(self.topic_heartbeat, payload)
        log.debug("Heartbeat  uptime=%s  bind=%s", payload["uptime"], is_bound)

    def _publish(self, topic: str, payload: dict) -> bool:
        if self._client is None:
            return False
        try:
            msg = json.dumps(payload, ensure_ascii=False)
            ok  = self._client.publish(topic, msg)
            if ok:
                with self._lock:
                    self._tx_count += 1
                log.debug("TX → %s  |  %s", topic, msg)
            else:
                log.warning("TX FAILED → %s", topic)
            return ok
        except Exception as exc:
            log.error("Publish error on %s: %s", topic, exc)
            return False

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _alarm_level(value, meta: dict):
        if value is None:
            return None
        try:
            v = float(value)
        except (TypeError, ValueError):
            return None
        lv1_lo, lv1_hi = meta.get("lv1", [0, 9999])
        lv2_lo, lv2_hi = meta.get("lv2", [0, 9999])
        if not (lv2_lo <= v <= lv2_hi): return "LV2"
        if not (lv1_lo <= v <= lv1_hi): return "LV1"
        return None

    @staticmethod
    def _net_status(role: str) -> bool:
        try:
            from core.data_model import get_mqtt_status
            return get_mqtt_status(role)
        except Exception:
            return False
