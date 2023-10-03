import os
import json
import concurrent.futures
import time
import random
import sys
import websocket
from utils.util import *
from colorama import Fore

def onliner(token, show=False):
    ws = websocket.WebSocket()
    ws.connect("wss://gateway.discord.gg/?encoding=json&v=9")
    response = ws.recv()
    event = json.loads(response)
    heartbeat_interval = int(event["d"]["heartbeat_interval"]) / 1000
    ws.send(
        json.dumps(
            {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {
                        "$os": sys.platform,
                        "$browser": "RTB",
                        "$device": f"{sys.platform} Device",
                    },
                    "presence": {
                        "status": random.choice(["online", "idle", "dnd"]),
                        "since": 0,
                        "activities": [],
                        "afk": False,
                    },
                },
                "s": None,
                "t": None,
            }
        )
    )
    if show:
        config = Config()
        Output("good", config, token).log(f"Successfully Onlined {Fore.BLUE}({token})")

    time.sleep(heartbeat_interval)
    ws.close()

def token_onliner():
    max_threads = utility.asknum("Thread Count")
    tokens = TokenManager.get_tokens()
    config = Config()
    show = True
    if tokens:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            for token in tokens:
                token = TokenManager.OnlyToken(token)
                try:
                    args = [token, show]
                    executor.submit(onliner, *args)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()

def online_tokens(show=False):
    max_threads = 9
    tokens = TokenManager.get_tokens()
    config = Config()
    show = show
    if tokens:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            for token in tokens:
                token = TokenManager.OnlyToken(token)
                try:
                    args = [token, show]
                    executor.submit(onliner, *args)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")
    else:
        Output("bad", config).log(f"No tokens were found in cache")