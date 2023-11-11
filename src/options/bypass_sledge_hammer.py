from src import *

class get_ephermal_embed(websocket.WebSocketApp):
    def __init__(self, token, bot_id):
        self.packets_recv = 0
        self.message: dict = {}
        self.bot_id = str(bot_id)
        self.token = token
        self.open = False
        self.create_id = None

        self.socket_headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "User-Agent": discord_props.user_agent
        }
        super().__init__(
            "wss://gateway.discord.gg/?encoding=json&v=9",
            header = self.socket_headers,
            on_open = lambda ws: self.sock_open(ws),
            on_message = lambda ws, msg: self.sock_message(ws, msg)
        )
        
    def run(self) -> dict:
        self.run_forever()
        self.open = True

        return self.message
    
    def sock_open(self, ws):
        self.send(
            '{"op":2,"d":{"token":"'
            + self.token
            + '","capabilities":125,"properties":{"os":"Windows","browser":"Firefox","device":"","system_locale":"sv-SE","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0","browser_version":"94.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":103981,"client_event_source":null},"presence":{"status":"online","since":0,"activities":[],"afk":false},"compress":false,"client_state":{"guild_hashes":{},"highest_last_message_id":"0","read_state_version":0,"user_guild_settings_version":-1,"user_settings_version":-1}}}'
        )

    def sock_message(self, ws, message):
        decoded = json.loads(message)

        if "Verify yourself to gain access to the server" in str(decoded):
            self.message = decoded["d"]
            self.close()
        
    def sock_close(self, ws, close_code, close_msg):
        pass

class Sledgehammer():
    def __init__(self, token, guild_id, channel_id, message_id) -> None:
        self.session = Client.get_session(token)
        self.token=token
        self.bot_id = "863168632941969438"
        self.session_id = (''.join(random.sample(string.ascii_lowercase+string.digits,32)))
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id

    def get_captcha(self):
        g = get_ephermal_embed(self.token, self.bot_id)
        thread = threading.Thread(target=g.run)
        thread.start()

        self.start()

        while not g.open:
            time.sleep(1)

        thread.join()

        return g.message

    def submit(self, answer):
        self.session.post("https://discord.com/api/v9/interactions",json={
            "type": 3,
            "nonce": str(round(Decimal(time.time()*1000-1420070400000)*4194304)),
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "message_flags": 64,
            "message_id": self.message_id,
            "application_id": self.bot_id,
            "session_id": self.session_id,
            "data": {
                "component_type": 3,
                "custom_id": "verificationRequest.en",
                "type": 3,
                "values": [
                    answer
                ]
            }
        })

    def start(self):
        self.session.post("https://discord.com/api/v9/interactions",json={
            "type": 3,
            "nonce": str(round(Decimal(time.time()*1000-1420070400000)*4194304)),
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "message_flags": 0,
            "message_id": self.message_id,
            "application_id": self.bot_id,
            "session_id": self.session_id,
            "data": {
                "component_type": 2,
                "custom_id": "startVerification.en"
            }
        })

    def get_answer(self, embed):
        desc = embed["embeds"][0]["description"]
        object = (re.search(r'select the (.*?) on the',desc).group(1)[2:][:-2]).lower()

        if " " in object:
            words = object.split()
            object =''.join([words[0]]+[word.capitalize() for word in words[1:]])

        for option in embed["components"][0]["components"][0]["options"]:
            value = option["value"]

            if value == object:
                return value

    def verify(self):
        embed = self.get_captcha()
        answer = self.get_answer(embed)
        self.message_id = embed["id"]
        self.submit(answer)
        return answer

def send(guild_id, channel_id, message_id, token):
    sledgehammer = Sledgehammer(token=token, guild_id=guild_id, channel_id=channel_id, message_id=message_id)
    answer = sledgehammer.verify()
    Output("good", token).log(f"Success -> {token}{Fore.LIGHTBLACK_EX} (Answer Was {answer})")

def sledge_hammer():
    Output.set_title(f"Sledge Hammer Bypass")
    message = utility.message_info()
    guild_id = message["guild_id"]
    channel_id = message["channel_id"]
    message_id = message["message_id"]
    max_threads = utility.asknum("Thread Count")
    utility.run_threads(max_threads=max_threads, func=send, args=[guild_id, channel_id, message_id], delay=0)