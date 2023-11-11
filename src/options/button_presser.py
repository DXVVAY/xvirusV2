from src import *

def click(guild_id, channel_id, message_id, custom_id, application_id, token):
    session = Client.get_session(token)
    data = {
        "application_id": str(application_id),
        "channel_id": str(channel_id),
        "data": {
            "component_type": 2,
            "custom_id": str(custom_id)
        },
        "guild_id": str(guild_id),
        "message_flags": 0,
        "message_id": str(message_id),
        "nonce": str(Decimal(time.time() * 1000 - 1420070400000) * 4194304).split(".")[0],
        'session_id': utility.rand_str(32),
        "type": 3,
    }
    session.headers.update({"referer": f"https://discord.com/channels/{guild_id}/{channel_id}"})
    result = session.post(f"https://discord.com/api/v9/interactions", json=data)
    if result.status_code == 204:
        Output("good", token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
    else:
        Output.error_logger(token, result.text, result.status_code)

def button_presser():
    Output.set_title(f"Button Presser")
    message = utility.message_info()
    guild_id = message["guild_id"]
    channel_id = message["channel_id"]
    message_id = message["message_id"]

    buttons = utility.get_buttons(
        token=TokenManager.get_random_token(),
        guild_id=guild_id,
        channel_id=channel_id,
        message_id=message_id
    )

    if buttons == None:
        Output("bad").notime("Invalid message and or message has no buttons")
        Output.PETC()

    print()
    for num, button in enumerate(buttons):
        label = button['label'].replace(' ', '') if button['label'] is not None else 'None'
        labels = f"    {Fore.BLUE}[{Fore.RED}{num}{Fore.BLUE}] {Fore.RED}{label}"
        print(labels)
    print()

    buttonnum = utility.ask("button number")
    for button in buttons:
        if buttons.index(button)==int(buttonnum):
            custom_id = button['custom_id']
            application_id = button['application_id']
            break

    max_threads = utility.asknum("Thread Count")
    utility.run_threads(max_threads=max_threads, func=click, args=[guild_id, channel_id, message_id, custom_id, application_id], delay=0)