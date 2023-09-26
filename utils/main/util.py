import base64
import json
import os
import random
import re
import sys
import time
import types
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import httpx
import requests
from colorama import Fore
from capmonster_python import capmonster, HCaptchaTask
import tls_client

from utils import *


class Output:
    def __init__(self, level, config, token=None):
        self.level = level
        self.config = config
        self.token = token
        self.color_map = {
            "info": (Fore.BLUE, "<~>"),
            "bad": (Fore.RED, "<!>"),
            "good": (Fore.GREEN, "<*>")
        }

    def should_hide(self):
        return not self.config._get('debug_mode', True)

    def hide_token(self, text):
        if self.should_hide() and self.token:
            token_length = len(self.token)
            if token_length >= 10:
                censored_part = '*' * 10
                text = text.replace(self.token[-10:], censored_part)
        return text

    def notime(self, *args, **kwargs):
        color, text = self.color_map.get(self.level, (Fore.LIGHTWHITE_EX, self.level))
        time_now = datetime.now().strftime("%H:%M:%S")

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
        config = Config()
        Output("info", config).notime(f"Press ENTER to continue")
        input()
    
    def SetTitle(_str):
        text = str(requests.get("https://cloud.xvirus.lol/title.txt").text)
        system = os.name
        if system == 'nt':
            ctypes.windll.kernel32.SetConsoleTitleW(f"{_str} - {text}")
        else:
            pass

class Config:
    def __init__(self):
        self.folder_path = os.path.join(os.getenv('LOCALAPPDATA'), 'xvirus_config')
        os.makedirs(self.folder_path, exist_ok=True)
        self.config_file = os.path.join(self.folder_path, 'config.json')
        self.config_data = self._load('config.json')

        for file_name in ['xvirus_tokens', 'xvirus_proxies', 'xvirus_usernames', 'xvirus_ids']:
            file_path = os.path.join(self.folder_path, file_name)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    pass

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
    
    def _reset(self):
        self.config_data = {}
        self._save('config.json', self.config_data)

    def add(self, file_name, data):
        if file_name not in ['xvirus_tokens', 'xvirus_proxies', 'xvirus_usernames', 'xvirus_ids']:
            raise ValueError(f"Error: {file_name} is not a valid file name.")
        
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, 'a') as file:
            file.write(data + '\n')

    def read(self, file_name):
        if file_name not in ['xvirus_tokens', 'xvirus_proxies', 'xvirus_usernames', 'xvirus_ids']:
            raise ValueError(f"Error: {file_name} is not a valid file name.")
        
        file_path = os.path.join(self.folder_path, file_name)
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: {file_name} not found.")
    
class DiscordProps:
    @staticmethod
    def get_build_number():
        scripts = re.compile(r'/assets/.{20}.js', re.I).findall(requests.get("https://discord.com/app", headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; NiggaOs x16; rv:109.0) Gecko/20100101 Niggafox/114.0'}).text)
        scripts.reverse()
        for v in scripts:
            content = requests.get(f"https://discord.com{v}", headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; NiggaOs x16; rv:109.0) Gecko/20100101 Niggafox/114.0'}).content.decode()
            if content.find("build_number:\"") != -1:
                return re.compile(r"build_number:\"(.*?)\"", re.I).findall(content)[0]

    user_agents = [
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    ]

    user_agent = random.choice(user_agents)
    buildNumber = get_build_number()

    _get_mobile_x_super_properties = base64.b64encode(json.dumps({
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": user_agent,
            "browser_version": random.randint(110, 116), 
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": buildNumber,
            "client_event_source": None,
            "design_id": 0}).encode()).decode()
    
    default_headers = {}

class Header:
    @staticmethod
    def x_content_props(guild):
        guild_id = guild["guild"]["id"]
        channel_id = guild["channel"]["id"]
        location_data = {
            "location": "Join Guild",
            "location_guild_id": guild_id,
            "location_channel_id": channel_id,
            "location_channel_type": 0
        }
        location_json = json.dumps(location_data)
        return base64.b64encode(location_json.encode()).decode()

    @staticmethod
    def tls_session() -> tls_client.Session:
        client = tls_client.Session(
            client_identifier=f"chrome_{random.randint(110, 116)}",
            random_tls_extension_order=True,
            ja3_string="771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,10-23-27-43-13-65281-16-5-45-18-0-11-35-17513-51-21-41,29-23-24,0",
            h2_settings={
                "HEADER_TABLE_SIZE": 65536,
                "MAX_CONCURRENT_STREAMS": 1000,
                "MAX_HEADER_LIST_SIZE": 262144,
                "INITIAL_WINDOW_SIZE": 6291456     
            },
            h2_settings_order=[
                "HEADER_TABLE_SIZE",
                "MAX_CONCURRENT_STREAMS",
                "INITIAL_WINDOW_SIZE",
                "MAX_HEADER_LIST_SIZE"
            ],
            supported_signature_algorithms=[
                "PKCS1WithSHA384",
                "PSSWithSHA512",
                "PKCS1WithSHA512",
                "ECDSAWithP256AndSHA256",
                "PSSWithSHA256",
                "PKCS1WithSHA256",
                "ECDSAWithP384AndSHA384",
                "PSSWithSHA384",
            ],
            supported_versions=["GREASE", "1.3", "1.2"],
            key_share_curves=["GREASE", "X25519"],
            cert_compression_algo="brotli",
            pseudo_header_order=[":method", ":authority", ":scheme", ":path"],
            connection_flow=15663105,
            header_order=["accept", "user-agent", "accept-encoding", "accept-language"]
        )
        return client

    @staticmethod
    def get_cookies(session, headers):
        cookies = dict(
            session.get("https://discord.com", headers=headers).cookies
        )

        cookies["__cf_bm"] = (
            "0duPxpWahXQbsel5Mm.XDFj_eHeCKkMo.T6tkBzbIFU-1679837601-0-"
            "AbkAwOxGrGl9ZGuOeBGIq4Z+ss0Ob5thYOQuCcKzKPD2xvy4lrAxEuRAF1Kopx5muqAEh2kLBLuED6s8P0iUxfPo+IeQId4AS3ZX76SNC5F59QowBDtRNPCHYLR6+2bBFA=="
        )
        cookies["locale"] = "en-US"

        return cookies

    @staticmethod
    def get_client(token):
        default_headers = DiscordProps.default_headers.copy()
        default_headers["authorization"] = token

        session = Header.tls_session()
        cookie = Header.get_cookies(session, headers=default_headers)
    
        default_headers["cookie"] = (
            f'__dcfduid={cookie["__dcfduid"]}; '
            f'__sdcfduid={cookie["__sdcfduid"]}; '
            f'__cfruid={cookie["__cfruid"]}; '
            f'__cf_bm={cookie["__cf_bm"]}; '
            f'locale={cookie["locale"]}'
        )
    
        return session, default_headers, cookie

class TokenManager:
    @classmethod
    def get_tokens(cls):
        config = Config()
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
            Output("bad", config).notime(f"File not found: {custom_path}")
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

class utility:
    def threads(func, args=[], delay=0, thread_amount=None, return_home=True, text=""):
        config = Config()
        try:
            tokens = TokenManager.get_tokens()
            maxine = thread_amount
            
            if thread_amount is None:
                thread_amount = utility.ask(f"Amount Of Threads")
                try:
                    thread_amount = int(thread_amount)
                except ValueError:
                    pass
                
                if not thread_amount:
                    thread_amount = len(tokens)
                
                if thread_amount > len(tokens):
                    thread_amount = len(tokens)
            
            if tokens:
                try:
                    with ThreadPoolExecutor(max_workers=int(thread_amount)) as executor:
                        for token in tokens:
                            try:
                                token = TokenManager.OnlyToken(token)
                                args.append(token)
                                executor.submit(func, *args)
                                args.remove(token)
                                time.sleep(delay)
                                    
                            except Exception as e:
                                Output("error", config).log(f"{Fore.RED}Error: {e}")
                    
                    if maxine is not None:
                        name = " ".join([name.capitalize() for name in func.__name__.split('_')])
                        if return_home:
                            Output.PETC()
                    
                    time.sleep(5)
                    
                    if return_home:
                        Output.PETC()
                except Exception as e:
                    Output("error", config).log(f"{Fore.RED}Error: {e}")
                    if return_home:
                        Output.PETC()
            else:
                Output("error", config).notime(f"No tokens were found in the cache")
                if return_home:
                    Output.PETC()
        except Exception as e:
            Output("error", config).notime(f"{Fore.RED}ERROR: {e}")
            if return_home:
                Output.PETC()
    
    def get_guild(invite):
        try:
            result = requests.get(f"https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true")
            data = result.json()
            if "Unknown Invite" in data.get("message"):
                return None
            return data
        except:
            return None

    def ask(text: str = ""):
        ask = input(f"{Fore.RED}<~> {text}: {Fore.BLUE}")
        return ask
    
    def asknum(num: int = ""):
        ask = input(f"{Fore.RED}<~> {num}: {Fore.BLUE}")
        return ask
    
    def getCapBal():
        config = Config()
        key = config._get("captcha_key")
        get_balance_resp = httpx.post(f"https://api.capmonster.cloud/getBalance", json={"clientKey": key}).text
        bal = json.loads(get_balance_resp)["balance"]
        balance = f"${bal}"
        return balance

class Captcha:
    def solve(url, sitekey, data = None):
            config = Config()
            captchaKey = config._get("captcha_key")
            cap = HCaptchaTask(captchaKey)
            cap.set_user_agent(f"Discord-Android/{DiscordProps.buildNumber};RNA")
            task = cap.create_task(
                website_url=url, 
                website_key=sitekey, 
                custom_data=data,
            )
            result = cap.join_task_result(task)
            return result.get("gRecaptchaResponse")