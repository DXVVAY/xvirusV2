
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def token_reactor():
    Output.SetTitle(f"Message Reactor")
    pressed = 0
    error = 0
    args = []
    tokens = TokenManager.get_tokens()

    def click(token, emoji, message_id, channel_id,):
        nonlocal pressed, error
        session = Client.get_session(token)
        result = session.put(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/%40me?location=Message&burst=false")

        if result.status_code == 204:
            Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            pressed += 1
        else:
            Output.error_logger(token, result.text, result.status_code)
            error += 1

    def thread_complete(future):
        nonlocal pressed, error
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

    message = utility.message_info()
    channel_id = message["channel_id"]
    message_id = message["message_id"]
    max_threads = utility.asknum("Thread Count")
    emojis = utility.get_reactions(channel_id, message_id)

    if emojis == None:
        Output("bad", config).notime("Invalid message and or message has no reacts")
        Output.PETC()

    print()
    for num, emoji in enumerate(emojis):
        name = emoji['name'].replace(' ', '')
        labels = f"    {Fore.BLUE}[{Fore.RED}{num}{Fore.BLUE}] {Fore.RED}{name}"
        print(labels)
    print()

    emojinum = utility.ask("Emoji number")
    for emoji in emojis:
        if emojis.index(emoji)==int(emojinum):
            emoji = emoji['name'].replace(" ", "")
            break

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
                    args = [token, emoji.replace(":", "%3A"), message_id, channel_id]
                    future = executor.submit(click, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info", config).notime(f"Pressed {str(pressed)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Pressed: {str(pressed)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()