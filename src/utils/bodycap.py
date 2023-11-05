import requests
import time
from src import *

class BodyCap:
    def __init__(self):
        self.captcha_key = config._get("captcha_key")
        self.key = self.captcha_key
        
    def solve_turnstile(self, sitekey : str, url : str, invisible : bool = False) -> object:
        return self.solve(type="turnstile", sitekey=sitekey, website=url, invisible=invisible)
    
    def solve_cybersiara(self, sitekey : str, url : str) -> object:
        return self.solve(type="cybersiara", sitekey=sitekey, website=url)

    def solve_recaptcha_v3(self, sitekey : str, url : str, action : str = "submit") -> object:
        return self.solve(type="recaptchav3", sitekey=sitekey, website=url, action=action)
    
    def solve_hcaptcha(self, sitekey : str, host : str, proxy : str = "", rqdata : str = "") -> object:
        return self.solve(type="hcaptcha", sitekey=sitekey, host=host, proxy=proxy, rqdata=rqdata)

    def solve(self, **kwargs) -> object:
        start = time.time()
        task = {}
        for key, value in kwargs.items():
            task[key] = value

        r = requests.post("https://api.hcaptcha.lol/api/create_task", json={
            "clientKey": self.key,
            "task": task
        }, timeout=5)

        print(r.json())

        if not "task_id" in r.json():
            return {
                "success": False,
                "duration": time.time() - start,
            }
    
        task_id = r.json()["task_id"]
        while True:
            r = requests.post("https://api.hcaptcha.lol/api/get_task_result", json={
                "clientKey": self.key,
                "task_id": task_id
            }, timeout=120)
            errors = ["timeout", "error", "failed"]
            if r.json()["status"] == "completed":
                break
            if r.json()["status"] in errors:
                return {
                    "success": False,
                    "duration": time.time() - start,
                }
            
            time.sleep(1)
        
        return {
            "solution": r.json()["solution"],
            "duration": time.time() - start,
            "success": True
        }