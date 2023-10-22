
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore
import typing
from src import *

def soundboard_spammer():
    Output.SetTitle(f"Sound Board Spammer")
    tokens = TokenManager.get_tokens()
    tokenn = TokenManager.get_random_token()
    session, headers, cookie = Header.get_client(tokenn)

    def send(token, channel_id, sounds: list[dict[str, typing.Union[str, int]]]):
        session, headers, cookie = Header.get_client(token)
        while True:
            sound = random.choice(sounds)
            data = {
                "sound_id":sound.get("sound_id"),
                "emoji_id":None,
                "emoji_name":sound.get("emoji_name"),
                "override_path": sound.get("override_path")
            }
            result = session.post(f"https://discord.com/api/v9/channels/{channel_id}/voice-channel-effects", headers=headers, cookies=cookie, json=data)

            if result.status_code == 204:
                Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            elif result.status_code == 429:
                pass
            elif result.text.startswith('{"captcha_key"'):
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
            elif result.text.startswith('{"message": "401: Unauthorized'):
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")
            elif "Cloudflare" in result.text:
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
            elif "\"code\": 40007" in result.text:
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
            elif "\"code\": 40002" in result.text:
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
            elif "\"code\": 10006" in result.text:
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
            elif "\"code\": 50168" in result.text:
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Not In A VC)")
            elif "\"code\": 50001" in result.text:
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")
            else:
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")

    def thread_complete(future):
        debug = config._get("debug_mode")
        try:
            result = future.result()
        except Exception as e:
            if debug == True:
                Output("dbg", config).log(f"Error -> {e}")
            else:  
                pass

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    channel_id = utility.ask("Channel ID")
    max_threads = utility.asknum("Thread Count")
    sounds = requests.get("https://discord.com/api/v9/soundboard-default-sounds", headers=headers, cookies=cookie).json()

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
                    args = [token, channel_id, sounds]
                    future = executor.submit(send, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()