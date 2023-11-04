
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import secrets
from colorama import Fore

from src import *

def send(token, guild_id, channel_id, message, title):  
    try:
        session = Client.get_session(token)
        session.headers.update({"referer":f"https://discord.com/channels/{guild_id}/{channel_id}"})
        while True:
            try:
                data = {
                    "name": title,
                    "applied_tags": [],
                    "auto_archive_duration":4320,
                    "message":
                    {
                        "content": message
                    },
                }
                req = session.post(f"https://discord.com/api/v9/channels/{channel_id}/threads?use_nested_fields=true", json=data)
                
                if req.status_code == 201:
                    result = session.post(
                        f"https://discord.com/api/v9/channels/{req.json()['id']}/messages",
                        json={
                            "content": secrets.token_urlsafe(16),
                            "nonce": str(Decimal(time.time()*1000-1420070400000)*4194304).split(".")[0],
                            "tts": False
                        }
                    )
                    if result.status_code == 200:
                        Output("good", token).log(f"Success {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
                    elif result.status_code == 429:
                        pass
                    else:
                        Output.error_logger(token, result.text, result.status_code)
                elif req.status_code == 429:
                    Output("bad", token).log(f"Rate Limited {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code})")
                    time.sleep(float(req.json()['retry_after']))
                else:
                    Output("bad", token).log(f"Error Creating Thread {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code}) ({req.text})")
            except Exception as e:
                Output("bad").log(f"{e}")
    except Exception as e:
        Output("bad").log(f"{e}")

def forum_spammer():
    Output.set_title(f"Mass Thread")
    args = []
    tokens = TokenManager.get_tokens()

    if tokens is None:
        Output("bad").log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    guild_id = utility.ask("Guild ID")
    channel_id = utility.ask("Channel ID")
    title = utility.ask("Title")
    message = utility.ask("Message")
    max_threads = utility.asknum("Thread Count")
    
    try:
        if not max_threads.strip():
            max_threads = "16"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "16"

    while True:
        if tokens:
            def thread_send(token):
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, guild_id, channel_id, message, title]
                    send(*args)
                except Exception as e:
                    Output("bad").log(f"{e}")

            threads = []
            for token in tokens:
                thread = threading.Thread(target=thread_send, args=(token,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
        else:
            Output("bad").log(f"No tokens were found in cache")
            Output.PETC()