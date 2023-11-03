
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def restorecord_bypass():
    Output.SetTitle(f"RestoreCord Bypasser")
    bypassed = 0
    error = 0
    args = []
    tokens = TokenManager.get_tokens()

    def bypass(token, guild_id, bot_id):
        nonlocal bypassed, error
        session = Client.get_session(token)
        query = {
            "client_id":{bot_id},
            "response_type":"code",
            "redirect_uri": "https://restorecord.com/api/callback",
            "scope":"identify guilds.join",
            "state":{guild_id}
        }
        auth = session.post(f"https://discord.com/api/v9/oauth2/authorize", params=query, json={"permissions":"0","authorize":True})
        if "location" in auth.text:
            answer = auth.json()["location"]
            result = session.get(answer, allow_redirects=True)

            if result.status_code in [307, 403, 200]:
                Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
                bypassed += 1
            else:
                Output.error_logger(token, result.text, result.status_code)
                error += 1
        else:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({auth.status_code}) {Fore.RED}({auth.text})")
            error += 1

    def thread_complete(future):
        nonlocal bypassed, error
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

    guild_id = utility.ask("Guild ID")
    bot_id = utility.ask("Bot ID")
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
                    args = [token, guild_id, bot_id]
                    future = executor.submit(bypass, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info", config).notime(f"Bypassed {str(bypassed)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}bypassed: {str(bypassed)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()