from termcolor import colored
import time, os, json, hash
from pow import mining

with open("config.json", "r") as r:
  config = json.load(r)

def clear():
  os.system('cls' if os.name == 'nt' else 'clear')

def setup():
  clear()
  print(colored("""
██████╗░██╗░█████╗░████████╗██╗░█████╗░███╗░░██╗░█████╗░██████╗░██╗░░░██╗██████╗░░█████╗░░██╗░░░░░░░██╗
██╔══██╗██║██╔══██╗╚══██╔══╝██║██╔══██╗████╗░██║██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗██╔══██╗░██║░░██╗░░██║
██║░░██║██║██║░░╚═╝░░░██║░░░██║██║░░██║██╔██╗██║███████║██████╔╝░╚████╔╝░██████╔╝██║░░██║░╚██╗████╗██╔╝
██║░░██║██║██║░░██╗░░░██║░░░██║██║░░██║██║╚████║██╔══██║██╔══██╗░░╚██╔╝░░██╔═══╝░██║░░██║░░████╔═████║░
██████╔╝██║╚█████╔╝░░░██║░░░██║╚█████╔╝██║░╚███║██║░░██║██║░░██║░░░██║░░░██║░░░░░╚█████╔╝░░╚██╔╝░╚██╔╝░
╚═════╝░╚═╝░╚════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░╚════╝░░░░╚═╝░░░╚═╝░░\n\n""", "red", attrs=["bold"]))
  hash.verify()
  if config["tampered"]:
    print(colored("Variant: Tampered", "red", attrs=["bold"]))
  elif config["tampered"] == False:
    print(colored("Variant: Intact", "green", attrs=["bold"]))
  elif hash.err == 404:
    print(colored("Variant: unknown", "yellow", attrs=["bold"]))
  print("\n---\n")
  print(colored("""
█▀▀ █▀█ █▄░█ █▀▀ █ █▀▀ █░█ █▀█ █▀▀
█▄▄ █▄█ █░▀█ █▀░ █ █▄█ █▄█ █▀▄ ██▄\n\n""", "white", attrs=["bold"]))
  print(colored("Dictionary:\n", "white", attrs=["bold"]))
  lang = input(colored("Select A Language (de, en, es, fr, it, pt-br, ro, zh): ", "white", attrs=["bold"]))
  if lang.lower() in config["configurations"]["options"]:
    config["configurations"]["lang"] = lang.lower()
  print("\n---\n")
  print(colored("Blockchain:\n", "white", attrs=["bold"]))
  maxWords = input(colored("Set Maximum Words per Block (d for Default): ", "white", attrs=["bold"]))
  if maxWords.lower() == "d":
    pass
  elif isinstace(int(maxWords), int):
    config["blockchain"]["maxWords"] = int(maxWords)
  hashrate = input(colored("Set Genesis Difficulty Hashrate (d for Default): ", "white", attrs=["bold"]))
  if hashrate.lower() == "d":
    pass
  elif isinstance(int(hashrate), int):
    config["blockchain"]["difficulty"]["hashrate"] = int(hashrate)
  confirmationTime = input(colored("Set Block Confirmation Time in Seconds (d for Default): ", "white", attrs=["bold"]))
  if confirmationTime.lower() == "d":
    pass
  elif isinstance(int(confirmationTime), int):
    config["blockchain"]["difficulty"]["confirmationTime"] = int(confirmationTime)
  print(colored("\nConfiguration Complete!", "green", attrs=["bold"]))
  config["time"] = round(time.time())
  with open("config.json", "w") as w:
    json.dump(config, w, indent=4)
  time.sleep(2)
  clear()
  mine()

def mine():
  while True:
    print(colored("[!] - Mining Initiated...", "yellow", attrs=["bold"]))
    mining.mine()
    if mining.status == 0:
      print(colored("[!] - Block Invalid. Unsuccessful Mining", "red", attrs=["bold"]))
      time.sleep(1)
      clear()
    elif mining.status == 1:
      print(colored("[!] - Successfully Mined Block! Check It Out At /data/wordChain.json", "green", attrs=["bold"]))
      time.sleep(1)
      clear()

if config["time"] == 0:
  setup()
else:
  print(colored("""
██████╗░██╗░█████╗░████████╗██╗░█████╗░███╗░░██╗░█████╗░██████╗░██╗░░░██╗██████╗░░█████╗░░██╗░░░░░░░██╗
██╔══██╗██║██╔══██╗╚══██╔══╝██║██╔══██╗████╗░██║██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗██╔══██╗░██║░░██╗░░██║
██║░░██║██║██║░░╚═╝░░░██║░░░██║██║░░██║██╔██╗██║███████║██████╔╝░╚████╔╝░██████╔╝██║░░██║░╚██╗████╗██╔╝
██║░░██║██║██║░░██╗░░░██║░░░██║██║░░██║██║╚████║██╔══██║██╔══██╗░░╚██╔╝░░██╔═══╝░██║░░██║░░████╔═████║░
██████╔╝██║╚█████╔╝░░░██║░░░██║╚█████╔╝██║░╚███║██║░░██║██║░░██║░░░██║░░░██║░░░░░╚█████╔╝░░╚██╔╝░╚██╔╝░
╚═════╝░╚═╝░╚════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░╚════╝░░░░╚═╝░░░╚═╝░░\n\n""", "red", attrs=["bold"]))
  hash.verify()
  if config["tampered"]:
    print(colored("Variant: Tampered", "red", attrs=["bold"]))
  elif config["tampered"] == False:
    print(colored("Variant: Intact", "green", attrs=["bold"]))
  elif hash.err == 404:
    print(colored("Variant: unknown", "yellow", attrs=["bold"]))
  time.sleep(2)
  clear()
  mine()
