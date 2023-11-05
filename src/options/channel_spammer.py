from src import *

def tls_session() -> tls_client.Session:
    client = tls_client.Session(
        client_identifier=f"chrome_{random.randint(110, 116)}",
        random_tls_extension_order=True
    )   
    if config._get("use_proxies"):
        proxy = ProxyManager.clean_proxy(ProxyManager.random_proxy())
        if isinstance(proxy, str):
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
        elif isinstance(proxy, dict):
            proxy_dict = proxy
        client.proxies = proxy_dict
    
    return client

def send(token, message, channelid, massping, amount=None):  
    try:
        session = tls_session()
        while True:
            try:
                if massping == 'y':
                    content = f"{message} | {utility.get_random_id(int(amount))}"
                else:
                    content = f"{message} | {utility.rand_str(7)}"
                session.headers = static_headers
                session.headers.update({"Authorization":token})
                session_id = utility.get_session_id(token)
                data = {'session_id': session_id, "content": content}
                result = session.post(f"https://discord.com/api/v9/channels/{channelid}/messages", json=data)

                if result.status_code == 200:
                    Output("good", token).log(f"Success {Fore.LIGHTBLACK_EX}->{Fore.GREEN} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code})")
                elif result.text.startswith('{"captcha_key"'):
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Captcha)")
                elif result.text.startswith('{"message": "401: Unauthorized'):
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Unauthorized)")   
                elif result.status_code == 429:
                    pass
                elif "\"code\": 50001" in result.text:
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")    
                elif "Cloudflare" in result.text:
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(CloudFlare Blocked)")
                elif "\"code\": 40007" in result.text:
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Token Banned)")
                elif "\"code\": 40002" in result.text:
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Locked Token)")
                elif "\"code\": 10006" in result.text:
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Invalid Invite)")
                elif "\"code\": 50013" in result.text:
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(No Access)")
                else:
                    Output("bad", token).log(f"Error {Fore.LIGHTBLACK_EX}->{Fore.RED} {message[:20]}... {Fore.LIGHTBLACK_EX}-> {token[:50]} {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
            except Exception as e:
                Output("bad").log(f"{e}")
    except Exception as e:
        Output("bad").log(f"{e}")

def channel_spammer():
    Output.set_title(f"Channel Spammer")
    tokens = TokenManager.get_tokens()

    if tokens is None:
        Output("bad").log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    channel_id = utility.ask("Channel ID")
    message = utility.ask("Message")
    max_threads = utility.asknum("Thread Count")
    massping = utility.ask("Massping (y/n)")
    amount = 0
    
    if massping == 'y':
        guild_id = utility.ask("Guild ID")
        id_scraper(guild_id, channel_id)
        ids = utility.get_ids()
        amount = utility.ask(f"Amount Of pings (Don't exceed {len(ids)})")

    try:
        if not max_threads.strip():
            max_threads = "16"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "16"
    
    while True:
        if tokens:
            def thread_send(token):
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, message, channel_id, massping, amount]
                    send(*args)
                except Exception as e:
                    print(f"{e}")

            threads = []
            for token in tokens:
                thread = threading.Thread(target=thread_send, args=(token,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
        else:
            return