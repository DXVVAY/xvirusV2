
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def send(token, message, channel_id, title):  
    try:
        session = Client.get_session(token)
        headers["content-type"] = "application/json"
        while True:
            try:
                data = {
                    "auto_archive_duration": "4320",
                    "location": "Plus Button",
                    "name": title,
                    "type": "11"
                }
                req = session.post(f"https://discord.com/api/v9/channels/{channel_id}/threads", json=data)
                
                if req.status_code == 201:
                    result = session.post(
                        f"https://discord.com/api/v9/channels/{req.json()['id']}/messages",
                        headers=headers,
                        json={
                            "content": message,
                            "nonce": str(Decimal(time.time()*1000-1420070400000)*4194304).split(".")[0],
                            "tts": False
                        }
                    )
                    if result.status_code == 200:
                        Output("good", config, token).log(f"Success {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
                    elif result.status_code == 429:
                        pass
                    else:
                        Output.error_logger(token, result.text, result.status_code)
                elif req.status_code == 429:
                    Output("bad", config, token).log(f"Rate Limited {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code})")
                    time.sleep(float(req.json()['retry_after']))
                else:
                    Output("bad", config, token).log(f"Error Creating Thread {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code})")
            except Exception as e:
                Output("bad", config).log(f"{e}")
    except Exception as e:
        Output("bad", config).log(f"{e}")

def mass_thread():
    Output.SetTitle(f"Mass Thread")
    args = []
    tokens = TokenManager.get_tokens()

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    channel_id = utility.ask("Channel ID")
    title = utility.ask("Thread Title")
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
                    args = [token, message, channel_id, title]
                    send(*args)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

            threads = []
            for token in tokens:
                thread = threading.Thread(target=thread_send, args=(token,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
        else:
            Output("bad", config).log(f"No tokens were found in cache")
            Output.PETC()