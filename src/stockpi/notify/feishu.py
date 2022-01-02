import time
import hmac
import base64
import hashlib
import logging
import aiohttp
import asyncio
from . import IMessenger
import json

LOGGER = logging.getLogger(__name__)

FEISHU_HOOK_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook'

class FeishuRobot(IMessenger):
    '''飞书机器人消息
    '''
    def __init__(self, ak, sk):
        self.ak = ak
        self.sk = sk
        self.msg_queue = asyncio.Queue()

    def make_sign(self):
        timestamp = round(time.time())
        string_to_sign = '{}\n{}'.format(timestamp, self.sk)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        LOGGER.info('-----ts:%s sign:%s', timestamp, sign)
        return timestamp, sign

    def submit_msg(self, msg):
        ''' 提交文本消息
        '''
        self.msg_queue.put_nowait(msg)

    async def main_loop(self):
        while True:
            msg = await self.msg_queue.get()
            await self.send_msg(msg)

    async def send_msg(self, msg):
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
        headers = {"Content-Type": "application/json"}
        body = json.dumps(data) 
        LOGGER.info("------send feishu request. url:%s body:%s", url, body)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body, headers=headers) as resp:
                body = await resp.text()
                LOGGER.debug("-----got response. status:%s body:%s", resp.status, body) 