"""
mqtt_client.py — Paho MQTT wrapper with auto-reconnection.

Network status is driven purely by on_connect / on_disconnect callbacks —
never by individual publish results — to prevent status LED flickering.
"""

import logging
import os
import time
import threading
from datetime import datetime

import paho.mqtt.client as mqtt

from core import data_model

log = logging.getLogger(__name__)


class MQTTClient:
    def __init__(
        self,
        broker:   str,
        port:     int,
        topic:    str,
        username: str = "SCIL-admin",
        password: str = "dotdoq-pyCboj-daqne9",
        role:     str = "public",
    ):
        self.broker = broker
        self.port   = port
        self.topic  = topic
        self.role   = role
        self._connected = False

        cid = f"cs_monitor_{role}_{os.urandom(4).hex()}"
        self._client = mqtt.Client(client_id=cid)
        self._client.username_pw_set(username, password)
        self._client.on_connect    = self._on_connect
        self._client.on_message    = self._on_message
        self._client.on_disconnect = self._on_disconnect

        # Uncomment for TLS:
        # import ssl
        # self._client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)

    # ── Callbacks ────────────────────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            log.info("MQTT [%s] connected to %s:%d", self.role, self.broker, self.port)
            data_model.set_mqtt_status(self.role, True)
            if self.topic:          # None = publish-only, skip subscribe
                client.subscribe(self.topic)
                log.info("MQTT [%s] subscribed to %s", self.role, self.topic)
        else:
            self._connected = False
            log.warning("MQTT [%s] connect failed rc=%d", self.role, rc)
            data_model.set_mqtt_status(self.role, False)

    def _on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8")
        except Exception:
            payload_str = repr(msg.payload)
        log.debug("MQTT [%s] ← topic=%s  payload=%s", self.role, msg.topic, payload_str)
        data_model.add_msg_to_buffer(msg)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        log.warning("MQTT [%s] disconnected rc=%d", self.role, rc)
        data_model.set_mqtt_status(self.role, False)

    # ── Background connection loop ───────────────────────────────────────────

    def _connect_loop(self):
        while True:
            try:
                self._client.connect(self.broker, self.port, keepalive=60)
                self._client.loop_forever(retry_first_connection=True)
            except Exception as exc:
                self._connected = False
                data_model.set_mqtt_status(self.role, False)
                log.error("MQTT [%s] error: %s — retry in 10s", self.role, exc)
                print(
                    f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
                    f"MQTT [{self.role}] error: {exc} — retrying in 10 s"
                )
                time.sleep(10)

    def start(self):
        t = threading.Thread(target=self._connect_loop, daemon=True)
        t.start()
        return self

    def stop(self):
        self._client.disconnect()

    # ── Publish — NEVER touches status ──────────────────────────────────────

    def publish(self, topic: str, message: str) -> bool:
        if not self._connected:
            return False
        try:
            rc, _ = self._client.publish(topic, message)
            if rc != 0:
                log.warning("MQTT [%s] publish failed to %s", self.role, topic)
            return rc == 0
        except Exception as exc:
            log.error("MQTT [%s] publish error: %s", self.role, exc)
            return False


def make_client(broker: str, port: int, topic: str, role: str) -> MQTTClient:
    """Convenience factory — creates and starts the client."""
    return MQTTClient(broker=broker, port=port, topic=topic, role=role).start()
