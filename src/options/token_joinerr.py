
import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from base64 import b64encode
from colorama import Fore

from src import *

def token_joiner():
    Output.SetTitle(f"Token Joiner")
    joined = 0
    error = 0
    args = []
    tokens = TokenManager.get_tokens()

    def runJoiner(token, invite):
        retry, rqdata, rqtoken = join(token, invite, "","")
        if retry:
            proxy = "http://" + ProxyManager.clean_proxy(ProxyManager.random_proxy())
            solver = Captcha(proxy=proxy, siteKey="b2b02ab5-7dae-4d6f-830e-7b55634c888b", siteUrl="https://discord.com/", rqdata=rqdata)
            Output("cap", config).log(f'Solving Captcha...')
            capkey = solver.solveCaptcha()
            if capkey is not None:
                Output("cap", config).log(f"Solved Captcha -> {Fore.LIGHTBLACK_EX} {capkey[:70]}")
            else: 
                Output("bad", config).log(f"Failed To Solve Captcha -> {Fore.LIGHTBLACK_EX} {capkey}")
            join(token, invite, capkey, rqtoken)

    def join(token, invite, capkey, rqtoken):
        nonlocal joined, error
        session = Client.get_session(token)
        
        if capkey != "":
            headers["x-captcha-key"] = capkey
            headers["x-captcha-rqtoken"] = rqtoken
            
        if capkey != "":
            data = {
                "captcha_key": capkey,
                "captcha_rqtoken": rqtoken,
                "session_id": utility.rand_str(32),
            }  
        else:
            data = {"session_id": utility.rand_str(32),}

        req = requests.get(f"https://discord.com/api/v9/invites/{invite}?with_counts=true&with_expiration=true", headers=headers)
        if req.status_code == 200:
            res = req.json()
            context = {
                "location": "Join Guild",
                "location_guild_id": str(res['guild']['id']),
                "location_channel_id": str(res['channel']['id']),
                "location_channel_type": int(res['channel']['type'])
            }
            json_data = json.dumps(context)
            xcontext = b64encode(json_data.encode()).decode()
            headers["x-context-properties"] = xcontext
        else:
            pass
        result = session.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, cookies=cookie, json=data)

        if result.status_code == 200:
            Output("good", config, token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            joined += 1
            return False, None, None  
        elif result.text.startswith('{"captcha_key"'):
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
            use_captcha = config._get("use_captcha")
            if use_captcha is True:
                return True, result.json()["captcha_rqdata"], result.json()["captcha_rqtoken"]
            else:
                error += 1
                return False, None, None 
        elif result.text.startswith('{"message": "401: Unauthorized'):
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")
            error += 1
            return False, None, None  
        elif "Cloudflare" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
            error += 1
            return False, None, None  
        elif "\"code\": 40007" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
            error += 1
            return False, None, None  
        elif "\"code\": 40002" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
            error += 1
            return False, None, None  
        elif "\"code\": 10006" in result.text:
            Output("bad", config, token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
            error += 1
            return False, None, None  
        else:
            Output("bad", config, token).log(f"Error -> {token[:40]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
            error += 1

        return False
        
    def thread_complete(future):
        nonlocal joined, error
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

    invite = utility.ask("Invite")
    invite = invite.replace("https://discord.gg/", "").replace("https://discord.com/invite/", "").replace("discord.gg/", "").replace("https://discord.com/invite/", "")
    max_threads = utility.asknum("Thread Count")
    req = requests.get(f"https://discord.com/api/v9/invites/{invite}?with_counts=true&with_expiration=true")
    if req.status_code == 200:
        res = req.json()
        Output("info", config).notime(f"Joining {Fore.RED}{res['guild']['name']}")
    else:
        pass

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
                    args = [token, invite]
                    future = executor.submit(runJoiner, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info", config).notime(f"Joined {str(joined)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Joined: {str(joined)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}"
        print(f" {status}")
        use_captcha = config._get("use_captcha")
        if use_captcha is True:
            Captcha.getCapBal()
            print()
        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in cache")
        Output.PETC()