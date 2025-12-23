import psutil

battery = psutil.sensors_battery()
if battery is None:
    print("沒有檢測到電池（可能是台式機或系統沒暴露接口）")
else:
    print(f"電量：{battery.percent}%")
    print("是否在充電：", battery.power_plugged)


import os

def get_battery_capacity():
    base = "/sys/class/power_supply"
    if not os.path.exists(base):
        return None

    # 找到名字裡帶 BAT 的設備，比如 BAT0、BAT1
    for name in os.listdir(base):
        if name.startswith("BAT"):
            cap_path = os.path.join(base, name, "capacity")
            try:
                with open(cap_path, "r") as f:
                    percent = int(f.read().strip())
                return percent
            except Exception:
                pass
    return None

percent = get_battery_capacity()
if percent is None:
    print("沒有找到電池資訊（可能是台式機 / 沒有 BAT* 目錄）")
else:
    print(f"電量：{percent}%")
