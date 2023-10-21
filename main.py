from src import *

pc_username = getpass.getuser()
def move_key():
    old_key = os.path.join(os.environ.get("TEMP", "C:\\temp"), "xvirus_key")
    if os.path.exists(old_key):
        with open(old_key, "r") as key_file:
            key = key_file.read().strip()
            config._set("xvirus_key", key)
        os.remove(old_key)
    else:
        pass

def get_checksum():
    md5_hash = hashlib.md5()
    with open("".join(sys.argv), "rb") as file:
        md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest

auth = api(
    name="xvirus",
    ownerid="H1Blx2txmS",
    secret="f8a86b6a889a4c6da214ceabc99fedffbbe464adb64d7df87934afb70625ad92",
    version="1.0",
    hash_to_check=get_checksum())

def license_check():
    saved_key = config._get("xvirus_key")
    if saved_key:
            auth.license(saved_key)
            Output("info", config).notime(f"Welcome Back {pc_username}!")
            sleep(2)
    else:
        ask_for_key()

def ask_for_key():
        key = utility.ask("Enter your Xvirus License Key")
        config._set("xvirus_key", key)
        auth.license(key)
        Output("info", config).notime(f"Welcome Back {pc_username}!")
        sleep(2)
            
class gui:
    def WIP():
        Output.SetTitle("This Option Is A WIP")
        Output("info", config).notime("This Option Is A Work In Progress, It Will Be Available In The Next Update!")
        Output.PETC()

    lr = Fore.LIGHTRED_EX
    lb = Fore.LIGHTBLACK_EX
    r = Fore.RED
    pc_username = getpass.getuser()
    logo = f'''{Fore.RED}
                                                                                  
                                         ,.   (   .      )        .      "        
                                       ("     )  )'     ,'        )  . (`     '`   
                                     .; )  ' (( (" )    ;(,     ((  (  ;)  "  )"  │Tokens: {len(TokenManager.get_tokens())}
                                    _"., ,._'_.,)_(..,( . )_  _' )_') (. _..( '.. │Proxies: {len(ProxyManager.get_proxies())}
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
{r}║   ({lb}01{r}) {lb}> Joiner                    {r}║ ║   {r}({lb}10{r}) {lb}> Global Nick Changer        {r}║ ║   {r}({lb}19{r}) {lb}> User Mass Friend{r}             ║
{r}    ({lb}02{r}) {lb}> Leaver                          {r}({lb}11{r}) {lb}> Server Nick Changer              {r}({lb}20{r}) {lb}> Server Mass Friend{r}
{r}    ({lb}03{r}) {lb}> Spammer                         {r}({lb}12{r}) {lb}> HypeSquad Changer                {r}({lb}21{r}) {lb}> N/A{r}
{r}    ({lb}04{r}) {lb}> Checker                         {r}({lb}13{r}) {lb}> Bio Changer                      {r}({lb}22{r}) {lb}> N/A{r}
{r}    ({lb}05{r}) {lb}> Bypass Rules                    {r}({lb}14{r}) {lb}> Pronouns Changer                 {r}({lb}23{r}) {lb}> N/A{r}
{r}    ({lb}06{r}) {lb}> Bypass RestoreCord              {r}({lb}15{r}) {lb}> VC Joiner                        {r}({lb}24{r}) {lb}> N/A{r}
{r}    ({lb}07{r}) {lb}> Button Presser                  {r}({lb}16{r}) {lb}> Sound Board Spammer              {r}({lb}25{r}) {lb}> N/A{r}
{r}    ({lb}08{r}) {lb}> Reactor                         {r}({lb}17{r}) {lb}> Fake Typer                       {r}({lb}26{r}) {lb}> N/A{r}
{r}║   ({lb}09{r}) {lb}> Mass Thread               {r}║ ║   {r}({lb}18{r}) {lb}> Forum Spammer               {r}║ ║  {r}({lb}27{r}) {lb}> N/A{r}                          ║
{r}╚═══                              ═══╝ ╚═══                                ═══╝ ╚═══                                ═══╝'''

    def main_menu():
        utility.clear()
        Output.SetTitle(f"Xvirus {THIS_VERSION}")
        print(gui.logo)
        print(gui.options)
        print(f'{Fore.RED}┌──<{gui.pc_username}@Xvirus>─[~]')
        choicee = input(f'└──╼ $ {Fore.BLUE}').lstrip("0")
        choice = choicee.upper()

        try:
            if choice == '1':
                utility.make_menu(f"RestoreCord Mode {Fore.RED}(bypass captcha)", f"Normal Mode {Fore.RED}(solve captcha)")
                choice = utility.ask("Choice")
                if choice == '1':
                    restorecord_bypass()
                else:
                    token_joiner()
            elif choice == '2':
                token_leaver()
            elif choice == '3':
                channel_spammer()
            elif choice == '4':
                token_checker()
            elif choice == '5':
                bypass_rules()
            elif choice == '6':
                restorecord_bypass()
            elif choice == '7':
                button_presser()
            elif choice == '8':
                token_reactor()
            elif choice == '9':
                mass_thread()
            elif choice == '10':
                global_nicker()
            elif choice == '11':
                server_nicker()
            elif choice == '12':
                hypesquad_changer()
            elif choice == '13':
                token_bio_changer()
            elif choice == '14':
                token_pron_changer()
            elif choice == '15':
                utility.make_menu("Join And Stay", "Join And Leave Spamm")
                choice = utility.ask("Choice")
                if choice == '1':
                    token_vc_joiner()
                else:
                    vc_join_spammer()
            elif choice == '16':
                soundboard_spammer()
            elif choice == '17':
                token_typer()
            elif choice == '18':
                gui.WIP()
            elif choice == '19':
                user_mass_friend()
            elif choice == '20':
                server_mass_friend()
            elif choice == '!':
                settings()
            elif choice == 'TKN':
                token_manager()
            else:
                Output("bad", config).notime("Invalid choice, please try again!")
                sleep(1)
        except Exception as e:
            Output("bad", config).notime(f"{e}")
            input()

        gui.main_menu()


if __name__ == "__main__":
    utility.clear()
    Output.SetTitle("Xvirus Loading")
    move_key()
    license_check()
    gui.main_menu()