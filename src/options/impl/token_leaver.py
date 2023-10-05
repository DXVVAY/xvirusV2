import base64
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from utils.util import *

def token_leaver():
    left = 0
    error = 0
    config = Config()
    args = []
    tokens = TokenManager.get_tokens()

    def leave(token, guild_id):
        nonlocal left, error
        session, headers, cookie = Header.get_client(token)
        result = session.delete(f"https://discord.com/api/v9/users/@me/guilds/{guild_id}", headers=headers, cookies=cookie, json={
            'session_id': utility.rand_str(32),
        })

        if result.status_code == 204:
            Output("good", config, token).log(f"Successfully Left Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            left += 1
        elif result.text.startswith('{"captcha_key"'):
            Output("bad", config, token).log(f"Error Leaving Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
            error += 1
        elif result.text.startswith('{"message": "401: Unauthorized'):
            Output("bad", config, token).log(f"Error Leaving Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")
            error += 1
        elif "Cloudflare" in result.text:
            Output("bad", config, token).log(f"Error Leaving Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
            error += 1
        elif "\"code\": 40007" in result.text:
            Output("bad", config, token).log(f"Error Leaving Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
            error += 1
        elif "\"code\": 40002" in result.text:
            Output("bad", config, token).log(f"Error Leaving Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
            error += 1
        elif "\"code\": 10006" in result.text:
            Output("bad", config, token).log(f"Error Leaving Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
            error += 1
        else:
            Output("bad", config, token).log(f"Error Leaving Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
            error += 1

    def thread_complete(future):
        nonlocal left, error
        result = future.result()

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    guild_id = utility.ask("Guild ID")
    max_threads = utility.asknum("Thread Count")

    try:
        if not max_threads.strip():
            max_threads = "13"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "13"

    if tokens:
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for token in tokens:
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, guild_id]
                    future = executor.submit(leave, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info", config).notime(f"Left {str(left)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Left: {str(left)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()