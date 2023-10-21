
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def button_presser():
    Output.SetTitle(f"Button Presser")
    pressed = 0
    error = 0
    args = []
    tokens = TokenManager.get_tokens()

    def click(token, guild_id, channel_id, message_id, custom_id, application_id, flags = 0):
        nonlocal pressed, error
        session, headers, cookie = Header.get_client(token)
        data = {
            "application_id": str(application_id),
            "channel_id": str(channel_id),
            "data": {
                "component_type": 2,
                "custom_id": str(custom_id)
            },
            "guild_id": str(guild_id),
            "message_flags": flags,
            "message_id": str(message_id),
            "nonce": str(Decimal(time.time() * 1000 - 1420070400000) * 4194304).split(".")[0],
            'session_id': utility.rand_str(32),
            "type": 3,
        }
        headers.update({"content-type": "application/json"})
        headers.update({"referer": f"https://discord.com/channels/{guild_id}/{channel_id}"})

        result = session.post(f"https://discord.com/api/v9/interactions", headers=headers, cookies=cookie, json=data)

        if result.status_code == 204:
            Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            pressed += 1
        elif result.text.startswith('{"captcha_key"'):
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
            error += 1
        elif result.text.startswith('{"message": "401: Unauthorized'):
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")
            error += 1
        elif "Cloudflare" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
            error += 1
        elif "\"code\": 40007" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
            error += 1
        elif "\"code\": 40002" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
            error += 1
        elif "\"code\": 10006" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
            error += 1
        elif "\"code\": 10004" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Not In Server)")
            error += 1
        else:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
            error += 1

    def thread_complete(future):
        nonlocal pressed, error
        result = future.result()

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    message = utility.message_info()
    guild_id = message["guild_id"]
    channel_id = message["channel_id"]
    message_id = message["message_id"]
    max_threads = utility.asknum("Thread Count")

    buttons = utility.get_buttons(
        token=TokenManager.get_random_token(),
        guild_id=guild_id,
        channel_id=channel_id,
        message_id=message_id
    )

    if buttons == None:
        Output("bad", config).notime("Invalid message and or message has no buttons")
        Output.PETC()

    print()
    for num, button in enumerate(buttons):
        label = button['label'].replace(' ', '') if button['label'] is not None else 'None'
        labels = f"    {Fore.BLUE}[{Fore.RED}{num}{Fore.BLUE}] {Fore.RED}{label}"
        print(labels)
    print()

    buttonnum = utility.ask("button number")
    for button in buttons:
        if buttons.index(button)==int(buttonnum):
            custom_id = button['custom_id']
            application_id = button['application_id']
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
                    args = [token, guild_id, channel_id, message_id, custom_id, application_id]
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