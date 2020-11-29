import json
from secrets import token_hex
def generate_device_info():
    return {
        "device_id": "015051B67B8D59D0A86E0F4A78F47367B749357048DD5F23DF275F05016B74605AAB0D7A6127287D9C",
        "device_id_sig": "AaauX/ZA2gM3ozqk1U5j6ek89SMu",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 7.1; LG-UK495 Build/MRA58K; com.narvii.amino.master/3.3.33180)"
    }

class DeviceGenerator:
    def __init__(self):
        try:
            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.user_agent = data["user_agent"]
                self.device_id = data["device_id"]
                self.device_id_sig = data["device_id_sig"]

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            device = generate_device_info()
            with open("device.json", "w") as stream:
                json.dump(device, stream, indent=4)

            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.user_agent = data["user_agent"]
                self.device_id = data["device_id"]
                self.device_id_sig = data["device_id_sig"]
