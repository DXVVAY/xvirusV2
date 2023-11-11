from src import *

def send(token, message, channel_id, title):  
    try:
        session = Client.get_session(token)
        while True:
            try:
                data = {
                    "auto_archive_duration": "4320",
                    "location": "Plus Button",
                    "name": title,
                    "type": "11"
                }
                req = session.post(f"https://discord.com/api/v9/channels/{channel_id}/threads", json=data)
                
                if req.status_code == 201:
                    result = session.post(
                        f"https://discord.com/api/v9/channels/{req.json()['id']}/messages",
                        json={
                            "content": message,
                            "nonce": str(Decimal(time.time()*1000-1420070400000)*4194304).split(".")[0],
                            "tts": False
                        }
                    )
                    if result.status_code == 200:
                        Output("good", token).log(f"Success {Fore.LIGHTBLACK_EX}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
                    elif result.status_code == 429:
                        pass
                    else:
                        Output.error_logger(token, result.text, result.status_code)
                elif req.status_code == 429:
                    Output("bad", token).log(f"Rate Limited {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code})")
                    time.sleep(float(req.json()['retry_after']))
                else:
                    Output("bad", token).log(f"Error Creating Thread {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code})")
            except Exception as e:
                Output("bad").log(f"{e}")
    except Exception as e:
        Output("bad").log(f"{e}")

def mass_thread():
    Output.set_title(f"Mass Thread")
    tokens = TokenManager.get_tokens()
    channel_id = utility.ask("Channel ID")
    title = utility.ask("Thread Title")
    message = utility.ask("Message")
    max_threads = utility.asknum("Thread Count")
    max_threads = int(max_threads)


    while True:
        if tokens:
            def thread_send(token):
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, message, channel_id, title]
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