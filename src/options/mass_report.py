import random
import threading
from colorama import Fore
import time
from src import *

def report(channel_id, message_id):
    session = Header.tls_session()
    reasons = {
        31: "MESSAGE_SPAM",
        34: "ABUSE_OR_HARASSMENT"
    }
    reason = random.choice(list(reasons.keys()))
    payload = {
        "version": "1.0",
        "variant": "3",
        "language": "en",
        "breadcrumbs": [
            3,
            reason
        ],
        "elements": {},
        "name": "message",
        "channel_id": channel_id,
        "message_id": message_id
    }
    
    with open('tokens.txt', 'r') as file:  #modify this dex
        tokens = file.readlines()  

    for token in tokens:
        fr = token.strip()
        resp = session.post("https://discord.com/api/v9/reporting/message", headers=bestheader(fr), json=payload)
        if resp.status_code == 200:
            print(f"{Fore.LIGHTBLACK_EX}[{Fore.GREEN}+{Fore.LIGHTBLACK_EX}]{Fore.GREEN} Report was sent successfully")
        else:
            print(f"{Fore.LIGHTBLACK_EX}[{Fore.RED}-{Fore.LIGHTBLACK_EX}]{Fore.RED} Failed to send report {resp.status_code}")

def startreport():
    threads = []
    channel_id = input(f"{Fore.CYAN}Channel ID: ")
    message_id = input(f"{Fore.CYAN}Message ID: ")
    threadin = input(f"{Fore.CYAN}Threads: ")

    try:  #also change this cuz this shit
        threadin = int(threadin)
        for _ in range(threadin):
            t = threading.Thread(target=report, args=(channel_id, message_id))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    except KeyboardInterrupt:
        time.sleep(1)