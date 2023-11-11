from src import *

def bypass(guild_id, bot_id, token):
    session = Client.get_session(token)
    query = {
        "client_id":{bot_id},
        "response_type":"code",
        "redirect_uri": "https://restorecord.com/api/callback",
        "scope":"identify guilds.join",
        "state":{guild_id}
    }
    auth = session.post(f"https://discord.com/api/v9/oauth2/authorize", params=query, json={"permissions":"0","authorize":True})
    if "location" in auth.text:
        answer = auth.json()["location"]
        result = session.get(answer, allow_redirects=True)
        if result.status_code in [307, 403, 200]:
            Output("good", token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
        else:
            Output.error_logger(token, result.text, result.status_code)
    else:
        Output.error_logger(token, auth.text, auth.status_code)

def restorecord_bypass():
    Output.set_title(f"RestoreCord Bypass")
    guild_id = utility.ask("Guild ID")
    bot_id = utility.ask("Bot ID")
    max_threads = utility.asknum("Thread Count")
    utility.run_threads(max_threads=max_threads, func=bypass, args=[guild_id, bot_id], delay=0)