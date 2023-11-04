from src import *

class proxy_setting():
    def toggle_proxy():
        current_setting = config._get("use_proxies")

        if current_setting == True:
            config._set("use_proxies", False)
            Output("info").notime(f"Proxy Use Toggled {Fore.RED}OFF")
            sleep(1)
        else:
            config._set("use_proxies", True)
            Output("info").notime(f"Proxy Use Toggled {Fore.RED}ON")
            sleep(1)

    def clear_proxy():
        config.reset("xvirus_proxies")
        Output("info").notime("Proxy Cache Cleared")
        sleep(1)   

    def add_proxies():
        path = utility.ask(f'Enter the path to the txt file containing proxies')
        folder_path = os.path.join(os.getenv('LOCALAPPDATA'), 'xvirus_config')
        file_path = os.path.join(folder_path, 'xvirus_proxies')
        proxy_setting.clear_proxy()

        with open(path, 'r') as file:
            proxies = file.read()

        with open(file_path, 'w') as f:
            f.write(proxies)

        Output("info").notime("Successfully Wrote New Proxies")
        sleep(1) 

class captcha_setting():
    def toggle_captcha():
        current_setting = config._get("use_captcha")

        if current_setting == True:
            config._set("use_captcha", False)
            Output("info").notime(f"Captcha Use Toggled {Fore.RED}OFF")
            sleep(1)
        else:
            config._set("use_captcha", True)
            Output("info").notime(f"Captcha Use Toggled {Fore.RED}ON")
            sleep(1)
            
    def change_service():
        utility.make_menu("Capsolver", "Capmonster")
        choice = utility.ask('Choice')
        if choice == "1":
            config._set("captcha_typ", "capsolver")
            Output("info").notime(f"Using {Fore.RED}Capsolver")
            sleep(1)
        elif choice == "2":
            config._set("captcha_typ", "capmonster")
            Output("info").notime(f"Using {Fore.RED}Capmonster")
            sleep(1)

    def change_key():
        key = utility.ask("Captcha Key")
        config._set("captcha_key", key)
        Output("info").notime("Captcha Key Applied")
        sleep(1)  

def settings():
    utility.make_menu("Captcha Settings", "Proxy Settings", "Toggle Debug Mode", f"{Fore.RED}Exit... ")
    choice = utility.ask('Setting')
    if choice not in ["1", "2", "3"]:
        Output("bad").notime(f'Invalid Setting')
        sleep(1)
    elif choice == "1":
        utility.make_menu("Toggle Captcha Use", "Choose Captcha Service", "Add/Change Captcha Key")
        captchachoice = utility.ask('Choice')
        if captchachoice == '1':
            captcha_setting.toggle_captcha()
        elif captchachoice == '2':
            captcha_setting.change_service()
        elif captchachoice == '3':
            captcha_setting.change_key()
        else:
            Output("bad").notime("Invalid Choice")

    elif choice == "2":
        utility.make_menu("Toggle Proxy Use", "Clear Proxy Cache", "Add own Proxies to Cache")
        proxychoice = utility.ask('Choice')
        if proxychoice == '1':
            proxy_setting.toggle_proxy()
        elif proxychoice == '2':
            proxy_setting.clear_proxy()
        elif proxychoice == '3':
            proxy_setting.add_proxies()
        else:
            Output("bad").notime("Invalid Choice")

    elif choice == '3':
        current_setting = config._get("debug_mode")

        if current_setting == True:
            config._set("debug_mode", False)
            Output("info").notime(f"Debug Mode Toggled {Fore.RED}OFF")
            sleep(1)
        else:
            config._set("debug_mode", True)
            Output("info").notime(f"Debug Mode Toggled {Fore.RED}ON")
            sleep(1)

    elif choice == "4":
        choice = utility.ask('Are you sure you want to exit Xvirus? (Y to confirm)')
        if choice.upper() == 'Y':
            utility.clear()
            os._exit(0)
        else:
            sleep(0.5)
    else:
        utility.clear()