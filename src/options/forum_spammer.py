
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import secrets
from colorama import Fore

from src import *

def send(token, channel_id, message, title):  
    try:
        session = Client.get_session(token)
        headers["content-type"] = "application/json"
        while True:
            try:
                data = {
                        "name":secrets.token_urlsafe(16),
                        "auto_archive_duration":10080,
                        "applied_tags": [],
                        "message":
                        {
                            "content": secrets.token_urlsafe(16)
                        }
                }
                req = session.post(f"https://discord.com/api/v9/channels/{channel_id}/threads?use_nested_fields=true", headers=headers, cookies=Client.get_cookies(session), json=data)
                
                if req.status_code == 201:
                    result = session.post(
                        f"https://discord.com/api/v9/channels/{req.json()['id']}/messages",
                        headers=headers,
                        cookies=Client.get_cookies(session),
                        json={
                            "content": secrets.token_urlsafe(16),
                            "nonce": str(Decimal(time.time()*1000-1420070400000)*4194304).split(".")[0],
                            "tts": False
                        }
                    )
                    if result.status_code == 200:
                        Output("good", config, token).log(f"Success {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
                    elif result.text.startswith('{"captcha_key"'):
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
                    elif result.text.startswith('{"message": "401: Unauthorized'):
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")   
                    elif result.status_code == 429:
                        pass
                    elif "\"code\": 50001" in result.text:
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")    
                    elif "Cloudflare" in result.text:
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
                    elif "\"code\": 40007" in result.text:
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
                    elif "\"code\": 40002" in result.text:
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
                    elif "\"code\": 10006" in result.text:
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
                    elif "\"code\": 50013" in result.text:
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")
                    else:
                        Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
                elif req.status_code == 429:
                    Output("bad", config, token).log(f"Rate Limited {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code})")
                    time.sleep(float(req.json()['retry_after']))
                else:
                    Output("bad", config, token).log(f"Error Creating Thread {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code}) ({req.text})")
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
                    args = [token, message, channel_id, title]
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