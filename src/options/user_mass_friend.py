from src import *

def send(token, username, capkey, rqtoken):
    session = Client.get_session(token)

    if capkey != "":
        session.headers.update({"x-captcha-key":capkey})
        session.headers.update({"x-captcha-rqtoken":rqtoken})

    data = {
        "session_id": utility.rand_str(32),
        "username": username,
    }

    result = session.post(f"https://discord.com/api/v9/users/@me/relationships", json=data)
    if result.status_code == 204:
        Output("good", token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
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

def frineder(username, token):
    retry, rqtoken, rqdata, sitekey = send(token, username, "","")
    if retry:
        cap = Captcha("https://discord.com", sitekey=sitekey, rqdata=rqdata)
        capkey = cap.solve()
        send(token, username, capkey, rqtoken)

def user_mass_friend():
    Output.set_title(f"User Mass Friend")
    username = utility.ask("Username")
    max_threads = utility.asknum("Thread Count")

    utility.run_threads(max_threads=max_threads, func=frineder, args=[username], delay=0)
    use_captcha = config._get("use_captcha")
    if use_captcha is True:
        get_captcha_bal()