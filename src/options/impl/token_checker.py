import base64
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from utils.util import *


def token_checker():
    valid = 0
    locked = 0
    invalid = 0
    error = 0
    config = Config()
    args = []
    Output("info", config).notime("Do you want to check the tokens in cache or custom path")
    print(f'''
    {Fore.BLUE}[{Fore.RED}1{Fore.BLUE}] Cache Checker
    {Fore.BLUE}[{Fore.RED}2{Fore.BLUE}] Custom Checker\n''')

    path = utility.ask("Choice")

    if path == '2':
        path = utility.ask("Enter the custom path to load tokens from").strip()
        tokens = TokenManager.custom_path(path)
    else:
        tokens = TokenManager.get_tokens()


    def check_token(token):
        nonlocal valid, locked, invalid, error
        session, headers, cookie = Header.get_client(token)
        result = session.get("https://discord.com/api/v9/users/@me/settings", headers=headers, cookies=cookie)

        if result.status_code == 200:
            Output("good", config, token).log(f"Valid -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            valid += 1
        elif "You need to verify your account in order to perform this action." in result.text:
            Output("info", config, token).log(f"Locked -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            locked += 1
        elif "Unauthorized" in result.text:
            Output("bad", config, token).log(f"Invalid -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            invalid += 1
        else:
            
            error += 1

    def thread_complete(future):
        nonlocal valid, locked, invalid, error
        result = future.result()

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

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
                    args = [token]
                    future = executor.submit(check_token, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info", config).notime(f"Checked {len(tokens)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Valid: {str(valid)}",
            f"{Fore.LIGHTBLACK_EX}Locked: {str(locked)}",
            f"{Fore.LIGHTRED_EX}Invalid: {str(invalid)}",
            f"{Fore.LIGHTCYAN_EX}Errors: {str(error)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(status)
        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()
        