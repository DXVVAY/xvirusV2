
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
        session, headers, cookie = Header.get_client(token)
        query = {
            "client_id":str(bot_id),
            "response_type":"code",
            "redirect_uri": "https://restorecord.com/api/callback",
            "scope":"identify guilds.join",
            "state":str(guild_id)
        }
        auth = requests.post(f"https://discord.com/api/v9/oauth2/authorize", headers=headers, params=query, json={"permissions":"0","authorize":True})
        if "location" in auth.text:
            answer = auth.json()["location"]
            result = requests.get(answer, headers=headers, cookies=cookie, allow_redirects=True)

            if result.status_code in [307, 403, 200]:
                Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
                bypassed += 1
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
            else:
                Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
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