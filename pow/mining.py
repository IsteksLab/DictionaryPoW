from hashlib import sha256
from pathlib import Path
import json, os, base58
from pow import block

status = None
block.propagate()

with open(f"{Path(__file__).parent.parent}/config.json", "r") as r:
  config = json.load(r)
with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "r") as r:
  wordChain = json.load(r)

def mine():
  nonce = 0
  wordChain[-1]["body"] = [block.word() for _ in range(config["blockchain"]["maxWords"])]
  merkleRoot = [bytes.fromhex(w["wID"]) for w in wordChain[-1]["body"]]
  while len(merkleRoot) > 1:
    if len(merkleRoot) % 2 == 1:
        merkleRoot.append(merkleRoot[-1])
    merkles = []
    for p in range(0, len(merkleRoot), 2):
        merkles.append(sha256(merkleRoot[p] + merkleRoot[p+1]).digest())
    merkleRoot = merkles
  merkleRoot = merkleRoot[0]

  while nonce <= (2**32) - 1:
    static = (wordChain[-1]["header"]["version"].to_bytes((wordChain[-1]["header"]["version"].bit_length() + 7) // 8, "big") + bytes.fromhex(wordChain[-1]["header"]["prevHash"]) + merkleRoot + wordChain[-1]["header"]["timestamp"].to_bytes((wordChain[-1]["header"]["timestamp"].bit_length() + 7) // 8, "big") + wordChain[-1]["header"]["difficulty"].to_bytes((wordChain[-1]["header"]["difficulty"].bit_length() + 7) // 8, "big") + wordChain[-1]["header"]["nonce"].to_bytes((wordChain[-1]["header"]["nonce"].bit_length() + 7) // 8, "big"))
    blockHash = sha256(sha256(static).digest()).hexdigest()
    if int(blockHash, 16) <= wordChain[-1]["header"]["difficulty"]:
      wordChain[-1]["header"]["blockHash"] = blockHash
      wordChain[-1]["header"]["merkleRoot"] = merkleRoot.hex()
      with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
        json.dump(wordChain, w, indent=4)
      break
    else:
      nonce += 1
      static = (wordChain[-1]["header"]["version"].to_bytes((wordChain[-1]["header"]["version"].bit_length() + 7) // 8, "big") + bytes.fromhex(wordChain[-1]["header"]["prevHash"]) + merkleRoot + wordChain[-1]["header"]["timestamp"].to_bytes((wordChain[-1]["header"]["timestamp"].bit_length() + 7) // 8, "big") + wordChain[-1]["header"]["difficulty"].to_bytes((wordChain[-1]["header"]["difficulty"].bit_length() + 7) // 8, "big") + nonce.to_bytes((nonce.bit_length() + 7) // 8, "big"))
      blockHash = sha256(sha256(static).digest()).hexdigest()
      if int(blockHash, 16) <= wordChain[-1]["header"]["difficulty"]:
        wordChain[-1]["header"]["blockHash"] = blockHash
        wordChain[-1]["header"]["merkleRoot"] = merkleRoot.hex()
        wordChain[-1]["header"]["nonce"] = nonce
        with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
          json.dump(wordChain, w, indent=4)
        break
      if nonce > (2**32) - 1:
        wordChain[-1]["body"][-1]["id"] = base58.b58encode(os.urandom(16)).decode()
        wordChain[-1]["body"][-1]["wID"] = sha256(wordChain[-1]["body"][-1]["id"].encode("utf-8") + wordChain[-1]["body"][-1]["word"].encode("utf-8") + wordChain[-1]["body"][-1]["lang"].encode("utf-8")).hexdigest()
        merkleRoot = [bytes.fromhex(w["wID"]) for w in wordChain[-1]["body"]]
        while len(merkleRoot) > 1:
          if len(merkleRoot) % 2 == 1:
            merkleRoot.append(merkleRoot[-1])
          merkles = []
          for p in range(0, len(merkleRoot), 2):
            merkles.append(sha256(merkleRoot[p] + merkleRoot[p+1]).digest())
          merkleRoot = merkles
        merkleRoot = merkleRoot[0]
        static = (wordChain[-1]["header"]["version"].to_bytes((wordChain[-1]["header"]["version"].bit_length() + 7) // 8, "big") + bytes.fromhex(wordChain[-1]["header"]["prevHash"]) + merkleRoot + wordChain[-1]["header"]["timestamp"].to_bytes((wordChain[-1]["header"]["timestamp"].bit_length() + 7) // 8, "big") + wordChain[-1]["header"]["difficulty"].to_bytes((wordChain[-1]["header"]["difficulty"].bit_length() + 7) // 8, "big") + nonce.to_bytes((nonce.bit_length() + 7) // 8, "big"))
        if int(sha256(sha256(static).digest()).hexdigest(), 16) <= wordChain[-1]["header"]["difficulty"]:
          wordChain[-1]["header"]["blockHash"] = sha256(sha256(static).digest()).hexdigest()
          wordChain[-1]["header"]["merkleRoot"] = merkleRoot.hex()
          with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
            json.dump(wordChain, w, indent=4)
          break
  validate()

def validate():
  global status
  version = prevHash = merkleRoot = timestamp = difficulty = nonce = blockHash = mined = False
  if wordChain[-1]["header"]["version"] == config["metadata"]["version"]:
    version = True
  if wordChain[-1]["header"]["prevHash"] == wordChain[-2]["header"]["blockHash"]:
    prevHash = True

  merkleRoot = [bytes.fromhex(w["wID"]) for w in wordChain[-1]["body"]]
  while len(merkleRoot) > 1:
    if len(merkleRoot) % 2 == 1:
        merkleRoot.append(merkleRoot[-1])
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
  if wordChain[-1]["header"]["nonce"] <= (2**32) - 1:
    nonce = True
  if int(wordChain[-1]["header"]["blockHash"], 16) <= wordChain[-1]["header"]["difficulty"]:
    mined = True

  if version and prevHash and merkleRoot and timestamp and difficulty and nonce and mined:
    status = 1
  else:
    wordChain[-1].pop()
    with open(f"{Path(__file__).parent.parent}/data/wordChain.json", "w") as w:
      json.dump(wordChain, w, indent=4)
    status = 0
