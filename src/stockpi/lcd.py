from smbus2 import SMBus, i2c_msg
import logging

LOGGER = logging.getLogger(__name__)

class LCD:
    '''RSCG12864B 功能封装
    '''
    def __init__(self):
        '''初始化
        '''
        self.lcd = SMBus(1)

    def reset(self):
        '''产品复位
        '''
        self.lcd.write_byte(0x00, 0x01)

    def clear(self):
        '''清屏
        '''
        self.lcd.write_byte(0x00, 0x10)

    def switch_on(self):
        '''打开lcd
        '''
        self.lcd.write_byte(0x00, 0x11)

    def switch_off(self):
        '''关闭lcd
        '''
        self.lcd.write_byte(0x00, 0x12)

    def brightness(self, level):
        '''背光亮度 0~255
        '''
        self.lcd.write_byte_data(0x00, 0x13, 0xff)


    def print_str8_xy(self, x, y, s):
        ''' 在x, y处显示8号字符串s. 注意不能显示汉字
            x 0~20 y 0~7
        '''
        px = x * 6
        py = y * 8
        data = [0x24] + [c for c in s.encode('gb2312')] + [0x00]
        self.lcd.i2c_rdwr(i2c_msg.write(0x00, [0x20, px, py]),
                i2c_msg.write(0x00, data))


    def print_str12_xy(self, x, y, s):
        '''在x,y处显示12号字符串
           x 0~17  y 0~3
        '''
        px = x * 7
        py = y * 15
        data = [0x27] + [c for c in s.encode('gb2312')] + [0x00]
        self.lcd.i2c_rdwr(i2c_msg.write(0x00, [0x20, px, py]),
                i2c_msg.write(0x00, data))


    def print_str16_xy(self, x, y, s):
        '''在x, y处显示16号字符串
            x 0~7 y 0~3
        '''
        px = x * 15
        py = y * 15
        data = [0x28] + [i for i in s.encode('gb2312')] + [0x00]
        self.lcd.i2c_rdwr(i2c_msg.write(0x00, [0x20, px, py]),
                i2c_msg.write(0x00, data))

    def print_str16_pxy(self, px, py, s):
        '''在px, py处显示16号字符串
            px 0~127 py 0~63
        '''
        data = [0x28] + [i for i in s.encode('gb2312')] + [0x00]
        self.lcd.i2c_rdwr(i2c_msg.write(0x00, [0x20, px, py]),
                i2c_msg.write(0x00, data))

