# 温度湿度传感器测试
import asyncio
import logging
from RPi import GPIO

# 使用GPIO17引脚驱动
PIN = 17
GPIO.setmode(GPIO.BCM)  # 设置为BCM编号模式


async def _delay_in_us(t):  # 微秒级延时函数
    await asyncio.sleep(t / 1000000)


async def read_device():
    GPIO.setup(PIN, GPIO.OUT)  # 设置GPIO口为输出模式
    GPIO.output(PIN, GPIO.HIGH)  # 设置GPIO输出高电平
    await _delay_in_us(10 * 1000)  # 延时10毫秒
    GPIO.output(PIN, GPIO.LOW)  # 设置GPIO输出低电平
    await _delay_in_us(25 * 1000)  # 延时25毫秒, 让DHT11检测到启动信号
    GPIO.output(PIN, GPIO.HIGH)  # 设置GPIO输出高电平
    await _delay_in_us(30)  # 延时30微秒

    GPIO.setup(PIN, GPIO.IN)  # 设置GPIO口为输入模式, 准备接收DHT11的数据

    _delay_in_us(40)
    if GPIO.input(PIN) != GPIO.LOW:  # DHT11拉低总线80us
        raise ValueError("设备未响应")
    _delay_in_us(80)
    if GPIO.input(PIN) != GPIO.HIGH:  # DHT11拉高总线80us, 准备输出数据
        raise ValueError("设备异常响应")

    logging.info('设备响应成功')


if __name__ == '__main__':
    try:
        asyncio.run(read_device())
    except Exception:
        logging.exception("unexpected exception.")
        GPIO.cleanup()
