import os
import time
import threading
import logging
from datetime import datetime

import paho.mqtt.client as mqtt
import funciton


class MQTTClient:
    """Paho MQTT wrapper with automatic reconnection.

    Network status is driven purely by on_connect / on_disconnect callbacks —
    never by individual publish results — to prevent status LED flickering.
    """

    def __init__(self, broker: str, port: int, topic: str,
                 username: str = "SCIL-admin",
                 password: str = "dotdoq-pyCboj-daqne9",
                 role: str = "public"):          # role: "private" | "public"
        self.broker   = broker
        self.port     = port
        self.topic    = topic
        self.role     = role
        self._connected = False

        client_id   = f"mqtt_client_{os.urandom(4).hex()}"
        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set(username, password)
        self.client.on_connect    = self._on_connect
        self.client.on_message    = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # Enable TLS when needed:
        # import ssl
        # self.client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)

    # ── Callbacks — only place that changes network status ──
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            logging.info(f"MQTT [{self.role}] connected to {self.broker}:{self.port}")
            print(f"MQTT [{self.role}] connected to {self.broker}:{self.port}")
            funciton.set_mqtt_status(self.role, True)
            client.subscribe(self.topic)
        else:
            self._connected = False
            logging.warning(f"MQTT [{self.role}] connect failed rc={rc}")
            funciton.set_mqtt_status(self.role, False)

    def _on_message(self, client, userdata, msg):
        funciton.add_msg_to_buffer(msg)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        logging.warning(f"MQTT [{self.role}] disconnected rc={rc}")
        funciton.set_mqtt_status(self.role, False)

    # ── Connection loop (runs in background thread) ──
    def _connect_loop(self):
        while True:
            try:
                self.client.connect(self.broker, self.port, keepalive=60)
                self.client.loop_forever(retry_first_connection=True)
            except Exception as exc:
                self._connected = False
                funciton.set_mqtt_status(self.role, False)
                logging.error(f"MQTT [{self.role}] connection error: {exc}")
                print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] MQTT [{self.role}] error: {exc} — retrying in 10s")
                time.sleep(10)

    def start(self):
        t = threading.Thread(target=self._connect_loop, daemon=True)
        t.start()

    def stop(self):
        self.client.disconnect()

    # ── Publish — NEVER touches status ──────────────────
    def publish(self, topic: str, message: str) -> bool:
        if not self._connected:
            return False
        try:
            result = self.client.publish(topic, message)
            ok = result[0] == 0
            if not ok:
                logging.warning(f"MQTT [{self.role}] publish failed to {topic}")
            return ok
        except Exception as exc:
            logging.error(f"MQTT [{self.role}] publish error: {exc}")
            return False