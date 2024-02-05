# 温度湿度传感器测试
import asyncio
import logging
import time

from RPi import GPIO

# 使用GPIO17引脚驱动
PIN = 17
GPIO.setmode(GPIO.BCM)  # 设置为BCM编号模式


async def _delay_in_ms(t):  # 毫秒级延时函数
    await asyncio.sleep(t / 1000)


def _wait_for_edge_in_time(pin: int, edge: int, time_in_ms: int):
    """
    边缘捕获.
    """
    t_start = time.time()
    rst = GPIO.wait_for_edge(pin, edge, timeout=time_in_ms)
    logging.info('-----rst:{}'.format(rst))
    # GPIO.wait_for_edge(pin, edge)
    t_cost_ms = (time.time() - t_start) * 1000
    if t_cost_ms > time_in_ms:
        raise TimeoutError('time cost(ms): {}'.format(t_cost_ms))


def _wait_for_dht_start():
    """
    等待dht数据回传开始信号.
    """
    _wait_for_edge_in_time(PIN, GPIO.FALLING, 1)  # DHT开始响应
    _wait_for_edge_in_time(PIN, GPIO.RISING, 1)
    _wait_for_edge_in_time(PIN, GPIO.FALLING, 1)


def _wait_for_dht_data():
    """
    等待dht回传数据.
    """
    _wait_for_edge_in_time(PIN, GPIO.RISING, 1)
    t_time = time.time()
    _wait_for_edge_in_time(PIN, GPIO.FALLING, 1)
    t_cost_us = (time.time() - t_time) * 1000000
    if t_cost_us > 50:
        return 1
    return 0


def _parse_int(data: list[int]):
    i = 0
    if len(data) != 8:
        raise ValueError('data size must be 8.')
    for c in reversed(range(0, 8)):
        i = i + data[c] * 2 ** c
    return i


def _unpack_dht_data(raw: list[int]):
    """
    解码数据
    """
    rh1 = _parse_int(raw[0:8])
    rh2 = _parse_int(raw[8:16])
    temp1 = _parse_int(raw[16:24])
    temp2 = _parse_int(raw[24:32])
    chk = _parse_int(raw[32:40])

    s = (rh1 + rh2 + temp1 + temp2) % 256
    if s != chk:
        raise ValueError('check sum error. sum:{} checksum:{}'.format(s, chk))

    return rh1 + rh2 * 0.1, temp1 + temp2 * 0.1


async def read_device():
    GPIO.setup(PIN, GPIO.OUT)  # 设置GPIO口为输出模式
    await _delay_in_ms(10)  # 延时1毫秒, 初始化

    GPIO.output(PIN, GPIO.LOW)  # 拉低电平
    await _delay_in_ms(20)  # 延时,
    GPIO.output(PIN, GPIO.HIGH)  # 恢复高电平, 让DHT11检测到启动信号

    GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 设置GPIO口为输入模式, 准备接收DHT11的数据

    _wait_for_dht_start()

    raw = []
    # data transmit start.
    for _ in range(0, 40):  # 40bit in total
        raw.append(_wait_for_dht_data())

    rh, temp = _unpack_dht_data(raw)

    logging.info('设备响应成功, 湿度:{}, 温度:{}'.format(rh, temp))


if __name__ == '__main__':
    try:
        asyncio.run(read_device())
    except Exception:
        logging.exception("unexpected exception.")

    GPIO.cleanup()
