import tls_client
import websocket
import json
import secrets
import logger
import colorama
import requests
import base64
from src.utils.bodycap import *

SOLVER = BodyCap()

class Discord:
    def __init__(self):
        os.system('cls')
        self.build_number = None
        self.darwin_ver = self.get_darwin_version()
        self.iv1, self.iv2 = str(randint(15, 16)), str(randint(1, 5))
        self.app_version = self.get_app_version()
        self.build_number = self.get_build_number()
        self.user_agent = f"Discord/{self.build_number} CFNetwork/1402.0.8 Darwin/{self.darwin_ver}"
        self.x_super_properties = self.mobile_xprops()

    def mobile_xprops(self):
        u = uuid.uuid4().hex; vendor_uuid = f"{u[0:8]}-{u[8:12]}-{u[12:16]}-{u[16:20]}-{u[20:36]}"
        iphone_models = ["11,2","11,4","11,6","11,8","12,1","12,3","12,5","12,8","13,1","13,2","13,3","13,4","14,2","14,3","14,4","14,5","14,6","14,7","14,8","15,2","15,3",]
        return base64.b64encode(json.dumps({
            "os":"iOS",
            "browser":"Discord iOS",
            "device":"iPhone"+random.choice(iphone_models),
            "system_locale":"sv-SE",
            "client_version":self.app_version,
            "release_channel":"stable",
            "device_vendor_id":vendor_uuid,
            "browser_user_agent":"",
            "browser_version":"",
            "os_version":self.iv1+"."+self.iv2,
            "client_build_number": self.build_number,
            "client_event_source":None,
            "design_id":0
        }).encode()).decode()

    def get_build_number(self):
        while True:
            try:
                build_number = httpx.get(
                    f"https://discord.com/ios/{self.app_version}/manifest.json").json()["metadata"]["build"]
                break
            except:
                Output("bad").notime(f"Couldn't Find Build Number In Manifest Version {self.app_version} Since It Doesn't Exist")
                self.app_version = float(self.app_version)-1
                continue

        return build_number

    def get_app_version(self):
        body = httpx.get(
        "https://apps.apple.com/us/app/discord-chat-talk-hangout/id985746746",headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }).text

        return re.search(r'latest__version">Version (.*?)</p>', body).group(1)

    def get_darwin_version(self):
        darwin_wiki = httpx.get("https://en.wikipedia.org/wiki/Darwin_(operating_system)").text
        return re.search(r'Latest release.*?<td class="infobox-data">(.*?) /', darwin_wiki).group(1)

    @property
    def headers(self):
        return {
            "Host": "discord.com",
            "x-debug-options": "bugReporterEnabled",
            "Content-Type": "application/json",
            "Accept": "/",
            "User-Agent": self.user_agent,
            "Accept-Language": "sv-SE",
            "x-discord-locale": "en-US",
            "x-super-properties": self.x_super_properties,
        }

discord_props = Discord()
headers = discord_props.headers

class Client:
    def get_cookies(session):
        cookies = dict(
            session.get("https://discord.com").cookies
        )
        cookies["__cf_bm"] = (
            "0duPxpWahXQbsel5Mm.XDFj_eHeCKkMo.T6tkBzbIFU-1679837601-0-"
            "AbkAwOxGrGl9ZGuOeBGIq4Z+ss0Ob5thYOQuCcKzKPD2xvy4lrAxEuRAF1Kopx5muqAEh2kLBLuED6s8P0iUxfPo+IeQId4AS3ZX76SNC5F59QowBDtRNPCHYLR6+2bBFA=="
        )
        cookies["locale"] = "en-US"
        return cookies

    def get_session(token:str):
        iv1, iv2 = str(randint(15,16)), str(randint(1,5))
        session = tls_client.Session(
            client_identifier = f"safari_ios_{iv1}_{iv2}",
            random_tls_extension_order = True
        )  
        cookie = Client.get_cookies(session)
        session.headers = headers
        session.headers.update({"Authorization": token})
        session.headers.update({
            "cookie": f"__cfruid={cookie['__cfruid']}; __dcfduid={cookie['__dcfduid']}; __sdcfduid={cookie['__sdcfduid']}",
        })

        return session

class TokenFiller:
    def __init__(self, token) -> None:
        self.token = token
        self.session = Client.get_session(token)
        self.ws = websocket.WebSocket()
        self.ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        j = json.loads(self.ws.recv())
        heartbeat_interval = j['d']['heartbeat_interval']
        self.ws.send(json.dumps({"op": 2,"d": {"token": token,"properties": {"$os": "windows","$browser": "Discord","$device": "desktop"}}}))
        while True:
            try:
                r = json.loads(self.ws.recv())
                if r["t"] == "READY":
                    print("got sess id")
                    self.session_id = r["d"]["session_id"]
                break
            except Exception as e:
                self.session_id = secrets.token_hex(16)
                break
        
    def join_server(self, invite):
        r = self.session.post(f"https://discord.com/api/v9/invites/{invite}", json={
            "session_id": self.session_id
        })

        print(r.json())

        if r.status_code == 200:
            logger.joined(invite, self.token)
        else:
            if "captcha_key" in r.json():
                captcha = None
                while not captcha:
                    res = SOLVER.solve_hcaptcha(r.json()["captcha_sitekey"], "discord.com", rqdata=r.json()["captcha_rqdata"])
                    if res["success"]:
                        logger.captcha_solved(res["solution"], res["duration"])
                        captcha = res["solution"]
                
                self.session.headers["X-Captcha-Key"] = captcha
                self.session.headers["X-Captcha-Rqtoken"] = r.json()["captcha_rqtoken"]
                self.join_server(invite)
                self.session.headers.pop("X-Captcha-Key")
                self.session.headers.pop("X-Captcha-Rqtoken")
                    
            else:
                logger.log(colorama.Fore.RED, "error", code=r.status_code, text=r.text)

    def fill(self):
        self.join_server("aid")

TokenFiller("OTM5MjIxOTc5MTAwMjI5NjUy.Yf1suA.TKQ911rJX5HMN9LHxQv7NOh-plY").fill()