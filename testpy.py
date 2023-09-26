import threading
import json
import time
from base64 import b64encode
from capmonster_python import capmonster, HCaptchaTask
from utils import *
import string

config = Config()

def rand_str(length:int) -> str:
    return ''.join(random.sample(string.ascii_lowercase+string.digits, length))
    
def join(invite, xcontent, token):
    try:
        session, headers, cookie = Header.get_client(token)

        headers["content-length"] = "0"
        headers['X-Fingerprint'] = session.get('https://discord.com/api/v9/experiments').json()['fingerprint']
        try:
            res = session.get(
                f"https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true", headers=headers).json()
            jsonContext = {
                "location": "Join Guild",
                "location_guild_id": str(res['guild']['id']),
                "location_channel_id": str(res['channel']['id']),
                "location_channel_type": int(res['channel']['type'])
            }
            json_str = json.dumps(jsonContext)
            xContext = b64encode(json_str.encode()).decode()
            headers["x-context-properties"] = xContext
        except Exception as e:
            pass

        result = session.post(f'https://discord.com/api/v9/invites/{invite}', headers=headers)
        if result.status_code == 200:
            Output("good", config, token).log(f"Joined -> {Fore.LIGHTBLACK_EX}(discord.gg/{invite}) {Fore.GREEN}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
        elif "captcha_key" in result.text:
            time.sleep(1)
            Output("bad", config, token).log(f"Error joining -> {Fore.LIGHTBLACK_EX}(discord.gg/{invite}) {Fore.RED}-> {token} {Fore.LIGHTBLACK_EX}(Captcha)")
            captcha_sitekey = result.json()["captcha_sitekey"]
            captcha_rqdata = result.json()["captcha_rqdata"]
            captcha_rqtoken = result.json()["captcha_rqtoken"]
            captcha = Captcha.solve(f"https://discord.com/api/v9/invites/{invite}", captcha_sitekey, captcha_rqdata)
            Output("good", config).log(f"Solved Captcha -> {Fore.LIGHTBLACK_EX}(discord.gg/{invite}) {Fore.GREEN}-> {Fore.LIGHTBLACK_EX}({captcha[0:20]}******)")
            data = {
                'captcha_key': captcha,
                'captcha_rqtoken': captcha_rqtoken
            }
            capreq = session.post(f'https://discord.com/api/v9/invites/{invite}', headers=headers, json={
                        'captcha_key': captcha,
                        'captcha_rqtoken': captcha_rqdata
                        })
            print(capreq.text)
            if '200' in str(capreq):
                Output("good", config, token).log(f"Joined -> {Fore.LIGHTBLACK_EX}(discord.gg/{invite}) {Fore.GREEN}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            else:
                Output("bad", config, token).log(f"Error joining -> {Fore.LIGHTBLACK_EX}(discord.gg/{invite}) {Fore.RED}-> {token} {Fore.LIGHTBLACK_EX}({capreq.json()['message']})")
        else:
                Output("bad", config, token).log(f"Error joining -> {Fore.LIGHTBLACK_EX}(discord.gg/{invite}) {Fore.RED}-> {token} {Fore.LIGHTBLACK_EX}({result.json()['message']})")
    except Exception as e:
        print(f"Error joining -> {Fore.LIGHTBLACK_EX}(discord.gg/{invite}) {Fore.RED}-> {Fore.LIGHTBLACK_EX}({e})")

def joiner():
    Start_balance = utility.getCapBal()
    
    invite = utility.ask("invite")
    invite = invite.replace("https://discord.gg/", "").replace("https://discord.com/invite/", "").replace("discord.gg/", "").replace("https://discord.com/invite/", "")
    invite_parts = invite.split("/")
        
    delay = utility.ask("delay")
    if delay == "":
        delay = 0
    if isinstance(delay, str) and not delay.isdigit() and not "." in delay:
        Output("error", config).log(f"{Fore.RED}FAILED{Fore.WHITE} {Fore.LIGHTBLACK_EX}(Delay must be a number)")
        time.sleep(3)
        Output.PETC()
    delay = float(delay)
        
    Output("info", config).notime(f"Getting guild info...")
    guild = utility.get_guild(invite)
    if guild is not None:
        xcontent = Header.x_content_props(guild)
        Output("info", config).notime(f"Joining {Fore.RED}{guild['guild']['name']}")
        time.sleep(1)
    else:
        xcontent = "eyJsb2NhdGlvbiI6IkFjY2VwdCBJbnZpdGUgUGFnZSJ9"
        
    utility.threads(func=join, delay=float(delay), return_home=False, args=[invite, xcontent])
    
    End_balance = utility.getCapBal()
    balance_used = float(Start_balance[1:]) - float(End_balance[1:])
    
    info = [
        f"{Fore.LIGHTGREEN_EX}Start: {Start_balance}",
        f"{Fore.LIGHTCYAN_EX}End: {End_balance}",
        f"{Fore.LIGHTRED_EX}Used: ${balance_used:.2f}",
    ]
    status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
    print(status)

joiner()
