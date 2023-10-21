
import datetime
import time
from concurrent.futures import ThreadPoolExecutor
import webbrowser
from colorama import Fore

from src import *

def buyTokensDazeer(): 
    redirect = utility.ask("Do you want to redirect to dazeer.sellpass.io (y/n)")
    if redirect.lower() == 'y':
        webbrowser.open("https://dazeer.sellpass.io/products/634d684f745af")
    elif redirect.lower() == 'n':
        Output("bad", config)("Redirect not requested.")
    else:
        Output("bad", config)("Invalid input. Redirect not requested.")

def buyTokensBody(): 
    redirect = utility.ask("Do you want to redirect to https://bodyx.mysellix.io/product/ (y/n)")
    if redirect.lower() == 'y':
        webbrowser.open("https://bodyx.mysellix.io/product/64e4b3244c004")
    elif redirect.lower() == 'n':
        Output("bad", config)("Redirect not requested.")
    else:
        Output("bad", config)("Invalid input. Redirect not requested.")

def choose_store():
    utility.make_menu("Body Tokens", "Dazeer Tokens")
    choice = utility.ask("Choice")

    if choice == '1':
        buyTokensBody()
    
    if choice == '2':
        buyTokensDazeer()

def token_manager():
    Output.SetTitle(f"Token Manager")
    utility.make_menu("Save Tokens", "Empty Tokens", "Buy Tokens")
    choice = utility.ask("Choice")

    if choice == '1':
        checker()
    
    if choice == '2':
        config.reset('xvirus_tokens')
        Output("info", config).notime("Tokens Chache Emptied.")
        Output.PETC()
    
    if choice == '3':
        choose_store()

def checker():
    valid = 0
    locked = 0
    invalid = 0
    error = 0
    
    token_file_path = utility.ask("Enter the path to the text file containing tokens").strip()
    tokens = TokenManager.custom_path(token_file_path)

    def check_token(token):
        nonlocal valid, locked, invalid, error
        session, headers, cookie = Header.get_client(token)
        result = session.get("https://discord.com/api/v9/users/@me/settings", headers=headers, cookies=cookie)

        if result.status_code == 200:
            Output("good", config, token).log(f"Valid -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            valid += 1
            config.add('xvirus_tokens', token)
        elif "You need to verify your account in order to perform this action." in result.text:
            Output("info", config, token).log(f"Locked -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            locked += 1
        elif "Unauthorized" in result.text:
            Output("bad", config, token).log(f"Invalid -> {token} {Fore.LIGHTBLACK_EX}({result.status_code})")
            invalid += 1
        else:
            error += 1

    def thread_complete(future):
        nonlocal valid, locked, invalid, error
        try:
            result = future.result()
        except Exception as e:
            pass

    if tokens is None:
        Output("bad", config).log("Token retrieval failed or returned None.")
        Output.PETC()
        return

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
                    args = [token]
                    future = executor.submit(check_token, *args)
                    future.add_done_callback(thread_complete)
                    time.sleep(0.1)
                except Exception as e:
                    Output("bad", config).log(f"{e}")

        elapsed_time = time.time() - start_time
        Output("info", config).notime(f"Checked {len(tokens)} Tokens In {elapsed_time:.2f} Seconds")

        info = [
            f"{Fore.LIGHTGREEN_EX}Valid: {str(valid)}",
            f"{Fore.LIGHTBLACK_EX}Locked: {str(locked)}",
            f"{Fore.LIGHTRED_EX}Invalid: {str(invalid)}",
            f"{Fore.LIGHTCYAN_EX}Errors: {str(error)}"
        ]

        status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
        print(f" {status}")
        
        Output.PETC()
    else:
        Output("bad", config).log(f"No tokens were found in the specified text file")
        Output.PETC()