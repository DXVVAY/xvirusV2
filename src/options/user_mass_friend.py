from src import *

def user_mass_friend():
    Output.set_title(f"User Mass Friend")
    sent = 0
    error = 0
    args = []
    tokens = TokenManager.get_tokens()

    def send(token, username):
        nonlocal sent, error
        session = Client.get_session(token)
        session_id = utility.get_session_id()
        data = {
            "session_id": session_id,
            "username": username,
        }
        result = session.post(f"https://discord.com/api/v9/users/@me/relationships", json=data)

        if result.status_code == 204:
            Output("good", token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            sent += 1
        else:
            Output.error_logger(token, result.text, result.status_code)
            error += 1

        
    def thread_complete(future):
        nonlocal sent, error
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

    username = utility.ask("Username")
    max_threads = utility.asknum("Thread Count")

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
                    args = [token, username]
                    future = executor.submit(send, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad").log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info").notime(f"Sent Friend Request Using {str(sent)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Sent: {str(sent)}",
            f"{Fore.LIGHTRED_EX}Errors: {str(error)}",
            f"{Fore.LIGHTCYAN_EX}Total: {len(tokens)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}"
        print(f" {status}")
        Output.PETC()
    else:
        Output("bad").log(f"No tokens were found in cache")
        Output.PETC()