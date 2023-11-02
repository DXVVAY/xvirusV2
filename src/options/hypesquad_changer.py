
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def hypesquad_changer():
    Output.SetTitle(f"Hypesquad Changer")
    changed = 0
    error = 0
    args = []
    tokens = TokenManager.get_tokens()

    def send(token, house):
        nonlocal changed, error
        session = Client.get_session(token)
        result = session.post(f"https://discord.com/api/v9/hypesquad/online", json={
            'house_id': house,
        })

        if result.status_code == 204:
            Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            changed += 1
        else:
            Output.error_logger(token, result.text, result.status_code)
            error += 1

    def thread_complete(future):
        nonlocal changed, error
        debug = config._get("debug_mode")
        try:
            result = future.result()
        except Exception as e:
            if debug:
                if "failed to do request" in str(e):
                    message = f"Proxy Error -> {str(e)[:80]}..."
                else:
                    message = f"Error -> {e}"
                Output("dbg", config).log(message)
            else:
                pass

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    print(f'''
        {Fore.MAGENTA}[1]{Fore.MAGENTA} HypeSquad Bravery
        {Fore.RED}[2]{Fore.LIGHTRED_EX} HypeSquad Brilliance
        {Fore.LIGHTGREEN_EX}[3]{Fore.LIGHTGREEN_EX} HypeSquad Balance
    ''')
    house = utility.ask("House")
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
                    args = [token, house]
                    future = executor.submit(send, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info", config).notime(f"Changed HypeSquad For {str(changed)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Changed: {str(changed)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()