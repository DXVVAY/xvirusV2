
import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

tags = ["test"]

def dyno_send(token, guild_id, channel_id, message, max_threads, amount=None):
    try:
        session = Client.get_session(token)

        while True:
            try:
                rand = utility.rand_str(8)
                data = {
                    "type":2,
                    "application_id":"161660517914509312",
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    'session_id': utility.rand_str(32),
                    "data":{
                        "version":"1116144106687692895",
                        "id":"824701594749763611",
                        "name":"tag",
                        "type":1,
                        "options":[
                            {
                                "type":1,
                                "name":"create",
                                "options":[
                                    {
                                        "type":3,
                                        "name":"name",
                                        "value": rand
                                    },
                                        {
                                            "type":3,
                                            "name":"content",
                                            "value": f"``````e {message} {utility.get_random_id(int(amount))} l```"
                                        }
                                ]
                            }
                        ]
                    }
                }
                showdata = {
                        "type":2,
                        "application_id":"161660517914509312",
                        "guild_id": guild_id,
                        "channel_id": channel_id,
                        'session_id': utility.rand_str(32),
                        "data":{
                            "version":"1116144106687692895",
                            "id":"824701594749763611",
                            "name":"tag",
                            "type":1,
                            "options":[
                                {
                                    "type":1,
                                    "name":"raw",
                                    "options":[
                                        {
                                            "type":3,
                                            "name":"name",
                                            "value": random.choice(tags)
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                result = session.post(f"https://discord.com/api/v9/interactions", headers=headers, cookies=cookie, json=data)
                

                if result.status_code == 204:
                    Output("good", config, token).log(f"Success {Fore.LIGHTBLACK_EX}->{Fore.GREEN} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code})")
                    tags.append(rand)
                elif result.text.startswith('{"captcha_key"'):
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
                elif result.text.startswith('{"message": "401: Unauthorized'):
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")   
                elif result.status_code == 429:
                    pass
                elif "\"code\": 50001" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")    
                elif "Cloudflare" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
                elif "\"code\": 40007" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
                elif "\"code\": 40002" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
                elif "\"code\": 10006" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
                elif "\"code\": 50013" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")
                else:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")

                show = session.post(f"https://discord.com/api/v9/interactions", headers=headers, cookies=cookie, json=showdata)

                if show.status_code == 204:
                    Output("good", config, token).log(f"Showing Tag {Fore.LIGHTBLACK_EX}->{Fore.GREEN} {rand} {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({show.status_code})")
                if show.status_code == 429:
                    pass
                else:
                    Output("bad").log(f"Could not show tag {Fore.LIGHTBLACK_EX}->{Fore.RED} {rand} {Fore.LIGHTBLACK_EX}-> {Fore.BLUE} {show.status_code})")
            except Exception as e:
                Output("bad").log(f"{e}")
    except Exception as e:
        Output("bad").log(f"{e}")

def dyno_spammer(guild_id, channel_id, message, max_threads, amount):
    Output.set_title(f"Channel Spammer")
    args = []
    tokens = TokenManager.get_tokens()

    if tokens is None:
        Output("bad").log("Token retrieval failed or returned None.")
        Output.PETC()
        return
    
    try:
        if not max_threads.strip():
            max_threads = "16"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "16"

    while True:
        if tokens:
            def thread_send(token):
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, guild_id, channel_id, message, max_threads, amount]
                    dyno_send(*args)
                except Exception as e:
                    Output("bad").log(f"{e}")

            threads = []
            for token in tokens:
                thread = threading.Thread(target=thread_send, args=(token,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
        else:
            Output("bad").log(f"No tokens were found in cache")
            Output.PETC()

# normal spammer

def send(token, message, channelid, massping, amount=None):  
    try:
        session, headerss, cookie = Client.get_client(token)

        while True:
            try:
                if massping == 'y':
                    content = f"{message} {utility.get_random_id(int(amount))}"
                else:
                    content = f"{message} {utility.rand_str(7)}"
                session.headers = headerss
                data = {'session_id': utility.rand_str(32), "content": content}
                result = session.post(f"https://discord.com/api/v9/channels/{channelid}/messages", cookies=cookie, json=data)

                if result.status_code == 200:
                    Output("good", config, token).log(f"Success {Fore.LIGHTBLACK_EX}->{Fore.GREEN} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code})")
                elif result.text.startswith('{"captcha_key"'):
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
                elif result.text.startswith('{"message": "401: Unauthorized'):
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")   
                elif result.status_code == 429:
                    pass
                elif "\"code\": 50001" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")    
                elif "Cloudflare" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
                elif "\"code\": 40007" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
                elif "\"code\": 40002" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
                elif "\"code\": 10006" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
                elif "\"code\": 50013" in result.text:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")
                else:
                    Output("bad", config, token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:20]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
            except Exception as e:
                Output("bad").log(f"{e}")
    except Exception as e:
        Output("bad").log(f"{e}")

def channel_spammer():
    Output.set_title(f"Channel Spammer")
    args = []
    tokens = TokenManager.get_tokens()

    if tokens is None:
        Output("bad").log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    channel_id = utility.ask("Channel ID")
    message = utility.ask("Message")
    max_threads = utility.asknum("Thread Count")
    massping = utility.ask("Massping (y/n)")
    amount = 0
    
    if massping == 'y':
        guild_id = utility.ask("Guild ID")
        id_scraper(guild_id, channel_id)
        ids = utility.get_ids()
        amount = utility.ask(f"Amount Of pings (Don't exceed {len(ids)})")

        dyno = utility.ask("Use Dyno Mode? <Server Must Have Dyno Tags> (y/n)")
        if dyno == "y":
            dyno_spammer(guild_id, channel_id, message, max_threads, amount)
    
    try:
        if not max_threads.strip():
            max_threads = "16"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "16"

    while True:
        if tokens:
            def thread_send(token):
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, message, channel_id, massping, amount]
                    send(*args)
                except Exception as e:
                    Output("bad").log(f"{e}")

            threads = []
            for token in tokens:
                thread = threading.Thread(target=thread_send, args=(token,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
        else:
            Output("bad").log(f"No tokens were found in cache")
            Output.PETC()