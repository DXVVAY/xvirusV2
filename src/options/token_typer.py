
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def token_typer():
    Output.set_title(f"Token Fake Typer")
    args = []
    tokens = TokenManager.get_tokens()

    def send(token, channel_id):
        session = Client.get_session(token)
        while True:
            result = session.post(f"https://discord.com/api/v9/channels/{channel_id}/typing")

            if result.status_code == 204:
                Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            elif result.status_code == 429:
                pass
            else:
                Output.error_logger(token, result.text, result.status_code)

    def thread_complete(future):
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

    channel_id = utility.ask("Channel ID")
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
                    args = [token, channel_id]
                    future = executor.submit(send, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad").log(f"{e}")
    else:
        Output("bad").log(f"No tokens were found in cache")
        Output.PETC()