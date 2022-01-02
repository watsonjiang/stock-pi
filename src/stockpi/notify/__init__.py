import logging
import abc
import asyncio

LOGGER = logging.getLogger(__name__)

def init():
    '''初始化模块
    '''
    return buildFeishuRobot()

def buildDingTalkRobot():
    from stockpi.notify.dingtalk import DingTalkRobot
    return DingTalkRobot(
        ak='076375a42fd3cecfb17141bdd88b2348021ebb961e2e6c5366d1650d0a699357',
        sk='SEC4c34a9f15cdb8431435861140e5713d0179a8d4506a9b64300a41aa872f45ea1'
    )


def buildFeishuRobot():
    from stockpi.notify.feishu import FeishuRobot
    return FeishuRobot(
        ak = '55d44b27-640e-4322-bda3-f036fa5558cf',
        sk = 'hxTZQI5aGfWkHu0FzPBjeh'
    )

class IMessenger(abc.ABC):
    '''messenger 基类
    '''
    @abc.abstractmethod
    def submit_msg(self, msg):
        '''发送消息
        '''
        raise NotImplementedError


class DummyMessenger(IMessenger):
    '''测试用消息发送
    '''

    def submit_msg(self, msg):
        '''发送消息
        '''
        LOGGER.info('submit msg %s', msg)