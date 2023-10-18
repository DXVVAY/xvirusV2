from concurrent.futures import ThreadPoolExecutor
import os
import httpx
from src import *

def reset_users(file):
    if os.path.exists(file):
        os.remove(file)

def user_scraper():
    Output.SetTitle(f"User Scraper")
    folder_path = os.path.join(os.getenv('LOCALAPPDATA'), 'xvirus_config')
    file = os.path.join(folder_path, 'xvirus_usernames')
    reset_users(file)
    token = TokenManager.get_random_token()
    session, headers, cookie = Header.get_client(token)
    
    user_ids = utility.get_ids()
    id_to_username = {}
    max_threads = utility.asknum("Thread Count")
    
    try:
        if not max_threads.strip():
            max_threads = "16"
        else:
            max_threads = int(max_threads)
    except ValueError:
        max_threads = "16"
    
    def fetch_user(user_id):
        nonlocal id_to_username
        result = httpx.get(f"https://discord.com/api/v9/users/{user_id}", headers=headers, cookies=cookie)
        if result.status_code == 200:
            user_data = result.json()
            username = user_data.get('username', 'Username not found')
            id_to_username[user_id] = username
            Output("good", config).log(f"Success -> Converted {user_id} > {username} {Fore.BLUE}({str(result.status_code)})")
            with open(file, "a", encoding='utf-8') as x:
                x.write(f"{username}\n")
        elif result.status_code == 429:
            Output("bad", config).log(f"Error -> {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}(Rate Limited)")
            sleep(result.json()["retry_after"] / 1000)
        else:
            Output("bad", config).log(f"Error -> {Fore.LIGHTBLACK_EX}({result.status_code}) {Fore.RED}({result.text})")
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(fetch_user, user_ids)