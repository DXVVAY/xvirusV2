import time
import os
from colorama import Fore, Back, Style  
from utils import ui
from tls_client import Session
import user_agents
import base64
import json
import websocket
from utils.bodycap import BodyCap
import secrets

SOLVER = BodyCap("admin")


class BoostBot:
    def __init__(self, token) -> None:
        self.token = token
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        self.parsed_ua = user_agents.parse(self.user_agent)
        self.session = Session(
            client_identifier="chrome_104"
        )
        self.session.proxies = f""
        self.xsuper = base64.b64encode(json.dumps({
            "os": "Windows",
            "browser": self.parsed_ua.browser.family,
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": self.user_agent,
            "browser_version": self.parsed_ua.browser.version_string,
            "os_version": self.parsed_ua.os.version_string,
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": 244874,
            "client_event_source": None
        }).encode()).decode()
        
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7',
            'Authorization': self.token,
            'Cookie': '__dcfduid=8fbe4ff02ed511ee882f35287c00d69a; __sdcfduid=8fbe4ff12ed511ee882f35287c00d69aefc864e10d067b7c0cd51d136a80abfbe002f83bf2cd7419bee1928e6d69d672; _gcl_au=1.1.2109856265.1692260163; _ga_Q149DFWHT7=GS1.1.1693333274.8.0.1693333276.0.0.0; __stripe_mid=62a377ae-7bfe-419c-b38c-230af973a5a95b48c6; _ga_YL03HBJY7E=GS1.1.1699389865.1.0.1699389865.0.0.0; _ga=GA1.1.1145913896.1692282696; OptanonConsent=isIABGlobal=false&datestamp=Tue+Nov+07+2023+21%3A44%3A26+GMT%2B0100+(Central+European+Standard+Time)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1; cf_clearance=z.kQmFyCGiH1WlJIhYX2ijXRz.pMy5WkYF2u8R33zkI-1699733797-0-1-c7ca96f.5f357a91.5b7df68f-0.2.1699733797; __cfruid=15b2a9f82b6b7fa756d6d9c92bbffdbac5dd283a-1699786620; _cfuvid=ssqFwPBU42myzeJyIT7UblZq54D9p62cmYUf9iGoGq4-1699786620236-0-604800000; locale=en-US',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://discord.com',
            'Pragma': 'no-cache',
            'Referer': 'https://discord.com/channels/@me',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Discord-Timezone': 'Europe/Paris',
            'X-Super-Properties': self.xsuper,
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        self.ws = websocket.WebSocket()
        self.ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        hello = json.loads(self.ws.recv())
        heartbeat_interval = hello['d']['heartbeat_interval']
        self.ws.send(json.dumps({"op": 2,"d": {"token": token,"properties": {"$os": "windows","$browser": "Chrome","$device": "desktop"}}}))
        while True:
            try:
                r = json.loads(self.ws.recv())
                if r["t"] == "READY":
                    self.session_id = r["d"]["session_id"]
                break
            except Exception as e:
                self.session_id = secrets.token_hex(16)
                break


        print(self.session.headers)

    def join_server(self, invite):

        r = self.session.get(f"https://discord.com/api/v9/invites/{invite}")
        if r.status_code == 404:
            print(r.text)
            return
        
        self.server_data = r.json()
        self.session.headers["X-Context-Properties"] = base64.b64encode(json.dumps({
            "location": "Join Guild",
            "location_guild_id": self.server_data["guild"]["id"],
            "location_channel_id": self.server_data["channel"]["id"],
            "location_channel_type": self.server_data["channel"]["type"],
        }).encode()).decode()

        print(self.session.headers["X-Context-Properties"])
        

        r = self.session.post(f"https://discord.com/api/v9/invites/{invite}", json={
            "session_id": self.session_id
        }, proxy=self.session.proxies)
        print(r.text)
        if r.status_code == 200:
            print("joined server")
        else:
            if "captcha_key" in r.json():
                captcha = None
                while not captcha:
                    res = SOLVER.solve_hcaptcha(r.json()["captcha_sitekey"], "discord.com", rqdata=r.json()["captcha_rqdata"], proxy=self.session.proxies)
                    if res["success"]:
                        print("solved captcha")
                        captcha = res["solution"]
                
                self.session.headers["X-Captcha-Key"] = captcha
                self.session.headers["X-Captcha-Rqtoken"] = r.json()["captcha_rqtoken"]
                self.join_server(invite)
                self.session.headers.pop("X-Captcha-Key")
                self.session.headers.pop("X-Captcha-Rqtoken")
                    
            else:
                print("error " + r.text)
                return False
        
        return r.json()
    
    def snowflake(self):
        unixts = time.time()
        return str((int(unixts)*1000-1420070400000)*4194304)


    def boost(self, invite):
        print("real")
        print(self.join_server(invite))
    

def run():
    os.system("cls")
    #invite = input(f"\n{Fore.WHITE}[{ui.COLOR}>{Fore.WHITE}] {Fore.WHITE}Invite: ")
    invite = "7APvcuvN"

    BoostBot("OTczMTcxNDgzODY4Mjc4ODY0.GpxhuE.ckVBPbEGeFFZzZUtraRtzfmfZPcHiGMiilOlV4").boost(invite)