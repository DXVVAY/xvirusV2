import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def webhook_tool():
    Output.SetTitle(f"Webhook Tools")
    session = Client.tls_session()
    args = []
    def spammer(webhook, Message):
        result = session.post(webhook, json={"content": Message})

        if result.status_code == 204 or result.status_code == 200:
            Output("good", config).log(f"Success -> {webhook[:60]} {Fore.LIGHTBLACK_EX}({result.status_code})")
        elif result.text.startswith('{"captcha_key"'):
            Output("bad", config).log(f"Error -> {webhook[:60]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
        elif result.status_code == 429:
            pass   
        elif result.text.startswith('{"message": "401: Unauthorized'):
            Output("bad", config).log(f"Error -> {webhook[:60]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")
        elif "Cloudflare" in result.text:
            Output("bad", config).log(f"Error -> {webhook[:60]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
        elif "\"code\": 40007" in result.text:
            Output("bad", config).log(f"Error -> {webhook[:60]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
        elif "\"code\": 40002" in result.text:
            Output("bad", config).log(f"Error -> {webhook[:60]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
        elif "\"code\": 10006" in result.text:
            Output("bad", config).log(f"Error -> {webhook[:60]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
        else:
            Output("bad", config).log(f"Error -> {webhook[:60]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")

    def webhook_spammer():
        webhook = utility.ask("Webhook")
        message = utility.ask("Message")
        utility.CheckWebhook(webhook)
        max_threads = utility.asknum("Thread Count")

        try:
            if not max_threads.strip():
                max_threads = 16
            else:
                max_threads = int(max_threads)
        except ValueError:
            max_threads = 16

        if webhook:
            while True:
                with ThreadPoolExecutor(max_workers=max_threads) as executor:
                    try:
                        args = [webhook, message]
                        futures = [executor.submit(spammer, *args) for _ in range(max_threads)]
                        for future in futures:
                            future.result()
                    except Exception as e:
                        Output("bad", config).log(f"Error: {e}")

        else:
            Output("bad", config).log(f"Invalid Webhook")
            Output.PETC()
    
    utility.make_menu("Webhook Spammer", "Webhook Deleter")
    choice = utility.ask("Choice")

    if choice == '1':
        webhook_spammer()
    
    if choice == '2':
        webhook = utility.ask("Webhook")
        utility.CheckWebhook(webhook)
        session.delete(webhook)
        Output("good", config).notime("Webhook successfully deleted")
