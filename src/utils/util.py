from capmonster_python import HCaptchaTask, capmonster
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from websocket import WebSocket
from json import dumps, loads
from decimal import Decimal
from random import randint
from colorama import Fore
from time import sleep
from src import *
import tls_client
import subprocess
import webbrowser
import threading
import websocket
import requests
import psutil
import decimal
import getpass
import pystyle
import string
import base64
import ctypes
import random
import typing
import httpx
import json
import time
import uuid
import sys
import os
import re

THIS_VERSION = "2.0.0"
whitelisted = ["1157603083308761118", "1157425827517055017", "1146496916419526727", "1157400926877925558", "1156946611646247013", "1149731357656883311", "322415832275615746"]

class Config:
    def __init__(self):
        self.folder_path = os.path.join(os.getenv('LOCALAPPDATA'), 'xvirus_config')
        self.file = os.path.join(self.folder_path, 'config.json')
        os.makedirs(self.folder_path, exist_ok=True)
        self.xvirus_files = ['xvirus_tokens', 'xvirus_proxies', 'xvirus_usernames', 'xvirus_ids']
        for file_name in self.xvirus_files:
            file_path = os.path.join(self.folder_path, file_name)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    pass
        self.content = {
            "xvirus_key": "",
            "use_proxies": False,
            "use_captcha": False,
            "captcha_key": "",
            "captcha_typ": "",
            "debug_mode": False
        }
        if not os.path.exists(self.file):
            with open(self.file, 'w') as f:
                json.dump(self.content, f, indent=3)
        else:
            pass
        self.config_data = self._load('config.json')

    def _load(self, file_name):
        file_path = os.path.join(self.folder_path, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            return {}

    def _save(self, file_name, data):
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def _set(self, key, value):
        self.config_data[key] = value
        self._save('config.json', self.config_data)

    def _get(self, key, default=None):
        return self.config_data.get(key, default) if default is not None else self.config_data.get(key)

    def _remove(self, key):
        if key in self.config_data:
            del self.config_data[key]
            self._save('config.json', self.config_data)

    def add(self, file_name, data):
        if file_name not in self.xvirus_files:
            raise ValueError(f"Error: {file_name} is not a valid file name.")
        
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, 'a') as file:
            file.write(data + '\n')

    def read(self, file_name):
        if file_name not in self.xvirus_files:
            raise ValueError(f"Error: {file_name} is not a valid file name.")
        
        file_path = os.path.join(self.folder_path, file_name)
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: {file_name} not found.")
    
    def reset(self, file_name):
        if file_name not in self.xvirus_files:
            raise ValueError(f"Error: {file_name} is not a valid file name.")
        
        file_path = os.path.join(self.folder_path, file_name)
        try:
            with open(file_path, 'w') as file:
                pass
        except Exception as e:
            print(f"{e}")

config = Config()

class Output:
    def __init__(self, level, token=None):
        self.level = level
        self.token = token
        self.color_map = {
            "info": (Fore.BLUE, "<*>"),
            "bad": (Fore.RED, "<!>"),
            "good": (Fore.GREEN, "<+>"),
            "cap": (Fore.CYAN, "<CAP>"),
            "dbg": (Fore.MAGENTA, "<DEBUG>"),
        }

    def should_hide(self):
        return not config._get('debug_mode', True)

    def hide_token(self, text):
        if self.should_hide() and self.token:
            token_length = len(self.token)
            if token_length >= 10:
                censored_part = '*' * 10
                text = text.replace(self.token[-10:], censored_part)
        return text

    def notime(self, *args, **kwargs):
        color, text = self.color_map.get(self.level, (Fore.LIGHTWHITE_EX, self.level))
        base = f"{color}{text.upper()}"
        for arg in args:
            arg = self.hide_token(arg)
            base += f" {arg}"
        if kwargs:
            for key, value in kwargs.items():
                value = self.hide_token(value)
                base += f" {key}={value}"
        print(base)

    def log(self, *args, **kwargs):
        color, text = self.color_map.get(self.level, (Fore.LIGHTWHITE_EX, self.level))
        time_now = datetime.now().strftime("%H:%M:%S")
        base = f"{Fore.RED}│{Fore.BLUE}{time_now}{Fore.RED}│ {color}{text.upper()}"
        updated_args = []

        for arg in args:
            arg = self.hide_token(arg)
            updated_args.append(arg)

        for arg in updated_args:
            base += f" {arg}"

        if kwargs:
            for key, value in kwargs.items():
                value = self.hide_token(value)
                base += f" {key}={value}"
        print(base)

    @staticmethod
    def PETC():
        Output("info").notime(f"Press ENTER to continue")
        input()
        __import__("main").gui.main_menu()
    
    @staticmethod
    def set_title(text):
        system = os.name
        if system == 'nt':
            ctypes.windll.kernel32.SetConsoleTitleW(f"{text} - Discord API Tool | https://xvirus.lol | Made By Xvirus™")
        else:
            pass
    
    @staticmethod
    def web_text():
        r = requests.get("https://cloud.xvirus.lol/webtext.txt")
        text = r.text.strip()
        print(f"{Fore.RED}Text Of The Week:\n {Fore.BLUE}{text}")
        sleep(2.5)

    @staticmethod
    def error_logger(token, res_text, res_status_code):
        if res_text.startswith('{"captcha_key"'):
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}(Captcha)")
        elif res_text.startswith('{"message": "401: Unauthorized'):
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}(Unauthorized)")
        elif "Cloudflare" in res_text:
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}(CloudFlare Blocked)")
        elif "\"code\": 40007" in res_text:
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}(Token Banned)")
        elif "\"code\": 40002" in res_text:
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}(Locked Token)")
        elif "\"code\": 10006" in res_text:
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}(Invalid Invite)")
        elif "\"code\": 10004" in res_text:
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}(Not In Server)")
        elif "\"code\": 50013:" or "\"code\": 50001:" in res_text:
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}(No Access)")
        else:
            Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({res_status_code}) {Fore.RED}({res_text})")

class Discord:
    def __init__(self):
        Output.set_title("Getting Discord Info")
        os.system('cls')
        self.build_number = None
        self.darwin_ver = self.get_darwin_version()
        self.iv1, self.iv2 = str(randint(15, 16)), str(randint(1, 5))
        self.app_version = self.get_app_version()
        Output("info").notime("Getting Discord Info..")
        sleep(0.2)
        self.build_number = self.get_build_number()
        self.user_agent = f"Discord/{self.build_number} CFNetwork/1402.0.8 Darwin/{self.darwin_ver}"
        Output("info").notime(f"Build Number: {Fore.RED}{self.build_number}")
        sleep(0.2)
        Output("info").notime(f"Darwin Version: {Fore.RED}{self.darwin_ver}")
        sleep(0.2)
        Output("info").notime(f"Discord App Version: {Fore.RED}{self.app_version}")
        sleep(0.2)
        Output("info").notime(f"User Agent: {Fore.RED}{self.user_agent}")
        sleep(0.5)
        Output("info").notime("Successfully Built Headers.")
        sleep(1)
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
static_headers = {
    'authority': 'discord.com',
    'accept': '*/*',
    'accept-language': 'sv,sv-SE;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://discord.com',
    'referer': 'https://discord.com/',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9016 Chrome/108.0.5359.215 Electron/22.3.12 Safari/537.36',
    'x-debug-options': 'bugReporterEnabled',
    'x-discord-locale': 'sv-SE',
    'x-discord-timezone': 'Europe/Stockholm',
    'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDE2Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6InN2IiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMTYgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMTIgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMTIiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyMTg2MDQsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM1MjM2LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',}

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
        
        if config._get("use_proxies"):
            proxy = ProxyManager.clean_proxy(ProxyManager.random_proxy())
            if isinstance(proxy, str):
                proxy_dict = {
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}"
                }
            elif isinstance(proxy, dict):
                proxy_dict = proxy

            session.proxies = proxy_dict

        return session

    def get_simple_session() -> tls_client.Session:
        client = tls_client.Session(
            client_identifier=f"chrome_{random.randint(110, 116)}",
            random_tls_extension_order=True
        )   
        if config._get("use_proxies"):
            proxy = ProxyManager.clean_proxy(ProxyManager.random_proxy())
            if isinstance(proxy, str):
                proxy_dict = {
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}"
                }
            elif isinstance(proxy, dict):
                proxy_dict = proxy
            client.proxies = proxy_dict

        return client

class ProxyManager:
    def get_proxies():
        f = config.read('xvirus_proxies')
        proxies = f.strip().splitlines()
        proxies = [proxy for proxy in proxies if proxy not in [" ", "", "\n"]]
        return proxies
        
    def random_proxy():
        try:
            return random.choice(ProxyManager.get_proxies())
        except:
            return {}

    def clean_proxy(proxy):
        if isinstance(proxy, str):
            parts = proxy.split(':')
            if '@' in proxy or len(parts) == 2:
                return proxy
            elif len(parts) == 4:
                return f'{parts[2:]}@{parts[:2]}'
            elif '.' in parts[0]:
                return f'{parts[2:]}@{parts[:2]}'
            else:
                return f'{parts[:2]}@{parts[2:]}'
        elif isinstance(proxy, dict):
            http_proxy = proxy.get("http") or proxy.get("https")
            https_proxy = proxy.get("https") or proxy.get("http")
            if http_proxy or https_proxy:
                return {
                    "http://": http_proxy,
                    "https://": https_proxy
                }
            elif proxy in [dict(), {}]:
                return {}
        return proxy

class TokenManager:
    @classmethod
    def get_tokens(cls):
        f = config.read('xvirus_tokens')
        tokens = f.strip().splitlines()
        tokens = [token for token in tokens if token not in [" ", "", "\n"]]
        return tokens
    
    @classmethod
    def custom_path(cls, custom_path):
        try:
            with open(custom_path, 'r') as file:
                tokens = file.read().strip().splitlines()
                tokens = [token for token in tokens if token.strip()]
                return tokens
        except FileNotFoundError:
            Output("bad").notime(f"File not found: {custom_path}")
            return None

    @staticmethod
    def OnlyToken(tokenn):
        r = re.compile(r"(.+):(.+):(.+)")
        if r.match(tokenn):
            return tokenn.split(":")[2]
        else:
            token = tokenn
        return token
    
    @classmethod
    def delete_token(cls, token):
        f = Config.read('xvirus_tokens')
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if token not in line:
                f.write(line)
        f.truncate()
    
    @classmethod
    def get_random_token(cls):
        tokens = cls.get_tokens()
        if tokens:
            return random.choice(tokens)
        else:
            return None

class utility:
    def rand_str(length:int) -> str:
        return ''.join(random.sample(string.ascii_lowercase+string.digits, length))
    
    def ask(text: str = ""):
        ask = input(f"{Fore.RED}<~> {text}: {Fore.BLUE}")
        if ask in whitelisted:
            Output("bad").notime(f"Answer Whitelisted! Press enter to continue...")
            input()
            __import__("main").gui.main_menu()
        elif ask == "back":
            Output("info").notime(f"Going Back...")
            sleep(2)
            __import__("main").gui.main_menu()
        return ask
    
    def asknum(num = ""):
        ask = input(f"{Fore.RED}<~> {num}: {Fore.BLUE}")
        if ask == "back":
            Output("info").notime(f"Going Back...")
            __import__("main").gui.main_menu()
        return ask
    
    def get_random_id(id):
        folder_path = os.path.join(os.getenv('LOCALAPPDATA'), 'xvirus_config')
        file = os.path.join(folder_path, 'xvirus_ids')
        with open(file, "r", encoding="utf8") as f:
            users = [line.strip() for line in f.readlines()]
        randomid = random.sample(users, id)
        return "<@" + "> <@".join(randomid) + ">"
    
    def get_ids():
        f = config.read('xvirus_ids')
        ids = f.strip().splitlines()
        ids = [idd for idd in ids if idd not in [" ", "", "\n"]]
        return ids
    
    def get_usernames():
        f = config.read('xvirus_usernames')
        users = f.strip().splitlines()
        users = [user for user in users if user not in [" ", "", "\n"]]
        return users
    
    def clear():
        system = os.name
        if system == 'nt':
            os.system('cls')
        else:
            print('\n'*120)
        return

    def message_info(message_link = None):
        if message_link is None:
            message_link = utility.ask("Message link")
        pattern = re.compile(r"^https:\/\/(ptb\.|canary\.)?discord\.com\/channels\/\d+\/\d+\/\d+$")
        if pattern.match(message_link):
            link_parts = message_link.split("/")
            guild_id, channel_id, message_id = link_parts[4], link_parts[5], link_parts[6]
            return {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "message_id": message_id
            }
        else:
            Output("bad").notime("Invalid message link")
            return None

    def get_message(token, channel_id, message_id, session=None, headers=None, cookie=None):
        if session is None or headers is None or cookie is None:
            session = Client.get_session(token)
        try:
            response = session.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1&around={message_id}").json()
            return response[0]
        except Exception as e:
            return {"code": 10008}

    def get_buttons(token, guild_id, channel_id, message_id, session=None, headers=None, cookie=None):
        try:
            message = utility.get_message(token, str(channel_id), str(message_id), session, headers, cookie)

            if message.get("code") == 10008 or len(message.get("components", [])) == 0:
                return None

            buttons = []
            for component in message["components"]:
                for button in component.get("components", []):
                    buttons.append({
                        "label": button.get("label"),
                        "custom_id": button["custom_id"],
                        "application_id": message["author"]["id"],
                    })

            return buttons
        except Exception as e:
            Output("bad").notime(f"{e}")
            return None
    
    def get_reactions(channel_id, message_id, iteration=0):
        if iteration > 5:
            return None

        try:
            token = TokenManager.get_random_token()
            message = utility.get_message(token=token, channel_id=channel_id, message_id=message_id)
            if message.get("code") == 10008:
                return utility.get_reactions(channel_id, message_id, iteration=iteration+1)
            emojis = []
            reactions = message.get("reactions", [])

            if not reactions:
                return None

            for reaction in reactions:
                emoji = reaction["emoji"]
                emoji_name = emoji["name"]
                emoji_id = emoji["id"]

                if emoji_id is None:
                    custom = False
                    emoji_name_with_id = emoji_name
                else:
                    custom = True
                    emoji_name_with_id = f"{emoji_name}:{emoji_id}"

                emojis.append({
                    "name": emoji_name_with_id,
                    "count": reaction["count"],
                    "custom": custom
                })
            return emojis
        except Exception as e:
            Output("bad").notime(f"{e}")
            return None

    def CheckWebhook(webhook):
        try:
            response = requests.get(webhook)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            Output("bad").notime(f"Invalid Webhook.")
            sleep(1)
            Output.PETC()
    
        try:
            json_data = response.json()
            j = json_data["name"]
            Output("info").notime(f"Valid webhook! {Fore.RED}({j})")
        except (KeyError, json.decoder.JSONDecodeError):
            Output("bad").notime(f"Invalid Webhook.")
            sleep(1)
    
    def make_menu(*options):
        print()
        for num, option in enumerate(options, start=1):
            label = f"    {Fore.BLUE}[{Fore.RED}{num}{Fore.BLUE}] {Fore.RED}{option}"
            print(label)
        print()

    def get_session_id():
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        j = json.loads(ws.recv())
        heartbeat_interval = j['d']['heartbeat_interval']
        ws.send(json.dumps({"op": 2,"d": {"token": token,"properties": {"$os": "windows","$browser": "Discord","$device": "desktop"}}}))
        while True:
            try:
                r = json.loads(ws.recv())
                if r["t"] == "READY":
                    print("got sess id")
                    return r["d"]["session_id"]
                break
            except Exception as e:
                return utility.rand_str(32)
                break

class Captcha:
    def payload(self, proxy:str=None, rqdata:str=None) -> None:
        captchaKey = config._get("captcha_key")
        p = {
            "clientKey":captchaKey,
            "task": {
                "websiteURL":"https://discord.com/",
                "websiteKey":"a9b5fb07-92ff-493f-86fe-352a2803b3df",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "enterprisePayload":{
                    "rqdata": rqdata,
                }
            }
        }
        p['appId']="E68E89B1-C5EB-49FE-A57B-FBE32E34A2B4"
        p['task']['type'] = "HCaptchaTurboTask"
        p['task']['proxy'] = proxy 
        return p


    def __init__(self, proxy:str, siteKey:str, siteUrl:str, rqdata:str) -> None:
        self.debug = False
        self.proxy = proxy
        self.siteKey = siteKey
        self.siteUrl = siteUrl
        self.rqdata = rqdata

    def solveCaptcha(self) -> str:
        captchaKey = config._get("captcha_key")
        captchaType = config._get("captcha_typ")
        if captchaType == "capsolver":
            r = requests.post(f"https://api.capsolver.com/createTask",json=self.payload(self.proxy, self.rqdata))
            try:
                if r.json().get("taskId"):
                    taskid = r.json()["taskId"]
                else:
                    return None
            except:
                Output("bad").log("Couldn't get task id.",r.text)
                return None
            while True:
                try:
                    r = requests.post(f"https://api.capsolver.com/getTaskResult",json={"clientKey":captchaKey,"taskId":taskid})
                    if r.json()["status"] == "ready":
                        key = r.json()["solution"]["gRecaptchaResponse"]
                        return key
                    elif r.json()['status'] == "failed":
                        return None
                except:
                    Output("bad").log("Failed to get status.",r.text)
                    return None
        elif captchaType == "capmonster":
            capmonster = HCaptchaTask(captchaKey)
            capmonster.set_user_agent(f"Discord-Android/{DiscordProps.buildNumber};RNA")
            task_id = capmonster.create_task(
                website_url=self.siteUrl, 
                website_key=self.siteKey, 
                custom_data=self.rqdata,
            )
            result = capmonster.join_task_result(task_id)
            return result.get("gRecaptchaResponse")
        else:
            utility.make_menu("Capsolver", "Capmonster")
            choice = utility.ask('Choice')
            if choice == "1":
                config._set("captcha_typ", "capsolver")
                Output("info").notime(f"Using {Fore.RED}Capsolver")
                sleep(1)
            elif choice == "2":
                config._set("captcha_typ", "capmonster")
                Output("info").notime(f"Using {Fore.RED}Capmonster")
                sleep(1)

    def getCapBal():
        captchaKey = config._get("captcha_key")
        captchaType = config._get("captcha_typ")
        if captchaType == "capsolver":
            get_balance_resp = httpx.post(f"https://api.capsolver.com/getBalance", json={"clientKey": captchaKey}).text
            bal = json.loads(get_balance_resp)["balance"]
            Output("info").notime(f"Captcha Balance: ${bal}")
        elif captchaType == "capmonster":
            get_balance_resp = httpx.post(f"https://api.capmonster.cloud/getBalance", json={"clientKey": captchaKey}).text
            bal = json.loads(get_balance_resp)["balance"]
            Output("info").notime(f"Captcha Balance: ${bal}")
