from src import *

def send(guild_id, vc_id, token):
    ws = WebSocket()
    ws.connect("wss://gateway.discord.gg/?v=8&encoding=json")
    hello = json.loads(ws.recv())
    ws.send(json.dumps({"op": 2,"d": {"token": token,"properties": {"$os": "windows","$browser": "Discord","$device": "desktop"}}}))
    ws.send(json.dumps({"op": 4,"d": {"guild_id": guild_id,"channel_id": vc_id,"self_mute": False,"self_deaf": False, "self_stream?": False, "self_video": False}}))
    ws.send(json.dumps({"op": 18,"d": {"type": "guild","guild_id": guild_id,"channel_id": vc_id,"preferred_region": "singapore"}}))
    ws.send(json.dumps({"op": 1,"d": None}))
    while True:
        ws.recv()
        time.sleep(hello.get("d").get("heartbeat_interval") / 1000)

def token_vc_joiner():
    Output.set_title("Vc Joiner")
    guild_id = utility.ask("Guild ID")
    vc_id = utility.ask("VC ID")
    max_threads = utility.asknum("Thread Count")

    utility.run_threads(max_threads=max_threads, func=send, args=[guild_id, vc_id], delay=0)