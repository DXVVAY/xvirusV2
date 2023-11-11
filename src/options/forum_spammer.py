from src import *

def send(guild_id, channel_id, message, title, token):  
    try:
        session = Client.get_session(token)
        session.headers.update({"referer":f"https://discord.com/channels/{guild_id}/{channel_id}"})
        while True:
            try:
                data = {
                    "name": title,
                    "applied_tags": [],
                    "auto_archive_duration":4320,
                    "message":
                    {
                        "content": message
                    },
                }
                req = session.post(f"https://discord.com/api/v9/channels/{channel_id}/threads?use_nested_fields=true", json=data)
                
                if req.status_code == 201:
                    result = session.post(
                        f"https://discord.com/api/v9/channels/{req.json()['id']}/messages",
                        json={
                            "content": secrets.token_urlsafe(16),
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
                    Output("bad", token).log(f"Error Creating Thread {Fore.LIGHTBLACK_EX}-> {token[:70]} {Fore.LIGHTBLACK_EX}({req.status_code}) ({req.text})")
            except Exception as e:
                Output("bad").log(f"{e}")
    except Exception as e:
        Output("bad").log(f"{e}")

def forum_spammer():
    Output.set_title(f"Mass Thread")
    guild_id = utility.ask("Guild ID")
    channel_id = utility.ask("Channel ID")
    title = utility.ask("Title")
    message = utility.ask("Message")
    max_threads = utility.asknum("Thread Count")
    utility.run_threads(max_threads=max_threads, func=send, args=[guild_id, channel_id, message, title], delay=0)