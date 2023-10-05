from colorma import Fore
from utils import *


class gui:
    logo = f'''{Fore.RED}
                                                                                  
                                         ,.   (   .      )        .      "        
                                       ("     )  )'     ,'        )  . (`     '`   
                                     .; )  ' (( (" )    ;(,     ((  (  ;)  "  )"  │Tokens: {token_count}
                                    _"., ,._'_.,)_(..,( . )_  _' )_') (. _..( '.. │Proxies: {proxycount}
                                    ██╗  ██╗██╗   ██╗██╗██████╗ ██╗   ██╗ ██████╗ ├─────────────
                                    ╚██╗██╔╝██║   ██║██║██╔══██╗██║   ██║██╔════╝ │Running on:
                                     ╚███╔╝ ╚██╗ ██╔╝██║██████╔╝██║   ██║╚█████╗  │{pc_username}\'s PC
                                     ██╔██╗  ╚████╔╝ ██║██╔══██╗██║   ██║ ╚═══██╗ ├─────────────
> [RPC] Toggle RPC                  ██╔╝╚██╗  ╚██╔╝  ██║██║  ██║╚██████╔╝██████╔╝ │Discord link:          
> [TM] Made by Xvirus™              ╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝  │.gg/xvirustool         Notes [NOTE] <
> [?] {THIS_VERSION} Changelog                                                                                    Restart [RST] <
> [!] Settings                                                                                     Manage Tokens [TKN] <'''

    options = f'''{Fore.RED}
 ╔═══                              ═══╗ ╔═══                               ═══╗ ╔═══                               ═══╗
 ║   (01) > Joiner                    ║ ║   (10) > Message Reactor            ║ ║   (20) > N/A                        ║
     (02) > Leaver                          (11) > Bio Changer                      (21) > N/A
     (03) > Spammer                         (12) > User Mass Friender               (22) > N/A
     (04) > Vc Joiner                       (13) > Server Mass Friender             (23) > N/A
     (05) > Server Nickname Changer         (14) > User Mass DM                     (24) > N/A
     (06) > Global Nickname Changer         (15) > Server Mass DM                   (25) > N/A
     (07) > Accept Rules                    (16) > N/A                              (26) > N/A
     (08) > Token Onliner                   (17) > N/A                              (27) > N/A
 ║   (09) > Button Presser            ║ ║   (18) > N/A                         ║ ║  (28) > N/A                        ║
 ╚═══                              ═══╝ ╚═══                                ═══╝ ╚═══                              ═══╝'''

    def main_menu():
        print(logo)
        print(options)
        print(f'{Fore.RED} ┌──<{username}@Xvirus>─[~]')
        choicee = input(f' └──╼ $ {Fore.BLUE}').lstrip("0")
        choice = choicee.upper()
        