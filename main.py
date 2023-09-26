from utils import *

Start_balance = utility.getCapBal()
End_balance = utility.getCapBal()
balance_used = float(Start_balance[1:]) - float(End_balance[1:])

info = [
    f"{Fore.LIGHTGREEN_EX}Start: {Start_balance}",
    f"{Fore.LIGHTCYAN_EX}End: {End_balance}",
    f"{Fore.LIGHTRED_EX}Used: ${balance_used:.2f}",
]
status = f"{Fore.RED} | ".join(info) + f"{Fore.RED}\n"
print(status)