from src import *

class gui:
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
{r}║   ({lb}01{r}) {lb}> Joiner                    {r}║ ║   {r}({lb}10{r}) {lb}> Message Reactor            {r}║ ║   {r}({lb}19{r}) {lb}> N/A{r}                          ║
{r}    ({lb}02{r}) {lb}> Leaver                          {r}({lb}11{r}) {lb}> Bio Changer                      {r}({lb}21{r}) {lb}> N/A{r}
{r}    ({lb}03{r}) {lb}> Spammer                         {r}({lb}12{r}) {lb}> User Mass Friender               {r}({lb}22{r}) {lb}> N/A{r}
{r}    ({lb}04{r}) {lb}> Checker                         {r}({lb}13{r}) {lb}> Server Mass Friender             {r}({lb}23{r}) {lb}> N/A{r}
{r}    ({lb}05{r}) {lb}> Server Nickname Changer         {r}({lb}14{r}) {lb}> User Mass DM                     {r}({lb}24{r}) {lb}> N/A{r}
{r}    ({lb}06{r}) {lb}> Global Nickname Changer         {r}({lb}15{r}) {lb}> Server Mass DM                   {r}({lb}25{r}) {lb}> N/A{r}
{r}    ({lb}07{r}) {lb}> Accept Rules                    {r}({lb}16{r}) {lb}> N/A                              {r}({lb}26{r}) {lb}> N/A{r}
{r}    ({lb}08{r}) {lb}> Token Onliner                   {r}({lb}17{r}) {lb}> N/A                              {r}({lb}27{r}) {lb}> N/A{r}
{r}║   ({lb}09{r}) {lb}> Button Presser            {r}║ ║   {r}({lb}18{r}) {lb}> N/A                         {r}║ ║  {r}({lb}28{r}) {lb}> N/A{r}                          ║
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
                token_joiner()
            elif choice == '2':
                token_leaver()
            elif choice == '3':
                channel_spammer()
            elif choice == '4':
                token_checker()
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
    gui.main_menu()