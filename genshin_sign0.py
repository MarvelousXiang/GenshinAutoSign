import uuid
import json
import time
import random
import hashlib
import string

import requests


app_version = '2.1.0'
act_id = 'e202009291139501'

user = [
    {
        "user_name": '用户名',
        # https://bbs.mihoyo.com/ys/页面cookie
        "cookie": ''
    }
]


class Sign:

    def __init__(self, account_no):
        self.user_name = user[account_no]["user_name"]
        self.cookie = user[account_no]["cookie"]

        self.session = requests.session()
        self.session.headers.update({
            "User-Agent": f'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/{app_version}',
            "Referer": f'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id={act_id}&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
            "Accept-Encoding": 'gzip, deflate, br',
            "Cookie": self.cookie,
        })

        self.region = ''
        self.uid = 0

    def get_role(self):
        url = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn'
        for _ in range(3):
            try:
                json_response = self.session.get(url).json()
                break
            except Exception as e:
                print(repr(e))
        else:
            return False
        print(json_response)

        # cn_gf01: Official server
        # cn_qd01: Bilibili server
        self.region = json_response["data"]["list"][0]["region"]
        self.uid = json_response["data"]["list"][0]["game_uid"]
        return True

    # Provided by Steesha
    def md5(self, text):
        str_md5 = hashlib.md5()
        str_md5.update(text.encode())
        return str_md5.hexdigest()

    def calc_DS(self):
        t = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        result = self.md5(f'salt={self.md5(app_version)}&t={t}&r={r}')
        return f'{t},{r},{result}'

    def get_header(self):

        return {
            "x-rpc-device_id": str(uuid.uuid3(uuid.NAMESPACE_URL, self.cookie)).replace('-', '').upper(),
            "x-rpc-client_type": '5',
            "x-rpc-app_version": app_version,
            'DS': self.calc_DS()
        }

    def sign(self):
        url = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
        data = {
            "act_id": act_id,
            "region": self.region,
            "uid": self.uid
        }
        headers = {
            "x-rpc-device_id": str(uuid.uuid3(uuid.NAMESPACE_URL, self.cookie)).replace('-', '').upper(),
            "x-rpc-client_type": '5',
            "x-rpc-app_version": app_version,
            'DS': self.calc_DS()
        }
        for _ in range(3):
            try:
                json_response = self.session.post(url, headers=headers,
                                                  data=json.dumps(data, ensure_ascii=False)).json()
                break
            except Exception as e:
                print(repr(e))
        else:
            return False
        print(json_response)
        # {'retcode': 0, 'message': 'OK', 'data': {'code': 'ok'}}
        # {'data': None, 'message': '旅行者,你已经签到过了', 'retcode': -5003}

    def run(self):
        if not self.get_role():
            return
        time.sleep(3)
        self.sign()


for i in range(len(user)):
    print(user[i]["user_name"])
    Sign(i).run()
    time.sleep(5)
