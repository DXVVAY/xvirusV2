import base64
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from utils.util import *
from src.main.scrape_ids import id_scraper

def send(token, message, channelid, massping, amount=None):
    config = Config()
    
    try:
        session, headers, cookie = Header.get_client(token)

        while True:
            try:
                if massping == 'y':
                    content = f"{message} {utility.get_random_id(int(amount))}"
                else:
                    content = message

                data = {'session_id': utility.rand_str(32), "content": content}
                result = session.post(f"https://discord.com/api/v9/channels/{channelid}/messages", headers=headers, cookies=cookie, json=data)

                if result.status_code == 200:
                    Output("good", config, token).log(f"Success {Fore.LIGHTBLACK_EX}->{Fore.GREEN} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
                elif result.text.startswith('{"captcha_key"'):
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
                elif result.text.startswith('{"message": "401: Unauthorized'):
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")   
                elif result.status_code == 429:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Rate Limit)")
                elif "\"code\": 50001" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")    
                elif "Cloudflare" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
                elif "\"code\": 40007" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
                elif "\"code\": 40002" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
                elif "\"code\": 10006" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
                elif "\"code\": 50013" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")
                else:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
            except Exception as e:
                Output("bad", config).log(f"{e}")
    except Exception as e:
        Output("bad", config).log(f"{e}")

def channel_spammer():
    config = Config()
    args = []
    tokens = TokenManager.get_tokens()

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    channel_id = utility.ask("Channel ID")
    message = utility.ask("Message")
    max_threads = utility.asknum("Thread Count")
    massping = utility.ask("Massping (y/n)")
    amount = None
    
    if massping == 'y':
        id_scraper()
        ids = utility.get_ids()
        amount = utility.ask(f"Amount Of pings (Don't exceed {len(ids)})")
    
    try:
        if not max_threads.strip():
            max_threads = "13"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "13"

    while True:
        if tokens:
            def thread_send(token):
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, message, channel_id, massping, amount]
                    send(*args)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

            threads = []
            for token in tokens:
                thread = threading.Thread(target=thread_send, args=(token,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
        else:
            Output("bad", config).log(f"No tokens were found in cache")
            Output.PETC()