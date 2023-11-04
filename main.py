from src import *

class XvirusApp:
    # Body DLL Patch!!!!!!
    def __init__(self):
        self.pc_username = getpass.getuser()
        self.fr = api(
            name="xvirus",
            ownerid="H1Blx2txmS",
            secret="f8a86b6a889a4c6da214ceabc99fedffbbe464adb64d7df87934afb70625ad92",
            version="1.0",
            hash_to_check=self.get_checksum())

    def move_key(self):
        old_key = os.path.join(os.environ.get("TEMP", "C:\\temp"), "xvirus_key")
        if os.path.exists(old_key):
            with open(old_key, "r") as key_file:
                key = key_file.read().strip()
                config._set("xvirus_key", key)
            os.remove(old_key)
        else:
            pass

    def get_checksum(self):
        md5_hash = hashlib.md5()
        with open("".join(sys.argv), "rb") as file:
            md5_hash.update(file.read())
        digest = md5_hash.hexdigest()
        return digest

    def check(self):
        saved_key = config._get("xvirus_key")
        if saved_key:
            self.fr.license(saved_key)
            Output("info").notime(f"Welcome Back {self.pc_username}!")
            sleep(2)
        else:
            self.ask_for_key()

    def ask_for_key(self):
            key = utility.ask("Enter your Xvirus License Key")
            config._set("xvirus_key", key)
            self.fr.license(key)
            Output("info").notime(f"Welcome Back {self.pc_username}!")
            sleep(2)

class gui:
    def get_tokens():
        f = config.read('xvirus_tokens')
        tokens = f.strip().splitlines()
        tokens = [token for token in tokens if token not in [" ", "", "\n"]]
        return tokens
    
    def get_proxies():
        f = config.read('xvirus_proxies')
        proxies = f.strip().splitlines()
        proxies = [proxy for proxy in proxies if proxy not in [" ", "", "\n"]]
        return proxies
    
    def WIP():
        Output.set_title("This Option Is A WIP")
        Output("info").notime("This Option Is A Work In Progress, It Will Be Available In The Future!")
        Output.PETC()

    lb = Fore.LIGHTBLACK_EX
    r = Fore.RED
    pc_username = getpass.getuser()
    logo = f'''{Fore.RED}
                                                                                  
                                         ,.   (   .      )        .      "        
                                       ("     )  )'     ,'        )  . (`     '`   
                                     .; )  ' (( (" )    ;(,     ((  (  ;)  "  )"  │Tokens: {len(get_tokens())}
                                    _"., ,._'_.,)_(..,( . )_  _' )_') (. _..( '.. │Proxies: {len(get_proxies())}
                                    ██╗  ██╗██╗   ██╗██╗██████╗ ██╗   ██╗ ██████╗ ├─────────────
                                    ╚██╗██╔╝██║   ██║██║██╔══██╗██║   ██║██╔════╝ │Running on:
                                     ╚███╔╝ ╚██╗ ██╔╝██║██████╔╝██║   ██║╚█████╗  │{pc_username}\'s PC
                                     ██╔██╗  ╚████╔╝ ██║██╔══██╗██║   ██║ ╚═══██╗ ├─────────────
                                    ██╔╝╚██╗  ╚██╔╝  ██║██║  ██║╚██████╔╝██████╔╝ │Discord link:          
> [TM] Made by Xvirus™              ╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝  │.gg/xvirustool
> [?] {THIS_VERSION} Changelog                                                                                     Notes [NOTE] <
> [!] Settings                                                                                     Manage Tokens [TKN] <'''

    options = f'''{r} 
{r}╔═══                              ═══╗ ╔═══                               ═══╗ ╔═══                                 ═══╗
{r}║   ({lb}01{r}) {lb}> Token Joiner              {r}║ ║   {r}({lb}10{r}) {lb}> Global Nick Changer        {r}║ ║   {r}({lb}19{r}) {lb}> User Mass Friend{r}             ║
{r}    ({lb}02{r}) {lb}> Token Leaver                    {r}({lb}11{r}) {lb}> Server Nick Changer              {r}({lb}20{r}) {lb}> User Mass DM{r}
{r}    ({lb}03{r}) {lb}> Token Spammer                   {r}({lb}12{r}) {lb}> HypeSquad Changer                {r}({lb}21{r}) {lb}> Mass Report{r}
{r}    ({lb}04{r}) {lb}> Multi Checker                   {r}({lb}13{r}) {lb}> Bio Changer                      {r}({lb}22{r}) {lb}> Mass Thread{r}
{r}    ({lb}05{r}) {lb}> Bypass Rules                    {r}({lb}14{r}) {lb}> Pronouns Changer                 {r}({lb}23{r}) {lb}> Forum Spammer{r}
{r}    ({lb}06{r}) {lb}> Bypass RestoreCord              {r}({lb}15{r}) {lb}> Voice Chat Joiner                {r}({lb}24{r}) {lb}> N/A{r}
{r}    ({lb}07{r}) {lb}> Bypass Sledge Hammer            {r}({lb}16{r}) {lb}> Sound Board Spammer              {r}({lb}25{r}) {lb}> N/A{r}
{r}    ({lb}08{r}) {lb}> Button Presser                  {r}({lb}17{r}) {lb}> Fake Typer                       {r}({lb}26{r}) {lb}> N/A{r}
{r}║   ({lb}09{r}) {lb}> Message Reactor           {r}║ ║   {r}({lb}18{r}) {lb}> Forum Spammer               {r}║ ║  {r}({lb}27{r}) {lb}> N/A{r}                          ║
{r}╚═══                              ═══╝ ╚═══                                ═══╝ ╚═══                                ═══╝'''

    def main_menu():
        utility.clear()
        Output.set_title(f"Xvirus {THIS_VERSION}")
        ascii = pystyle.Center.XCenter(gui.logo)
        ops = pystyle.Center.XCenter(gui.options)
        print(ascii)
        print(ops)
        print(f'{Fore.RED}┌──<{gui.pc_username}@Xvirus>─[~]')
        choicee = input(f'└──╼ $ {Fore.BLUE}').lstrip("0")
        choice = choicee.upper()

        def joiner_menu():
            utility.make_menu(f"Normal Mode", f"RestoreCord Mode {Fore.RED}(bypass captcha)")
            choice = utility.ask("Choice")
            if choice == '1':
                token_joiner()
            else:
                restorecord_bypass()
        
        def checker_menu():
            utility.make_menu("Cache Checker", "Custom Checker", "Server Checker")
            choice = utility.ask("Choice")
            if choice == '1':
                tokens = TokenManager.get_tokens()
                token_checker(tokens)
            elif choice == '2':
                path = utility.ask("Enter the custom path to load tokens from").strip()
                tokens = TokenManager.custom_path(path)
                token_checker(tokens)
            elif choice == '3':
                server_checker()

        def vc_menu():
            utility.make_menu("Join And Stay", "Join And Leave Spam")
            choice = utility.ask("Choice")
            if choice == '1':
                token_vc_joiner()
            else:
                vc_join_spammer()

        def wip():
            gui.WIP()

        try:
            options = {
                '1': joiner_menu,
                '2': token_leaver,
                '3': channel_spammer,
                '4': checker_menu,
                '5': bypass_rules,
                '6': restorecord_bypass,
                '7': sledge_hammer,
                '8': button_presser,
                '9': token_reactor,
                '10': global_nicker,
                '11': server_nicker,
                '12': hypesquad_changer,
                '13': token_bio_changer,
                '14': token_pron_changer,
                '15': vc_menu,
                '16': soundboard_spammer,
                '17': token_typer,
                '18': forum_spammer,
                '19': user_mass_friend,
                '20': user_mass_dm,
                '21': mass_report,
                '22': mass_thread,
                '23': forum_spammer,
                '!': settings,
                'TKN': token_manager
            }
            choosen = options.get(choice)
            if choosen:
                choosen()
                time.sleep(1)
            else:
                Output("bad").notime("Invalid choice, please try again!")
                sleep(1)

        except Exception as e:
            Output("bad").notime(f"{e}")
            input()

        gui.main_menu()

if __name__ == "__main__":
    utility.clear()
    run_anti_debug()
    Output.set_title("Xvirus Loading")
    app = XvirusApp()
    app.move_key()
    app.check()
    gui.main_menu()