import json, os, threading, base58
from hashlib import sha256
from pathlib import Path
from pow import block

with open(f"{Path(__file__).parent.parent}/config.json", "r") as r:
  config = json.load(r)
with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "r") as r:
  wordChain = json.load(r)

def mine():
  block.propagate()
  wordChain[-1]["body"] = [block.word() for _ in range(config["blockchain"]["maxWords"])]
  merkleRoot = wordChain[-1]["body"]
  while len(merkleRoot) > 1:
    if len(merkleRoot) % 2 == 1:
        merkleRoot.append(merkleRoot[-1]["wID"])
    merkles = []
    for p in range(0, len(merkleRoot), 2):
        merkles.append(sha256(merkleRoot[p] + merkleRoot[p+1]).digest())
    merkleRoot = merkles
  merkleRoot = merkleRoot[0]

  static = (bytes.fromhex(wordChain[-1]["header"]["version"]) + bytes.fromhex(wordChain[-1]["header"]["prevHash"]) + merkleRoot + wordChain[-1]["header"]["timestamp"].to_bytes((wordChain[-1]["header"]["timestamp"].bit_length() + 7) // 8, "big") + bytes.fromhex(wordChain[-1]["header"]["difficulty"]) + bytes.fromhex(wordChain[-1]["header"]["nonce"]))
  blockHash = sha256(sha256(static).digest()).hexdigest()
  while int(wordChain[-1]["header"]["nonce"], 16) <= (2**32) - 1:
    if int(blockHash, 16) <= int(wordChain[-1]["header"]["difficulty"], 16):
      wordChain[-1]["header"]["blockHash"] = blockhash
      wordChain[-1]["header"]["merkleRoot"] = merkleRoot.hex()
      with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
        json.dump(wordChain, w, indent=4)
      break
    else:
      nonce += 1
      nonce = hex(nonce)
      static = (bytes.fromhex(wordChain[-1]["header"]["version"]) + bytes.fromhex(wordChain[-1]["header"]["prevHash"]) + merkleRoot + wordChain[-1]["header"]["timestamp"].to_bytes((wordChain[-1]["header"]["timestamp"].bit_length() + 7) // 8, "big") + bytes.fromhex(wordChain[-1]["header"]["difficulty"]) + bytes.fromhex(nonce))
      if sha256(sha256(static).digest()).hexdigest() <= int(wordChain[-1]["header"]["difficulty"], 16):
        wordChain[-1]["header"]["blockHash"] = sha256(sha256(static).digest()).hexdigest()
        wordChain[-1]["header"]["merkleRoot"] = merkleRoot.hex()
        wordChain[-1]["header"]["nonce"] = nonce
        with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
          json.dump(wordChain, w, indent=4)
        break
      if int(nonce, 16) > (2**32) - 1:
        wordChain[-1]["body"][-1]["id"] = base58.b58encode(os.urandom(16)).decode()
        wordChain[-1]["body"][-1]["wID"] = sha256(wordChain[-1]["body"][-1]["id"].encode("utf-8") + wordChain[-1]["body"][-1]["word"].encode("utf-8") + wordChain[-1]["body"][-1]["lang"].encode("utf-8")).hexdigest()
        merkleRoot = wordChain[-1]["body"]
        while len(merkleRoot) > 1:
          if len(merkleRoot) % 2 == 1:
            merkleRoot.append(merkleRoot[-1]["wID"])
          merkles = []
          for p in range(0, len(merkleRoot), 2):
            merkles.append(sha256(merkleRoot[p] + merkleRoot[p+1]).digest())
          merkleRoot = merkles
        merkleRoot = merkleRoot[0]
        static = (bytes.fromhex(wordChain[-1]["header"]["version"]) + bytes.fromhex(wordChain[-1]["header"]["prevHash"]) + merkleRoot + wordChain[-1]["header"]["timestamp"].to_bytes((wordChain[-1]["header"]["timestamp"].bit_length() + 7) // 8, "big") + bytes.fromhex(wordChain[-1]["header"]["difficulty"]) + bytes.fromhex(nonce))
        if int(sha256(sha256(static).digest()).hexdigest(), 16) <= int(wordChain[-1]["header"]["difficulty"], 16):
          wordChain[-1]["header"]["blockHash"] = sha256(sha256(static).digest()).hexdigest()
          wordChain[-1]["header"]["merkleRoot"] = merkleRoot.hex()
          with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
            json.dump(wordChain, w, indent=4)
          break
  validate()

def validate():
  global status
  status = None
  version = prevHash = merkleRoot = timestamp = difficulty = nonce = blockHash = mined = False
  if wordChain[-1]["header"]["version"] == hex(config["metadata"]["version"]):
    version = True
  if wordChain[-1]["header"]["prevHash"] == wordChain[-2]["header"]["blockHash"]:
    prevHash = True

  merkleRoot = wordChain[-1]["body"]
  while len(merkleRoot) > 1:
    if len(merkleRoot) % 2 == 1:
        merkleRoot.append(merkleRoot[-1]["wID"])
    merkles = []
    for p in range(0, len(merkleRoot), 2):
        merkles.append(sha256(merkleRoot[p] + merkleRoot[p+1]).digest())
    merkleRoot = merkles
  if wordChain[-1]["header"]["merkleRoot"] == merkleRoot[0]:
    merkleRoot = True
  if isinstance(wordChain[-1]["header"]["timestamp"], int) and len(wordChain[-1]["header"]["timestamp"]) >= 10:
    timestamp = True
  if isinstance(wordChain[-1]["header"]["difficulty"], hex):
    difficulty = True
  if isinstance(wordChain[-1]["header"]["nonce"], hex):
    nonce = True
  if int(wordChain[-1]["header"]["blockHash"], 16) <= int(wordChain[-1]["header"]["difficulty"], 16):
    mined = True

  if version and prevHash and merkleRoot and timestamp and difficulty and nonce and mined:
    status = 1
  else:
    wordChain[-1].pop()
    with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
      json.dump(wordChain, w, indent=4)
    status = 0

def start():
  cpuUsage = 0
  if config["blockchain"]["cpuUsage"] > 5:
    cpuUsage = 3
  else:
    cpuUsage = config["blockchain"]["cpuUsage"]
  usage = max(1, int(os.cpu_count() * (cpuUsage / 5)))

  threads = []
  for _ in range(usage):
    cpu = threading.Thread(target=pow)
    cpu.daemon = True
    cpu.start()
    threads.append(cpu)
  for thread in threads:
    thread.join()
