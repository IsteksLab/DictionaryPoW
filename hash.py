from hashlib import sha256
import json, requests, os

with open("config.json", "r") as r:
  config = json.load(r)

def test():
  try:
    testing = requests.get(config["metadata"]["external"])
    testing.raise_for_status()
    return bool(testing.json())
  except:
    return None

def compute():
  static = (config["metadata"]["version"].to_bytes((config["metadata"]["version"].bit_length() + 7) // 8, "big") + config["metadata"]["developer"].encode("utf-8") + config["metadata"]["github"].encode("utf-8") + config["metadata"]["external"].encode("utf-8") + config["metadata"]["created"].to_bytes((config["metadata"]["created"].bit_length() + 7) // 8, "big"))
  config["metadata"]["verifyHash"] = sha256(static).hexdigest()
  with open("config.json", "w") as w:
    json.dump(config, w, indent=4)

def verify():
  global err
  if not os.path.exists("config.json"):
    if test() == True:
      external = requests.get(config["metadata"]["external"]).json()
      with open("config.json", "w") as w:
        json.dump(external, w, indent=4)
    else:
      err = 404
  else:
    if test() == True:
      external = requests.get(config["metadata"]["external"]).json()
      static = (config["metadata"]["version"].to_bytes((config["metadata"]["version"].bit_length() + 7) // 8, "big") + config["metadata"]["developer"].encode("utf-8") + config["metadata"]["github"].encode("utf-8") + config["metadata"]["external"].encode("utf-8") + config["metadata"]["created"].to_bytes((config["metadata"]["created"].bit_length() + 7) // 8, "big"))
      if sha256(static).hexdigest() != external["metadata"]["verifyHash"]:
        config["tampered"] = True
        with open("config.json", "w") as w:
          json.dump(config, w, indent=4)
        compute()
    else:
      err = 202

    
