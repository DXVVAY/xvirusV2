import requests
import time
from tls_client import Session
from src import *

class VastSolver:
    def __init__():
        hsw_api = "http://api.vast.sh:3030"
        solve_api = "http://api.vast.sh:3200"
        ses = Session()

    def solver(api_key, sitekey, proxy):
        try:
            payload = {
                'userId': api_key,
                'data': {
                    'websiteURL': "discord.com",
                    'websiteKey': sitekey,
                    'userAgent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    'hsw_serv': f"{VastSolver.hsw_api}/hsw",
                    "proxy": proxy
                }
            }
            response = VastSolver.ses.post(f"{VastSolver.solve_api}/createTask", json=payload)
            if response.json().get("status") == "Task created and enqueued":
                task_id = response.json().get('taskId')
            else:
                if response.json().get("error") is None:
                    Output("bad").log(f'Solver -> {response.text}')
                else:
                    Output("bad").log(f'Solver -> {response.json().get("error")}')
                return VastSolver.solver(api_key, sitekey, proxy)

            while True:
                payload2 = {'userId': api_key, 'taskId': task_id}
                response = VastSolver.ses.get(f"{VastSolver.solve_api}/getTask", json=payload2)
                task_status = response.json().get('status')
                
                if task_status == 'pending':
                    sleep(1)
                elif task_status == 'completed':
                    task_result = response.json().get('result')
                    if task_result == "Maximum number of attempts reached":
                        return VastSolver.solver(api_key, sitekey, proxy)
                    else:
                        return task_result
                elif task_status == 'error':
                    Output("bad").log(f'Solver -> {response.json().get("error")}')
                    break
                else:
                    Output("bad").log(f"Solver -> Unknown response -> {response.text}")
                    break
        except exceptions.TLSClientExeption:
            Output("bad").log(f"Solver -> Vast Solver API Offline.")
        except:
            Output("bad").log(f"Solver -> other exception")