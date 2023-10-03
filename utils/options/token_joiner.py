import base64
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from utils import *

def token_joiner():
    joined = 0
    error = 0
    config = Config()
    args = []
    tokens = TokenManager.get_tokens()

    def join(token, invite):
        nonlocal joined, error
        session, headers, cookie = Header.get_client(token)
        result = session.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, cookies=cookie, json={
            'session_id': utility.rand_str(32),
        })

        if result.status_code == 200:
            Output("good", config, token).log(f"Successfully Joined Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            joined += 1
        elif result.text.startswith('{"captcha_key"'):
            Output("bad", config, token).log(f"Error Joining Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
            error += 1
        elif result.text.startswith('{"message": "401: Unauthorized'):
            Output("bad", config, token).log(f"Error Joining Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")
            error += 1
        elif "Cloudflare" in result.text:
            Output("bad", config, token).log(f"Error Joining Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
            error += 1
        elif "\"code\": 40007" in result.text:
            Output("bad", config, token).log(f"Error Joining Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
            error += 1
        elif "\"code\": 40002" in result.text:
            Output("bad", config, token).log(f"Error Joining Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
            error += 1
        elif "\"code\": 10006" in result.text:
            Output("bad", config, token).log(f"Error Joining Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
            error += 1
        else:
            Output("bad", config, token).log(f"Error Joining Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
            error += 1

    def thread_complete(future):
        nonlocal joined, error
        result = future.result()

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    invite = utility.ask("Invite")
    invite = invite.replace("https://discord.gg/", "").replace("https://discord.com/invite/", "").replace("discord.gg/", "").replace("https://discord.com/invite/", "")
    invite_parts = invite.split("/")
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
                    args = [token, invite]
                    future = executor.submit(join, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info", config).notime(f"Joined {str(joined)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Joined: {str(joined)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(status)
        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()