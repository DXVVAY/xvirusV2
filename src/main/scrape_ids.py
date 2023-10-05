import json
import os
import random
import threading
import time

import requests
import websocket
from colorama import Fore

from utils.util import *

folder_path = os.path.join(os.getenv('LOCALAPPDATA'), 'xvirus_config')
file = os.path.join(folder_path, 'xvirus_ids')
config = Config()

class WebSocket(websocket.WebSocketApp):
    
    def __init__(self, token, guild_id, channel_id):
        self.MAX_ITER = 10
        self.token = token
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.socket_headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "User-Agent": DiscordProps.user_agent,
        }
        super().__init__(
            "wss://gateway.discord.gg/?encoding=json&v=9",
            header=self.socket_headers,
            on_open=lambda ws: self.sock_open(ws),
            on_message=lambda ws, msg: self.sock_message(ws, msg),
            on_close=lambda ws, close_code, close_msg: self.sock_close(
                ws, close_code, close_msg
            ),
        )
        self.endScraping = False
        self.guilds = {}
        self.members: list[str] = []
        self.ranges = [[0]]
        self.lastRange = 0
        self.packets_recv = 0
        self.msgs = []
        self.d = 1
        self.iter = 0
        self.big_iter = 0
        self.finished = False

    def getRanges(self, index, multiplier, memberCount):
        initialNum = int(index * multiplier)
        rangesList = [[initialNum, initialNum + 99]]
        if memberCount > initialNum + 99:
            rangesList.append([initialNum + 100, initialNum + 199])
        if [0, 99] not in rangesList:
            rangesList.insert(0, [0, 99])
        return rangesList

    def parseGuildMemberListUpdate(self, response):
        memberdata = {
            "online_count": response["d"]["online_count"],
            "member_count": response["d"]["member_count"],
            "id": response["d"]["id"],
            "guild_id": response["d"]["guild_id"],
            "hoisted_roles": response["d"]["groups"],
            "types": [],
            "locations": [],
            "updates": [],
        }
        
        for chunk in response["d"]["ops"]:
            memberdata["types"].append(chunk["op"])
            if chunk["op"] in ("SYNC", "INVALIDATE"):
                memberdata["locations"].append(chunk["range"])
                if chunk["op"] == "SYNC":
                    memberdata["updates"].append(chunk["items"])
                else:
                    memberdata["updates"].append([])
            elif chunk["op"] in ("INSERT", "UPDATE", "DELETE"):
                memberdata["locations"].append(chunk["index"])
                if chunk["op"] == "DELETE":
                    memberdata["updates"].append([])
                else:
                    memberdata["updates"].append(chunk["item"])
        return memberdata

    def find_most_reoccuring(self, list):
        return max(set(list), key=list.count)

    def run(self) -> list[str]:
        try:
            self.run_forever()
            self.finished = True
            return self.members
        except Exception as e:
            print(e)
            pass

    def scrapeUsers(self):
        if self.endScraping == False:
            self.send(
                '{"op":14,"d":{"guild_id":"'
                + self.guild_id
                + '","typing":true,"activities":true,"threads":true,"channels":{"'
                + self.channel_id
                + '":'
                + json.dumps(self.ranges)
                + "}}}"
            )

    def sock_open(self, ws):
        self.send(
            '{"op":2,"d":{"token":"'
            + self.token
            + '","capabilities":125,"properties":{"os":"Windows","browser":"Firefox","device":"","system_locale":"it-IT","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0","browser_version":"94.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":103981,"client_event_source":null},"presence":{"status":"online","since":0,"activities":[],"afk":false},"compress":false,"client_state":{"guild_hashes":{},"highest_last_message_id":"0","read_state_version":0,"user_guild_settings_version":-1,"user_settings_version":-1}}}'
        )

    def heartbeatThread(self, interval):
        try:
            while True:
                self.send('{"op":1,"d":' + str(self.packets_recv) + "}")
                time.sleep(interval)
        except Exception as e:
            return

    def sock_message(self, ws, message):
        try:
            decoded = json.loads(message)
            if decoded is None:
                return
            if decoded["op"] != 11:
                self.packets_recv += 1
            if decoded["op"] == 10:
                threading.Thread(
                    target=self.heartbeatThread,
                    args=(decoded["d"]["heartbeat_interval"] / 1000,),
                    daemon=True,
                ).start()
            if decoded["t"] == "READY":
                for guild in decoded["d"]["guilds"]:
                    self.guilds[guild["id"]] = {"member_count": guild["member_count"]}
            if decoded["t"] == "READY_SUPPLEMENTAL":
                self.ranges = self.getRanges(
                    0, 100, self.guilds[self.guild_id]["member_count"]
                )
                self.scrapeUsers()
            elif decoded["t"] == "GUILD_MEMBER_LIST_UPDATE":
                parsed = self.parseGuildMemberListUpdate(decoded)
                self.msgs.append(len(self.members))
                print(f"{Fore.BLUE} <*> Scraped {Fore.RED}{len(self.members)}{Fore.BLUE} members", end="\r")
                if self.d == len(self.members):
                    self.iter += 1
                    if self.iter == self.MAX_ITER:
                        print(f"{Fore.BLUE} <*> Scraped {Fore.RED}{len(self.members)}{Fore.BLUE} members")
                        self.endScraping = True
                        self.close()
                        return
                self.d = self.find_most_reoccuring(self.msgs)
                if parsed["guild_id"] == self.guild_id and (
                    "SYNC" in parsed["types"] or "UPDATE" in parsed["types"]
                ):
                    for (elem, index) in enumerate(parsed["types"]):
                        if index == "SYNC":
                            for item in parsed["updates"]:
                                if len(item) > 0:
                                    for member in item:
                                        if "member" in member:
                                            mem = member["member"]
                                            obj = {
                                                "tag": mem["user"]["username"]
                                                + "#"
                                                + mem["user"]["discriminator"],
                                                "id": mem["user"]["id"],
                                            }
                                            if not mem["user"].get("bot"):
                                                self.members.append(str(mem["user"]["id"]))
                        elif index == "UPDATE":
                            for item in parsed["updates"][elem]:
                                if "member" in item:
                                    mem = item["member"]
                                    obj = {
                                        "tag": mem["user"]["username"]
                                        + "#"
                                        + mem["user"]["discriminator"],
                                        "id": mem["user"]["id"],
                                    }
                                    if not mem["user"].get("bot"):
                                        self.members.append(str(mem["user"]["id"]))
                        self.lastRange += 1
                        self.ranges = self.getRanges(
                            self.lastRange, 100, self.guilds[self.guild_id]["member_count"]
                        )
                        time.sleep(0.45)
                        self.scrapeUsers()
                if self.endScraping:
                    print(f"{Fore.BLUE} <*> Scraped {Fore.RED}{len(self.members)}{Fore.BLUE} members")
                    self.close()
        except Exception as e:
            print(e)

def reset_ids():
    if os.path.exists(file):
        os.remove(file)

def scrape_id(token, guild_id, channel_id):
        return WebSocket(token, guild_id, channel_id).run()

def id_scraper():
    reset_ids()
    guild_id = utility.ask("guild id")
    channel_id = utility.ask("channel id")
    
    token = TokenManager.OnlyToken(TokenManager.get_random_token())
    
    users = scrape_id(token, guild_id, channel_id)
    with open(file, "w") as f:
        for user in users:
            f.write(f"{user}\n")
        
    Output("info", config).notime(f"Scraped {len(users)} ids")