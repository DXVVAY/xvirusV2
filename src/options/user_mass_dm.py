from src import *

def send_message(token, channel_id, message):
    session = Client.get_session(token)
    result = session.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",json={'content': message})
    if result.status_code == 200:
        Output("good", token).log(f"Success {Fore.LIGHTBLACK_EX}->{Fore.GREEN} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code})")
    else:
        Output.error_logger(token, result.text, result.status_code)

def send(token, user_id, message, capkey, rqtoken):
    session = Client.get_session(token)

    if capkey != "":
        session.headers.update({"x-captcha-key":capkey})
        session.headers.update({"x-captcha-rqtoken":rqtoken})

    data = {
        "session_id": utility.rand_str(32),
        "recipients": [user_id],
    }
    
    result = session.post(f"https://discord.com/api/v9/users/@me/channels", json=data)
    if result.status_code == 200:
        Output("good", token).log(f"Opened DM -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
        if 'id' in result.json():
            channel_id = result.json()['id']
            send_message(token, channel_id, message) 
        return False, None, None, None
    elif result.text.startswith('{"captcha_key"'):
        Output("bad", token).log(f"Error -> {token} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
        use_captcha = config._get("use_captcha")
        if use_captcha is True:
            return True, result.json()["captcha_rqtoken"], result.json()["captcha_rqdata"], result.json()["captcha_sitekey"]
        else:
            return False, None, None, None
    else:
        Output.error_logger(token, result.text, result.status_code)
        return False, None, None, None

    return False

def dmer(user_id, message, token):
    retry, rqtoken, rqdata, sitekey = send(token, user_id, message, "","")
    if retry:
        cap = Captcha("https://discord.com", sitekey=sitekey, rqdata=rqdata)
        capkey = cap.solve()
        send(token, user_id, message, capkey, rqtoken)

def user_mass_dm():
    Output.set_title(f"User Mass DM")
    user_id = utility.ask("User ID")
    message = utility.ask("Message")
    max_threads = utility.asknum("Thread Count")
    use_captcha = config._get("use_captcha")
    if use_captcha is True:
        Captcha.get_captcha_bal()
    utility.run_threads(max_threads=max_threads, func=dmer, args=[user_id, message], delay=0)