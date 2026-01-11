import json, time, os, random, copy, base58
from hashlib import sha256
from pathlib import Path

with open(f"{Path(__file__).parent.parent}/config.json", "r") as r:
  config = json.load(r)
with open(f"{Path(__file__).parent.parent}/formats/block.json", "r") as r:
  block = json.load(r)
with open(f"{Path(__file__).parent.parent}/formats/word.json", "r") as r:
  word = json.load(r)
block = copy.deepcopy(block)
word = copy.deepcopy(word)

def difficulty():
  if not os.path.exists(f"{Path(__file__).parent.parent}/data/wordChain.json"):
    diff = round(2**224 * 2**32 / (2**32 / config["blockchain"]["difficulty"]["hashrate"] * config["blockchain"]["difficulty"]["confirmationTime"]))
    return format(diff, f"0{((diff.bit_length() + 3) // 4)}x")
  else:
    with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "r") as r:
      wordChain = json.load(r)
    diff = (int(wordChain[-1]["header"]["difficulty"], 16) * ((wordChain[-1]["header"]["timestamp"] - wordChain[-2]["header"]["timestamp"]) / config["blockchain"]["difficulty"]["confirmationTime"]))
    return format(diff, f"0{((diff.bit_length() + 3) // 4)}x")

def propagate():
  os.makedirs(f"{Path(__file__).parent.parent}/data", exist_ok=True)
  block["header"]["version"] = config["metadata"]["version"]
  block["header"]["prevHash"] = "0"*64
  if os.path.exists(f"{Path(__file__).parent.parent}/data/wordChain.json"):
    with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "r") as r:
      wordChain = json.load(r)
    block["header"]["prevHash"] = wordChain[-1]["header"]["blockHash"]
  block["header"]["merkleRoot"] = "0"*64
  block["header"]["timestamp"] = round(time.time())
  block["header"]["difficulty"] = difficulty()
  block["header"]["nonce"] = 0
  static = (block["header"]["version"].to_bytes((block["header"]["version"].bit_length() + 7) // 8, "big") + bytes.fromhex(block["header"]["prevHash"]) + bytes.fromhex(block["header"]["merkleRoot"]) + block["header"]["timestamp"].to_bytes((block["header"]["timestamp"].bit_length() + 7) // 8, "big") + bytes.fromhex(block["header"]["difficulty"]) + block["header"]["nonce"].to_bytes((block["header"]["nonce"].bit_length() + 7) // 8, "big"))
  block["header"]["blockHash"] = sha256(sha256(static).digest()).hexdigest()

  if block["header"]["prevHash"] == "0"*64:
    temp = []
    temp.append(block)
    with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
      json.dump(temp, w, indent=4)
  else:
    with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "r") as r:
      wordChain = json.load(r)
    wordChain.append(block)
    with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
      json.dump(wordChain, w, indent=4)

def word():
  lang = config["configurations"]["lang"]
  options = config["configurations"]["options"]
  if lang in options:
    with open(f"{Path(__file__).parent.parent}/dictionaries/{lang}.json", "r") as f:
        words = json.load(f)
    word["word"] = random.choice(words)
  word["id"] = base58.b58encode(os.urandom(16)).decode()
  word["lang"] = config["configurations"]["lang"]
  if lang in options:
    with open(f"{Path(__file__).parent.parent}/dictionaries/{lang}.json", "r") as f:
      words = json.load(f)
    word["word"] = random.choice(words)
  word["wID"] = sha256(word["id"].encode("utf-8") + word["word"].encode("utf-8") + word["lang"].encode("utf-8")).hexdigest()

  return json.dumps(word)
