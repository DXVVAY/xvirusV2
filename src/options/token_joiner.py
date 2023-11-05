from src import *

def token_joiner():
    Output.set_title(f"Token Joiner")
    joined = 0
    error = 0
    args = []
    tokens = TokenManager.get_tokens()

    def join(token, invite):
        nonlocal joined, error
        session = Client.get_session(token)
        session_id = utility.get_session_id()
        result = session.post(f"https://discord.com/api/v9/invites/{invite}", json={"session_id": session_id})

        if result.status_code == 200:
            Output("good", token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            joined += 1
        else:
            Output.error_logger(token, result.text, result.status_code)
            error += 1
        
    def thread_complete(future):
        nonlocal joined, error
        debug = config._get("debug_mode")
        try:
            result = future.result()
        except Exception as e:
            if debug:
                if "failed to do request" in str(e):
                    message = f"Proxy Error -> {str(e)[:80]}..."
                else:
                    message = f"Error -> {e}"
                Output("dbg").log(message)
            else:
                pass


    if tokens is None:
        Output("bad").log("Token retrieval failed or returned None.")
        Output.PETC()
        return

    invite = utility.ask("Invite")
    invite = invite.replace("https://discord.gg/", "").replace("https://discord.com/invite/", "").replace("discord.gg/", "").replace("https://discord.com/invite/", "")
    max_threads = utility.asknum("Thread Count")

    req = requests.get(f"https://discord.com/api/v9/invites/{invite}?with_counts=true&with_expiration=true")
    if req.status_code == 200:
        res = req.json()
        Output("info").notime(f"Joining {Fore.RED}{res['guild']['name']}")
    else:
        pass

    try:
        if not max_threads.strip():
            max_threads = "16"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "16"

    if tokens:
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for token in tokens:
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, invite]
                    future = executor.submit(join, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad").log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info").notime(f"Joined {str(joined)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Joined: {str(joined)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad").log(f"No tokens were found in cache")
        Output.PETC()