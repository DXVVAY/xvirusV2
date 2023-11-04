from src import *

def mass_report():
    Output.set_title(f"Mass Report")
    tokens = TokenManager.get_tokens()

    def send(token, channel_id, message_id):
        while True:
            reasons = {
                31: "MESSAGE_SPAM",
                34: "ABUSE_OR_HARASSMENT"
            }
            reason = random.choice(list(reasons.keys()))
            data = {
                "version": "1.0",
                "variant": "3",
                "language": "en",
                "breadcrumbs": [
                    3,
                    reason
                ],
                "elements": {},
                "name": "message",
                "channel_id": channel_id,
                "message_id": message_id
            }
            session = Client.get_session(token)
            result = session.post(f"https://discord.com/api/v9/reporting/message", json=data)
    
            if result.status_code == 200:
                Output("good", token).log(f"Success -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            else:
                Output.error_logger(token, result.text, result.status_code)

    def thread_complete(future):
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

    message = utility.message_info()
    channel_id = message["channel_id"]
    message_id = message["message_id"]
    max_threads = utility.asknum("Thread Count")

    try:
        if not max_threads.strip():
            max_threads = "16"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "16"

    if tokens:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for token in tokens:
                try:
                    token = TokenManager.OnlyToken(token)
                    args = [token, channel_id, message_id]
                    future = executor.submit(send, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad").log(f"{e}")
    else:
        Output("bad").log(f"No tokens were found in cache")
        Output.PETC()