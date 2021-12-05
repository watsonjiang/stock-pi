import time
import hmac
import base64
import hashlib
import urllib3 as urllib
import logging
import requests
from . import IMessenger

LOGGER = logging.getLogger(__name__)

FEISHU_HOOK_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook'

class FeishuRobot(IMessenger):
    '''飞书机器人消息
    '''
    def __init__(self, ak, sk):
        self.ak = ak
        self.sk = sk

    def make_sign(self):
        timestamp = round(time.time())
        string_to_sign = '{}\n{}'.format(timestamp, self.sk)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        LOGGER.info('-----ts:%s sign:%s', timestamp, sign)
        return timestamp, sign

    def send_msg(self, msg):
        ''' 发送文本消息
        '''
        ts, sign = self.make_sign()
        data = {
            'timestamp': str(ts),
            'sign': sign,
            'msg_type': 'text',
            'content': {
                'text': msg
            }
        }
        url = "{}/{}".format(FEISHU_HOOK_URL, self.ak)
        LOGGER.info("------data:%s", data)
        rsp = requests.post(url, json=data)
        LOGGER.debug("-----rsp:%s", rsp.json()) 