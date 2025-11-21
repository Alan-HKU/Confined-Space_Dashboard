
import os
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import threading

import funciton

mqtt_client_global = None

import ssl

class MQTTClient:
    def __init__(self, broker, port, topic, username=None, password=None):
        client_id = f"mqtt_client_{os.urandom(4).hex()}"
        self.client = mqtt.Client(client_id=client_id)
        self.broker = broker
        self.port = port
        self.topic = topic
        self.username = "SCIL-admin"
        self.password = "dotdoq-pyCboj-daqne9"
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        if username and password:
            self.client.username_pw_set(username, password)

        # Enable SSL/TLS encryption
        # self.client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            funciton.set_global_status_network(True)
            # 重新订阅之前的主题
            self.client.subscribe(self.topic)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        #可以在这里处理接收到的消息
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        funciton.set_global_status_network(True)
        funciton.add_msg_to_buffer(msg)
        # if (msg.topic == self.topic_gateway):
            # parse_message_mqtt.parse_message(msg)
            
            #print topic
            

    def connect(self):
        while True:
            try:
                self.client.connect(self.broker, self.port, 60)
                self.client.loop_start()
                break
            except Exception as e:
                print(f"MQTT connection error: {e}, attempting to reconnect...")
                funciton.set_global_status_network(False)
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(10)  # 等待5秒后重试

    def publish(self, message, topic=None):
        try:
            print(f"Sent to topic `{topic}`")
            result = self.client.publish(topic, message)
            status = result[0]
            if status == 0:
                print(f"Sent `{message}` to topic `{topic}`")
                funciton.set_global_status_network(True)
                pass
                return True
            else:
                print(f"Failed to send message to topic {topic}")
                funciton.set_global_status_network(False)
        except Exception as e:
            print(f"Error in sending message: {e}")

    def start(self):
        # 在新线程中运行客户端连接
        threading.Thread(target=self.connect).start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


