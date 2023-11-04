
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def server_checker():
    Output.set_title(f"Token Server Checker")
    yes = 0
    error = 0
    args = []
    valid_tokens = []
    tokens = TokenManager.get_tokens()
    folder_path = os.path.join(os.getenv('LOCALAPPDATA'), 'xvirus_config')
    file = os.path.join(folder_path, 'xvirus_tokens')

    def check(token, guild_id):
        nonlocal yes, error
        session = Client.get_session(token)
        result = session.get(f"https://discord.com/api/v9/guilds/{guild_id}")

        if result.status_code == 200:
            Output("good", config, token).log(f"In Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            yes += 1
        else:
            Output("bad", config, token).log(f"Not In Server -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            error += 1
            valid_tokens.remove(token)

    def thread_complete(future):
        nonlocal yes, error
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
                    valid_tokens.append(token)
                    args = [token, guild_id]
                    future = executor.submit(check, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad").log(f"{e}")
        
        config.reset("xvirus_tokens")
        with open(file, "w") as f:
            for token in valid_tokens:
                f.write(f"{token}\n")
        elapsed_time = time.time() - start_time
        Output("info").notime(f"Checked {str(yes)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}In Server: {str(yes)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad").log(f"No tokens were found in cache")
        Output.PETC()