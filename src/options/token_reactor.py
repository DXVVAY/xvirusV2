from src import *

def click(emoji, message_id, channel_id, token):
    session = Client.get_session(token)
    result = session.put(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/%40me?location=Message&burst=false")
    if result.status_code == 204:
        Output("good", token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
    else:
        Output.error_logger(token, result.text, result.status_code)

def token_reactor():
    Output.set_title(f"Message Reactor")
    message = utility.message_info()
    channel_id = message["channel_id"]
    message_id = message["message_id"]
    emojis = utility.get_reactions(channel_id, message_id)

    if emojis == None:
        Output("bad").notime("Invalid message and or message has no reacts")
        Output.PETC()

    print()
    for num, emoji in enumerate(emojis):
        name = emoji['name'].replace(' ', '')
        labels = f"    {Fore.BLUE}[{Fore.RED}{num}{Fore.BLUE}] {Fore.RED}{name}"
        print(labels)
    print()

    emojinum = utility.ask("Emoji number")
    for emoji in emojis:
        if emojis.index(emoji)==int(emojinum):
            emoji = emoji['name'].replace(" ", "")
            break
    
    max_threads = utility.asknum("Thread Count")
    utility.run_threads(max_threads=max_threads, func=click, args=[emoji.replace(":", "%3A"), message_id, channel_id], delay=0)