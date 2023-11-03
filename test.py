import json, uuid, base64, httpx, random, tls_client, re
from random import randint as rd
from colorama import Fore

class Discord():
    def Mobile_xprops(self):
        u = uuid.uuid4().hex; vendor_uuid=f"{u[0:8]}-{u[8:12]}-{u[12:16]}-{u[16:20]}-{u[20:36]}"
        iphone_models=["11,2","11,4","11,6","11,8","12,1","12,3","12,5","12,8","13,1","13,2","13,3","13,4","14,2","14,3","14,4","14,5","14,6","14,7","14,8","15,2","15,3",]

        return base64.b64encode(json.dumps({
            "os":"iOS",
            "browser":"Discord iOS",
            "device":"iPhone"+random.choice(iphone_models),
            "system_locale":"sv-SE",
            "client_version":self._app_version,
            "release_channel":"stable",
            "device_vendor_id":vendor_uuid,
            "browser_user_agent":"",
            "browser_version":"",
            "os_version":self.iv1+"."+self.iv2,
            "client_build_number": self.build_number,
            "client_event_source":None,
            "design_id":0
        }).encode()).decode()
    
    def Get_build():
        body=httpx.get(
            "https://apps.apple.com/us/app/discord-chat-talk-hangout/id985746746",headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            }).text
        
        app_version=re.search(r'latest__version">Version (.*?)</p>', body).group(1)
        
        while True:
            try:
                build_number=httpx.get(
                    f"https://discord.com/ios/{app_version}/manifest.json").json()["metadata"]["build"]
                break

            except:
                print(f"{Fore.RED}discord hasnt added manifest for {app_version} fire")
                app_version=float(app_version)-1
                continue

        return {
            "build_number":int(build_number),
            "app_version": str(app_version)
        }

    def Get_darwin():
        darwin_wiki = httpx.get("https://en.wikipedia.org/wiki/Darwin_(operating_system)").text
        return re.search(r'Latest release.*?<td class="infobox-data">(.*?) /', darwin_wiki).group(1)

    def Get_session(self, token:str, use_proxy:bool=True):
        user_agent=f"Discord/{self.build_number} CFNetwork/1408.0.4 Darwin/{self._Dazeer__darwin_ver}"
        self.iv1,self.iv2=str(rd(15,16)), str(rd(1,5))

        session=tls_client.Session(
            client_identifier=f"safari_ios_{self.iv1}_{self.iv2}",
            random_tls_extension_order=True
        )

        session.headers={
            "Host": "discord.com",
            "x-debug-options": "bugReporterEnabled",
            "Content-Type": "application/json",
            "Accept": "/",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": user_agent,
            "Accept-Language": "sv-SE",
            "x-discord-locale": "sv-SE",
            "x-super-properties": Discord.Mobile_xprops(self),
            "Authorization": token
        }

        cookies=dict(session.get("https://discord.com").cookies)

        session.headers.update({
            "Cookie": f"__cfruid={cookies['__cfruid']}; __dcfduid={cookies['__dcfduid']}; __sdcfduid={cookies['__sdcfduid']}",
        })
        
        if use_proxy:
            if self.config["proxy"]["enabled"]:
                session.proxies=f"http://{random.choice(self.proxies)}"
                    
            session.timeout_seconds=self.config["proxy"]["max_timeout"]//1000

        return session