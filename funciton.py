from paho.mqtt import client as mqtt_client
import logging
import time
import inspect
import datetime
from main import *
import configparser
import json
from PySide6.QtGui import QScreen
import ctypes
import time
import os
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import serial

#from gpiozero import LED

title = "密閉空間監測系統"
description = "密閉空間監測系統"
client_id = "sam testing2"
unit = ["ppm", "ppm", "%LEL", "%Vol", "C", "%RH","m/s", "exist","exist"]
item = ["硫化氫 (H2S)", "一氧化碳 (CO)", "易燃氣體 (EX)", "氧氣 (O2)", "氣溫", "相對濕度"]
#min_max = [[0, 2], [0, 2], [0, 2], [20, 26], [0, 100], [0, 100], [0, 1],[0, 1],[0, 1]]
configfilename = "config.ini"
Item_display = 12

item_font = "font: 19pt;"
value_font = "font: 60pt;"
device_font = "font: 14pt;"
bottom_font = "font: 16pt;"
unit_font = "font: 18pt;"
red = "background-color: red;"
yellow = "background-color: yellow;"
green = "background-color: green;"
trans = "background: transparent;"
ver = "v1.2b"

#led = LED(17)
#led.on()

lastlog = []
#data = []

status_network  = False
status_485 = False

databuffer = []

def get(data):
    # print( globals()[data])
    return globals()[data]

class config:
    def __init__(self):
        self.configfile = configparser.ConfigParser()
        self.configfile.optionxform = str
        self.configfile.read(configfilename, encoding="utf-8")
        conf = {}
        for x in self.configfile:
            for y in self.configfile[x]:
                #print(y)
                conf = conf | {y: json.loads(self.configfile[x][y])}
                # print(conf)
        #print(conf)
        globals().update(conf)
        # print(globals())

    def get(self, data):
        return self.configfile["DEFAULT"][data]

    def change_data(self, name, value):
        for x in self.configfile:
            for y in self.configfile[x]:
                #print(y)
                if y == name:
                    self.configfile[x][y] = str(value)
                    with open(configfilename, "w", encoding="utf-8") as file:
                        self.configfile.write(file)
                    return True
        return False

def logging_init():
    FORMAT = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT, filename=LogLocation)
    #logging.basicConfig(level=logging.INFO, format=FORMAT)
    logging.info("Start logging")


class mqtt:
    def __init__(self,ip,port,topic):
        try:
            self.ip = ip
            self.port = port
            self.topic = topic
            self.connected = False
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    logging.info(f"Connected to {self.ip}")
                    #print(f"Connected to {self.ip}")
                    self.connected = True
                else:
                    logging.error(f"Failed to connect, return code {rc}")
                    #print("Failed to connect, return code %d\n", rc)
                self.client.subscribe(self.topic)

            def on_message(client, userdata, msg):
                #print(json.loads(msg.payload))
                databuffer.append(json.loads(msg.payload))
                '''msg = json.loads(msg.payload)
                sensor = msg["sensor_type"]
                value = msg["Value"]
                print(f'{sensor} : {value}')
                print(f'{type(sensor)} : {type(value)}')'''

                '''print(msg.topic + " " + str(msg.payload))
                msg = json.loads(msg.payload)
                name = msg["name"]
                value = msg["value"]
                #print(name, value)
                if Config.change_data(name, value):
                    conf = {name: value}
                    globals().update(conf)'''

            # Set Connecting Client ID
            self.client = mqtt_client.Client(os.urandom(4).hex())
            #self.client._conn
            # print(client)
            # client.username_pw_set(username, password)
            self.client.on_connect = on_connect
            self.client.on_message = on_message
            self.connect()
            self.client.loop_start()
            #print(3)
            # client.loop_forever()
        except Exception as exc:
            #print(inspect.stack()[0][3], ":", str(exc))
            logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")

    def connect(self):
        try:
            #print(1)
            self.client.connect(self.ip, self.port)
            #print(2)
            #self.client.loop_start()
            #self.connected = True
        except Exception as exc:
            #print(inspect.stack()[0][3], ":", str(exc))
            logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")

    def publish(self, topic, msg):
        if self.connected == False:
            self.connect()
        else:
            global status_network
            result = self.client.publish(topic, msg)
            # result: [0, 1]
            status = result[0]
            #print(status)
            if status == 0:
                #print(f"Send `{msg}` to topic `{topic}`")
                status_network  = True
                return True
            else:
                #print(f"Failed to send message to topic {topic}")
                logging.error(f"Failed to send message to topic {topic}")
                status_network  = False
                return False


class data:
    def __init__(self,mqtt) -> None:
        self.started = False
        self.binded = None
        #self.value = ["-"]*10
        self.value2 = []
        self.TOtime = [None] * 3
        for x in range(len(self.TOtime)):
            self.TOtime[x]= datetime.datetime.now()
        self.get()
        self.send(mqtt)

    """def start(self, mqtt):
        try:
            topic = "station/sensor_type_collection/" + station_ID
            msg = {"station_id": station_ID, "location_name:": location}
            msg2 = []
            for x in range(len(sensor)):
                msg2 += [
                    {
                        "sensor_type": sensor[x],
                        "max_value": min_max[x][1],
                        "min_value": min_max[x][0],
                        "unit": str(unit[x]),
                    }
                ]
            msg = msg | {"sensor_type_detail": msg2}
            if mqtt.publish(topic, json.dumps(msg, indent=4, separators=(",", ": "))):
                self.started = True
        except Exception as exc:
            print(inspect.stack()[0][3], ":", str(exc))
            logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")"""

    def send(self, mqtt):
        try:
            for y in self.value2:
                #print(y)
                for x in sensor:
                    #print(x)
                    if x in y:
                        topic = "sensor/sensor_data/" + station_ID
                        #print(topic)
                        if self.binded:
                            status = "bind"
                        else:
                            status = "unbind"
                    # print(sensor[x], data[x], MQTT[x])
                        msg = {
                            "status" : status,
                            "station_id": station_ID,
                            "location_name": location,
                            "device_id": y['device_id'],
                            "sensor_type": x,
                            "value": y[x],
                        }
                        #print(msg)
                        if not mqtt.publish(topic, json.dumps(msg, indent=4, separators=(",", ": "))):
                            break
                        time.sleep(0.02)


            """print(self.started)
            if self.started == False:
                self.started == True
                #self.start(mqtt)
            else:
                for y in self.value2:
                    print(y)
                    for x in sensor:
                        #print(x)
                        if x in y:
                            topic = "sensor/sensor_data/" + station_ID
                            #print(topic)
                        # print(sensor[x], data[x], MQTT[x])
                            msg = {
                                "station_id": station_ID,
                                "location_name": location,
                                "device_id": y['device_id'],
                                "sensor_type": x,
                                "value": y[x],
                            }
                            print(msg)
                            if not mqtt.publish(topic, json.dumps(msg, indent=4, separators=(",", ": "))):
                                break
                            time.sleep(0.02)"""
        except Exception as exc:
            print(inspect.stack()[0][3], ":", str(exc))
            logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")

    def bind(self,mqtt):
        bind_button = GPIO.get_gpio_value('GPIO-H18')
        #if self.binded != True:
        if bind_button == True and self.binded != True:
            logging.info('Binded')
            self.binded = True
            try:
                topic = "station/sensor_type_collection/" + station_ID
                msg = {"station_id": station_ID, "location_name": location}
                msg2 = []
                for x in range(len(sensor)):
                    msg2 += [
                        {
                            "sensor_type": sensor[x],
                            "max_value_lv1": min_max_lv1[x][1],
                            "max_value_lv2": min_max_lv2[x][1],
                            "min_value_lv1": min_max_lv1[x][0],
                            "min_value_lv2": min_max_lv2[x][0],
                            "unit": str(unit[x]),
                        }
                    ]
                msg = msg | {"sensor_type_detail": msg2}
                msg = {"event": "bind", "content": msg}
                if mqtt.publish(topic, json.dumps(msg, indent=4, separators=(",", ": "))):
                    logging.info('Binded sent')
                    #self.binded = True
            except Exception as exc:
                print(inspect.stack()[0][3], ":", str(exc))
                logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")

        #if bind_button == 0 and self.binded != False:
        if bind_button == False and self.binded != False:
            try:
                logging.info('Unbinded')
                self.binded = False
                topic = "station/sensor_type_collection/" + station_ID
                msg = {"station_id": station_ID, "location_name": location}

                msg2 = []
                for x in range(len(sensor)):
                    msg2 += [
                        {
                            "sensor_type": sensor[x],
                            "max_value_lv1": min_max_lv1[x][1],
                            "max_value_lv2": min_max_lv2[x][1],
                            "min_value_lv1": min_max_lv1[x][0],
                            "min_value_lv2": min_max_lv2[x][0],
                            "unit": str(unit[x]),
                        }
                    ]
                msg = msg | {"sensor_type_detail": msg2}
                msg = {"event": "unbind", "content": msg}
                #print(msg)
                if mqtt.publish(topic, json.dumps(msg, indent=4, separators=(",", ": "))):
                    logging.info('Unbinded sent')
                    #self.binded = False
            except Exception as exc:
                print(inspect.stack()[0][3], ":", str(exc))
                logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")

    def get(self):
        """while databuffer:
            print(databuffer.pop(0))"""
        #print(self.value2)
        time_now = datetime.datetime.now()
        #print(databuffer)
        while databuffer:
            msg = databuffer.pop(0)
            #print(msg)
            #print(msg["device_ID"])
            i = next((i for i, item in enumerate(self.value2) if item["device_id"] == msg["device_id"]), None)
            msg.update({"time": time_now})
            #print(i)
            if i is not None:
                self.value2[i].update(msg)
            else:
                self.value2.append(msg)
                self.value2 = sorted(self.value2, key=lambda d: d['device_id'])
            #print(self.value2)
        #print(self.value2)

    def log(self):
        try:
            global lastlog
            log = f"Log data:{self.value2}"
            if log != lastlog:
                logging.info(log)
                lastlog = log
        except Exception as exc:
            # print(inspect.stack()[0][3], ":", str(exc))
            logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")

    def check(self):
        try:
            time_now = datetime.datetime.now()
            for x in self.value2:
                #print(time_now.timestamp() - x["time"].timestamp())
                if (time_now.timestamp() - x["time"].timestamp()) > ConnectionTimeOut:
                    for y in x:
                        if y != "time" and y != "device_id":
                            x[y] = "-"
                
        except Exception as exc:
            # print(inspect.stack()[0][3], ":", str(exc))
            logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")


def set_status(window,icon,status):
    if status == True:
        exec("window.ui."+icon+".setStyleSheet('background-image: url(:/images/images/images/green-dot.png);''background-position:center;''background-repeat:no-repeat;')")
    else:
        exec("window.ui."+icon+".setStyleSheet('background-image: url(:/images/images/images/red-dot.png);''background-position:center;''background-repeat:no-repeat;')")

class GUI:
    def __init__(self) -> None:
        self.time_update = None
        self.display_page = 1
        self.display_list = None
        self.display_device = None

    def switch_display_device(self,data):
        if data.value2:
            temp_list = []
            for x in range(len(data.value2)):
                for y in range(len(sensor)):
                    if sensor[y] in data.value2[x]:
                        if sensor[y] != "cam":
                            temp_list.append([x,y])
            self.display_list = temp_list[(self.display_page-1)*Item_display:self.display_page*Item_display]
            #print(len(temp_list))
            if self.display_page*Item_display >= len(temp_list):
                self.display_page = 1
            else:
                self.display_page += 1
        #print(self.display_list)

    def update(self,window,data):
        data.check()
        for x in range(Item_display):
            exec("window.ui.value_" + str(x) + ".setText(str(""))")
            exec("window.ui.value_" + str(x) + ".setStyleSheet(trans + value_font)")

        """if self.display_device is not None:
            for x in range(10):"""

        # print(data)
        # window.ui.label.setText(str(datetime.datetime.now().time()))
        """if not data:
        mod_init()
        data = [0, 0, 0, 0, 0, 0]"""
        # send_sensor_data(mqtt,data)
        if self.display_list is not None:
            for x in range(Item_display):
                exec("window.ui.value_" + str(x) + ".setStyleSheet(trans + value_font)")
                exec("window.ui.value_" + str(x) + ".setText(str(""))")
                exec("window.ui.unit_" + str(x) + ".setText(str(""))")
                exec("window.ui.name_" + str(x) + ".setText(str(""))")
                exec("window.ui.device_" + str(x) + ".setText(str(""))")
        #for x in device:
            for x in range(len(self.display_list)):
                display_device = self.display_list[x][0]
                display_sensor = self.display_list[x][1]
                #print(min_max[display_sensor][0] , data.value2[display_device][sensor[display_sensor]], min_max[display_sensor][1])
                if sensor[display_sensor] == "water_level":
                    #print("yes")
                    if data.value2[display_device][sensor[display_sensor]] > min_max_lv2[display_sensor][1]:
                        exec("window.ui.value_" + str(x) + ".setText('過高')")
                    if min_max_lv2[display_sensor][0] <= data.value2[display_device][sensor[display_sensor]] <= min_max_lv2[display_sensor][1]:
                        exec("window.ui.value_" + str(x) + ".setText('正常')")
                else:
                    exec("window.ui.value_" + str(x) + ".setText(str(data.value2["+ str(display_device) +"][sensor["+ str(display_sensor) +"]]))")
                exec("window.ui.unit_" + str(x) + ".setText(unit[" + str(display_sensor) + "])")
                exec("window.ui.name_" + str(x) + ".setText(display_name[" + str(display_sensor) + "])")
                exec("window.ui.device_" + str(x) + ".setText(str(data.value2["+ str(display_device) +"]['device_id'])+'號機')")
                try:
                    #print(min_max[display_sensor][0] , data.value2[display_device][sensor[display_sensor]], min_max[display_sensor][1])
                    if min_max_lv1[display_sensor][0] <= data.value2[display_device][sensor[display_sensor]] <= min_max_lv1[display_sensor][1]:
                        exec("window.ui.value_" + str(x) + ".setStyleSheet(green + value_font)")
                    elif min_max_lv2[display_sensor][0] <= data.value2[display_device][sensor[display_sensor]] <= min_max_lv2[display_sensor][1]:
                        exec("window.ui.value_" + str(x) + ".setStyleSheet(yellow + value_font)")
                    else:
                        exec("window.ui.value_" + str(x) + ".setStyleSheet(red + value_font)")
                except:
                    exec("window.ui.value_" + str(x) + ".setStyleSheet(red + value_font)")

            """for x in range(len(sensor)):
                #print(sensor[x])
                if sensor[x] in data.value2[self.display_device]:
                    #print(data.value2[self.display_device][sensor[x]])
                    exec("window.ui.value_" + str(x) + ".setText(str(data.value2["+ str(self.display_device) +"][sensor["+ str(x) +"]]))")
                    try:
                        if min_max[x][0] <= data.value2[self.display_device][sensor[x]] <= min_max[x][1]:
                            exec("window.ui.value_" + str(x) + ".setStyleSheet(green + value_font)")
                        else:
                            exec("window.ui.value_" + str(x) + ".setStyleSheet(red + value_font)")
                    except:
                        exec("window.ui.value_" + str(x) + ".setStyleSheet(red + value_font)")
                else:
                    exec("window.ui.value_" + str(x) + ".setStyleSheet(trans + value_font)")"""
            """for x in range(len(sensor)):
                exec("window.ui.value_" + str(x) + ".setText(str(data.value[" + str(x) + "]))")"""
        
        time = datetime.datetime.now()
        window.ui.creditsLabel.setText(str(time.strftime("%d/%m/%y %H:%M:%S")))
        """if data.value2:
            for x in range(len(sensor)):
                if sensor[x] in data.value2[self.display_device]:
                    try:
                        if min_max[x][0] <= data.value2[self.display_device][sensor[x]] <= min_max[x][1]:
                            exec("window.ui.value_" + str(x) + ".setStyleSheet(green + value_font)")
                        else:
                            exec("window.ui.value_" + str(x) + ".setStyleSheet(red + value_font)")
                    except:
                        exec("window.ui.value_" + str(x) + ".setStyleSheet(red + value_font)")
                else:
                    exec("window.ui.value_" + str(x) + ".setStyleSheet(black + value_font)")"""
        set_status(window,'icon',status_network)
        set_status(window,'icon_2',data.binded)
        update_alarm(data)


class status_led:
    def __init__(self) -> None:
        self.status = None
        self.com = None
        self.found = False
        self.find_port()

    def find_port(self):
        try:
            if hasattr(self,"master"):
                self.master.close()
            ports = ['COM%s' % (i + 1) for i in range(256)]
            result = []
            for port in ports:
                try:
                    s = serial.Serial(port)
                    s.close()
                    result.append(port)
                except (OSError, serial.SerialException):
                    pass
            
            print("result",result)
            logging.info(f"result {result}")

            for port in result:
                try:
                    self.master = modbus_rtu.RtuMaster(
                        serial.Serial(
                            port,
                            baudrate=9600,
                            bytesize=8,
                            parity="E",
                            stopbits=1,
                            xonxoff=0,
                        )
                    )
                    self.master.set_timeout(0.05, 0)
                    self.master.set_verbose(True)
                    if self.check():
                        self.com = port
                        print(port)
                        self.found = True
                        break
                    self.master.close()
                    
                except Exception:
                    pass
            #print(self.com)
        except Exception as exc:
            print(inspect.stack()[0][3], ":", str(exc))
            #logging.error(f"{inspect.stack()[0][3]}: {str(exc)}")

    def check(self):
        result = self.master.execute(1, cst.WRITE_SINGLE_COIL, 0, output_value=0)
        #print(result)
        if result == (0,0):
            return True
        return False
    
    def off(self):
        if self.found:
            try:
                self.master.execute(1, cst.WRITE_SINGLE_COIL, 0, output_value=0)
                self.status = 0
            except Exception:
                self.found = False
        else:
            self.find_port()


    def alarm(self):
        if self.found:
            try:
                if self.status != 1:
                    self.off()
                    self.status = 1
                    self.master.execute(1, cst.WRITE_SINGLE_COIL, 10, output_value=65280)
                    #print(1)
                #self.master.execute(1, cst.WRITE_SINGLE_COIL, 10, output_value=65280)
                #print(2)
            except Exception:
                self.found = False
                #print(3)
        else:
            self.find_port()
            #print(4)

    def alert(self):
        if self.found:
            try:
                if self.status != 1:
                    self.off()
                    self.status = 1
                    #print(1)
                    self.master.execute(1, cst.WRITE_SINGLE_COIL, 7, output_value=65280)
                #print(2)
            except Exception:
                self.found = False
                #print(3)
        else:
            self.find_port()
            #print(4)

    def normal(self):
        if self.found:
            try:
                if self.status != 2:
                    self.off()
                    self.status = 2
                    self.master.execute(1, cst.WRITE_SINGLE_COIL, 3, output_value=65280)
            except Exception:
                self.found = False
        else:
            self.find_port()

    def standby(self):
        if self.found:
            try:
                if self.status != 3:
                    self.off()
                    #self.master.execute(1, cst.WRITE_SINGLE_COIL, 2, output_value=65280)
                    self.status = 3
                    self.master.execute(1, cst.WRITE_SINGLE_COIL, 2, output_value=65280)
            except Exception:
                self.found = False
        else:
            self.find_port()

def update_alarm(data):
    TOtime = None
    temp_alert = False
    temp_alarm = False
    nowtime = datetime.datetime.now()
    for x in data.value2:
        for y in range(len(sensor)):
            if sensor[y] in x:
                try:
                    if min_max_lv1[y][0] > x[sensor[y]] or x[sensor[y]] > min_max_lv1[y][1]:
                        temp_alert = True
                    if min_max_lv2[y][0] > x[sensor[y]] or x[sensor[y]] > min_max_lv2[y][1]:
                        temp_alarm = True
                except Exception as exc:
                    pass
            #print(inspect.stack()[0][3], ":", str(exc))
    if data.binded:
        if temp_alarm:
            TOtime = datetime.datetime.now()
            #GPIO.on('GPIO-H19')
            '''GPIO.set_output("GPIO-H19")
            GPIO.set_gpio_value("GPIO-H19", 0)'''
            Status_led.alarm()
            """if data.binded:
                Status_led.alarm()"""
            #print(1)
        elif temp_alert:
            TOtime  = datetime.datetime.now()
            Status_led.alert()
            #print(2)
        elif TOtime  == None or (nowtime.timestamp() - TOtime.timestamp()) > AlarmTimeOut:
            Status_led.normal()
            #print(3)
        """elif(nowtime.timestamp() - TOtime4.timestamp()) > TimeOut:
            #GPIO.off('GPIO-H19')
            '''GPIO.set_gpio_value("GPIO-H19", 1)
            GPIO.set_input("GPIO-H19")'''
            Alarm.normal()"""
    else:
        Status_led.standby()
        print(4)
        
    """for x in data.value2:
        for y in range(len(sensor)):
            if sensor[y] in x:
                try:
                    if min_max_lv2[y][0] > x[sensor[y]] or x[sensor[y]] > min_max_lv2[y][1]:
                        alarm = True
                except Exception as exc:
                    pass
            #print(inspect.stack()[0][3], ":", str(exc))
        
        for y in range(len(sensor)):
            if sensor[y] in x:
                try:
                    if min_max_lv1[y][0] > x[sensor[y]] or x[sensor[y]] > min_max_lv1[y][1]:
                        alert = True
                except Exception as exc:
                    pass
    if alarm:
        TOtime4 = datetime.datetime.now()
        GPIO.on('GPIO-H19')
        '''GPIO.set_output("GPIO-H19")
        GPIO.set_gpio_value("GPIO-H19", 0)'''
        #led.on()
    elif (nowtime.timestamp() - TOtime4.timestamp()) > TimeOut:
        GPIO.off('GPIO-H19')
        '''GPIO.set_gpio_value("GPIO-H19", 1)
        GPIO.set_input("GPIO-H19")'''
        #led.off()"""
    
class gpio:
    def __init__(self) -> None:
        # 加载 inpoutx64.dll
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.dll_path = os.path.join(self.current_dir, 'inpoutx64.dll')
        self.inpoutx64 = ctypes.WinDLL(self.dll_path)

        # 定义函数原型
        self.inpoutx64.SetPhysLong.argtypes = [ctypes.c_ulonglong, ctypes.c_uint]
        self.inpoutx64.SetPhysLong.restype = ctypes.c_bool
        self.inpoutx64.GetPhysLong.argtypes = [ctypes.c_ulonglong, ctypes.POINTER(ctypes.c_uint)]
        self.inpoutx64.GetPhysLong.restype = ctypes.c_bool

        self.GPIO_ADDRESSES = {
            'GPIO-H19': 0xFD6D0730,
            'GPIO-H18': 0xFD6D0720,
            'GPIO-H17': 0xFD6D0710,
            'GPIO-H16': 0xFD6D0700,
            'GPIO-H00': 0xFD6D0600,
        }

        # 输出和输入模式的值
        self.OUTPUT_MODE = 0x00800201
        self.INPUT_MODE = 0x84000100

    # 定义设置GPIO电平的函数
    def set_gpio_value(self,phys_addr, phys_val):
        success = self.inpoutx64.SetPhysLong(self.GPIO_ADDRESSES[phys_addr], phys_val)
        return success

    # 定义读取GPIO电平的函数
    def get_gpio_value(self,phys_addr):
        phys_val = ctypes.c_uint()
        success = self.inpoutx64.GetPhysLong(self.GPIO_ADDRESSES[phys_addr], ctypes.byref(phys_val))
        if success:
            if phys_val.value == 0x84000102:
                return False
            if phys_val.value == 0x84000100:
                return True
        else:
            return None
        
    def set_input(self,phys_addr):
        success = self.inpoutx64.SetPhysLong(self.GPIO_ADDRESSES[phys_addr], self.INPUT_MODE)
        if not success:
            logging.error(f"Failed to set {phys_addr} as input")
    
    def set_output(self,phys_addr):
        success = self.inpoutx64.SetPhysLong(self.GPIO_ADDRESSES[phys_addr], self.OUTPUT_MODE)
        if not success:
            logging.error(f"Failed to set {phys_addr} as output")

    # 设置GPIO为输入模式并读取电平状态的函数
    '''def set_input_and_read(self,phys_addr):
        if self.set_gpio_value(phys_addr, self.INPUT_MODE):
            print("GPIO set to input mode.")
            time.sleep(0.1)  # 等待硬件反应时间
            value = self.get_gpio_value(phys_addr)
            if value == 0x84000102:
                print("GPIO input is HIGH.")
            elif value == 0x84000100:
                print("GPIO input is LOW.")
            else:
                print(f"Unexpected GPIO input value: {hex(value)}")
        else:
            print("Failed to set GPIO to input mode.")'''

    def on(self,phys_addr):
        self.set_output(phys_addr)
        self.set_gpio_value(phys_addr, 0)

    def off(self,phys_addr):
        self.set_gpio_value(phys_addr, 1)
        self.set_input(phys_addr)

    def read(self,phys_addr):
        self.set_gpio_value(phys_addr, 1)
        self.set_input(phys_addr)

def window_init(window):
    # set full screen
    #monitor = QDesktopWidget().screenGeometry(2)
    #window.move(monitor.left(), monitor.top())
    monitors = QScreen.virtualSiblings(window.screen())
    monitor = monitors[ScreenDisplayed].availableGeometry()
    window.move(monitor.left(), monitor.top())
    window.showFullScreen()
    window.ui.appMargins.setContentsMargins(0, 0, 0, 0)
    # display time
    time = datetime.datetime.now()
    window.ui.titleRightInfo.setText(f"{description} - {location} ({station_ID})")
    window.ui.titleRightInfo.setStyleSheet("font: 25pt")
    window.ui.creditsLabel.setText(str(time.strftime("%H:%M:%S %D")))
    window.ui.status.setText("網絡")
    window.ui.status_2.setText("運行中")
    # display version
    window.ui.version.setText(ver)
    # set frot

    window.ui.creditsLabel.setStyleSheet(bottom_font)
    window.ui.version.setStyleSheet(bottom_font)
    #window.ui.memory.setStyleSheet(bottom_font)
    window.ui.status.setStyleSheet(bottom_font)
    window.ui.status_2.setStyleSheet(bottom_font)

    for x in range(Item_display):
        exec("window.ui.name_" + str(x) + '.setText("")')
        exec("window.ui.unit_" + str(x) + '.setText("")')
        exec("window.ui.value_" + str(x) + '.setText("")')
        exec("window.ui.device_" + str(x) + '.setText("")')
        exec("window.ui.name_" + str(x) + ".setStyleSheet(item_font)")
        exec("window.ui.unit_" + str(x) + ".setStyleSheet(unit_font)")
        exec("window.ui.value_" + str(x) + ".setStyleSheet(value_font)")
        exec("window.ui.device_" + str(x) + ".setStyleSheet(device_font)")

    for x in range(12):
        exec("window.ui.name_" + str(x) + ".setText(display_name[" + str(x) + "])")
        exec("window.ui.value_" + str(x) + ".setText('-')")
        exec("window.ui.unit_" + str(x) + ".setText(unit[" + str(x) + "])")

    #update_GUI(window)

def time_init():
    pass
    """global TOtime4
    TOtime4 = datetime.datetime.now()"""

def all_init():
    global Config
    Config = config()
    #print(dir())
    logging_init()
    time_init()
    global GPIO
    GPIO = gpio()
    GPIO.off('GPIO-H19')
    '''GPIO.set_output('GPIO-H19')
    GPIO.set_gpio_value('GPIO-H19', 1)'''
    GPIO.set_input('GPIO-H18')
    '''if GPIO.set_gpio_value('GPIO-H19', GPIO.OUTPUT_MODE):
        print("GPIO-H19 set to output mode.")
    else:
        print("Failed to set GPIO-H19 to output mode.")
    GPIO.set_gpio_value('GPIO-H19', 1)'''
    global Status_led
    Status_led = status_led()