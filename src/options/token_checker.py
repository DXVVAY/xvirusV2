
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *


def token_checker(tokens):
    Output.set_title(f"Token Checker")
    valid = 0
    locked = 0
    invalid = 0
    error = 0
    args = []

    def check_token(token):
        nonlocal valid, locked, invalid, error
        session = Client.get_simple_session()
        session.headers = static_headers
        session.headers.update({"Authorization":token})
        result = session.get("https://discord.com/api/v9/users/@me/settings")

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
            Output("bad", config, token).log(f"Invalid -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) ({result.text})")
            error += 1

    def thread_complete(future):
        nonlocal valid, locked, invalid, error
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
                    args = [token]
                    future = executor.submit(check_token, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad").log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info").notime(f"Checked {len(tokens)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Valid: {str(valid)}",
            f"{Fore.LIGHTBLACK_EX}Locked: {str(locked)}",
            f"{Fore.LIGHTRED_EX}Invalid: {str(invalid)}",
            f"{Fore.LIGHTCYAN_EX}Errors: {str(error)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad").log(f"No tokens were found in cache")
        Output.PETC()
        
