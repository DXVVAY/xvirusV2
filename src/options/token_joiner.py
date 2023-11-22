from src import *

def join(token, invite, capkey, rqtoken):
    session = Client.get_session(token)

    if capkey != "":
        session.headers.update({"x-captcha-key":capkey})
        session.headers.update({"x-captcha-rqtoken":rqtoken})

    result = session.post(f"https://discord.com/api/v9/invites/{invite}", json={"session_id": utility.rand_str(32)})
    if result.status_code == 200:
        if capkey == "":
            Output("good", token).log(f"Joined {Fore.LIGHTBLACK_EX}{invite} {Fore.GREEN}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            return False, None, None, None
        else:
            Output("good", token).log(f"Joined {Fore.LIGHTBLACK_EX}With Cptcha {Fore.GREEN}-> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
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


def joiner(invite, token):
    retry, rqtoken, rqdata, sitekey = join(token, invite, "","")
    if retry:
        cap = Captcha("https://discord.com", sitekey=sitekey, rqdata=rqdata)
        capkey = cap.solve()
        join(token, invite, capkey, rqtoken)

def token_joiner():
    Output.set_title(f"Token Joiner")
    invite = utility.ask("Invite")
    invite = invite.split("/")[-1]
    max_threads = utility.asknum("Thread Count")

    server_name = utility.get_server_name(invite)
    if server_name is not None:
        Output("info").notime(f"Joining {Fore.RED}{server_name}")
    use_captcha = config._get("use_captcha")
    if use_captcha is True:
        Captcha.get_captcha_bal()
    utility.run_threads(max_threads=max_threads, func=joiner, args=[invite], delay=0)