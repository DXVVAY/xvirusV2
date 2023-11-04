from json import loads
from src import *
from time import sleep
from json import dumps
from websocket import WebSocket
from concurrent.futures import ThreadPoolExecutor
import os

def token_vc_joiner():
    joined = 0
    error = 0
    tokens = TokenManager.get_tokens()
    def run(token, guild_id, channel_id, mute, deaf, video):
        nonlocal joined, error
        ws = WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=8&encoding=json")
        hello = loads(ws.recv())
        heartbeat_interval = hello['d']['heartbeat_interval']
        ws.send(dumps({"op": 2,"d": {"token": token,"properties": {"$os": "windows","$browser": "Discord","$device": "desktop"}}}))
        ws.send(dumps({"op": 4,"d": {"guild_id": guild_id,"channel_id": channel_id,"self_mute": mute,"self_deaf": deaf, "self_video": video}}))
        ws.send(dumps({"op": 1,"d": None}))
        sleep(0.1)
        Output("good", config, token).log(f"Success -> {token}")
        joined += 1

    def thread_complete(future):
        nonlocal joined, error
        debug = config._get("debug_mode")
        try:
            result = future.result()
        except Exception as e:
            if debug:
                if "failed to do request" in str(e):
                    message = f"Proxy Error -> {str(e)[:80]}..."
                else:
                    message = f"Error -> {e}"
                Output("dbg").log(message)
            else:
                pass

    if tokens is None:
        Output("bad").log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    guild_id = utility.ask("Guild ID")
    channel_id = utility.ask("Channel ID")
    deaf = utility.ask("Defean (y/n)")
    if deaf == "y":
        deaf = True
    else:
        deaf = False
    mute = utility.ask("Mute (y/n)")
    if mute == "y":
        mute = True
    else:
        mute = False
    video = utility.ask("Video (y/n)")
    if video == "y":
        video = True
    else:
        video = False
    max_threads = utility.asknum("Thread Count")

    try:
        if not max_threads.strip():
            max_threads = "16"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "16"

    if tokens:
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for token in tokens:
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, guild_id, channel_id, mute, deaf, video]
                    future = executor.submit(run, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad").log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info").notime(f"Joined VC Using {str(joined)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Joined: {str(joined)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad").log(f"No tokens were found in cache")
        Output.PETC()