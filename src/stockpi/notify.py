import requests
import hmac, base64, time, hashlib, urllib
import json
import logging
import abc

LOGGER = logging.getLogger(__name__)

DING_TALK_SEND_URL = 'https://oapi.dingtalk.com/robot/send'

def init():
    '''初始化模块
    '''
    return DingTalkRobot( 
                ak='076375a42fd3cecfb17141bdd88b2348021ebb961e2e6c5366d1650d0a699357',
                sk='SEC4c34a9f15cdb8431435861140e5713d0179a8d4506a9b64300a41aa872f45ea1'
           )

class IMessenger(abc.ABC):
   '''messenger 基类
   '''
   @abc.abstractmethod
   def send_msg(self, msg):
       '''发送消息
       '''
       raise NotImplementedError

class DummyMessenger(IMessenger):
    '''测试用消息发送
    '''
    def send_msg(self, msg):
        '''发送消息
        '''
        LOGGER.info('send msg %s', msg)

class DingTalkRobot(IMessenger):
    '''钉钉机器人消息
    '''
    def __init__(self, ak, sk):
        self.ak = ak
        self.sk = sk

    def make_sign(self):
        timestamp = str(round(time.time() * 1000))
        secret = self.sk
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        LOGGER.info('-----ts:%s sign:%s', timestamp, sign)
        return timestamp, sign

    def send_msg(self, msg):
        ''' 发送文本消息
        '''
        data = {
            'msgtype': 'text',
            'text': {
                'content': msg
            },
            'at': {
                'atMobiles': [],
                'isAtAll': False 
            }
        }
        ts, sign = self.make_sign()
        url = "{}?access_token={}&timestamp={}&sign={}".format(DING_TALK_SEND_URL, self.ak, ts, sign)
        LOGGER.info("------data:%s", data)
        rsp = requests.post(url, json=data)
        LOGGER.debug("-----rsp:%s", rsp.json()) 
         
         
