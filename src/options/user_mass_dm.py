
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore

from src import *

def user_mass_dm():
    Output.set_title(f"User Mass DM")
    sent = 0
    error = 0
    args = []
    tokens = TokenManager.get_tokens()

    def runMassDm(token, user_id, message):
        retry, rqdata, rqtoken = send(token, user_id, message, "", "")
        if retry:
            proxy = "http://" + ProxyManager.clean_proxy(ProxyManager.random_proxy())
            solver = Captcha(proxy=proxy, siteKey="b2b02ab5-7dae-4d6f-830e-7b55634c888b", siteUrl="https://discord.com/", rqdata=rqdata)
            Output("cap").log(f'Solving Captcha...')
            capkey = solver.solveCaptcha()
            if capkey is not None:
                Output("cap").log(f"Solved Captcha -> {Fore.LIGHTBLACK_EX} {capkey[:70]}")
            else: 
                Output("bad").log(f"Failed To Solve Captcha -> {Fore.LIGHTBLACK_EX} {capkey}")
            send(token, user_id, message, capkey, rqtoken)

    def send_message(token, channel_id, message) -> None:
        nonlocal sent, error
        session = Client.get_session(token)
        result = session.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",json={
            'session_id': utility.rand_str(32),
            'content': message
        })

        if result.status_code == 200:
            Output("good", config, token).log(f"Success {Fore.LIGHTBLACK_EX}->{Fore.GREEN} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code})")
            sent += 1
        else:
            Output.error_logger(token, result.text, result.status_code)
            error += 1

    def send(token, user_id, message, capkey, rqtoken):
        nonlocal sent, error
        session = Client.get_session(token)
        
        if capkey != "":
            headers["x-captcha-key"] = capkey
            headers["x-captcha-rqtoken"] = rqtoken
            
        if capkey != "":
            data = {
                "captcha_key": capkey,
                "captcha_rqtoken": rqtoken,
                "session_id": utility.rand_str(32),
                "recipients": [user_id],
            }  
        else:
            data = {
                "session_id": utility.rand_str(32),
                "recipients": [user_id],
            }
        result = session.post(f"https://discord.com/api/v9/users/@me/channels", json=data)

        if result.status_code == 200:
            Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            if 'id' in result.json():
                channel_id = result.json()['id']
                send_message(token, channel_id, message) 
                sent += 1
            return False, None, None  
        elif result.text.startswith('{"captcha_key"'):
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
            use_captcha = config._get("use_captcha")
            if use_captcha is True:
                return True, result.json()["captcha_rqdata"], result.json()["captcha_rqtoken"]
            else:
                return False, None, None 
                error += 1
        else:
            Output.error_logger(token, result.text, result.status_code)
            error += 1
            return False, None, None  

        return False
        
    def thread_complete(future):
        nonlocal sent, error
        debug = config._get("debug_mode")
        try:
            result = future.result()
        except Exception as e:
            if debug:
                if "failed to do request" in str(e):
                    message = f"Proxy Error -> {str(e)[:80]}..."
                else:
                    message = f"Error -> {e}"
                Output("dbg").log(message)
            else:
                pass

    if tokens is None:
        Output("bad").log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    user_id = utility.ask("User ID")
    message = utility.ask("Message")
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
                    args = [token, user_id, message]
                    future = executor.submit(runMassDm, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad").log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info").notime(f"Sent Friend Request Using {str(sent)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Sent: {str(sent)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}"
        print(f" {status}")
        Captcha.getCapBal()
        print()
        Output.PETC()
    else:
        Output("bad").log(f"No tokens were found in cache")
        Output.PETC()