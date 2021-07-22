import datetime
from smbus2 import SMBus, i2c_msg
import logging
import abc
import time
import pandas as pd


from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select

from stockpi.model import CompanyInfo, HqHistory

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
        self.lcd.write_byte_data(0x00, 0x13, level)


    def print_str8_xy(self, x, y, s):
        ''' 在x, y处显示8号字符串s. 注意不能显示汉字
            x 0~20 y 0~7
        '''
        px = x * 6
        py = y * 8
        self.print_str8_pxy(x, y, s)

    def print_str8_pxy(self, x, y, s):
        '''以px, py像素点为左上角，显示8号字符串
        '''
        data = [0x24] + [c for c in s.encode('gb2312')] + [0x00]
        self.lcd.i2c_rdwr(i2c_msg.write(0x00, [0x20, x, y]),
                i2c_msg.write(0x00, data))


    def print_str12_xy(self, x, y, s):
        '''在x,y处显示12号字符串
           x 0~17  y 0~3
        '''
        px = x * 7
        py = y * 15
        self.print_str12_pxy(px, py, s)
 
    def print_str12_pxy(self, x, y, s):
        '''以px, py像素点为左上角，显示12号字符串
        '''
        data = [0x27] + [c for c in s.encode('gb2312')] + [0x00]
        self.lcd.i2c_rdwr(i2c_msg.write(0x00, [0x20, x, y]),
                i2c_msg.write(0x00, data))


    def print_str16_xy(self, x, y, s):
        '''在x, y处显示16号字符串
            x 0~7 y 0~3
        '''
        px = x * 15
        py = y * 15
        self.print_str16_pxy(px, py, s)

    def print_str16_pxy(self, x, y, s):
        '''在px, py处显示16号字符串
            px 0~127 py 0~63
        '''
        data = [0x28] + [i for i in s.encode('gb2312')] + [0x00]
        self.lcd.i2c_rdwr(i2c_msg.write(0x00, [0x20, x, y]),
                i2c_msg.write(0x00, data))

class IDispComponent(abc.ABC):
   '''显示组件
   '''
   @abc.abstractmethod
   def render(self, lcd):
       '''渲染组件
       '''
       raise NotImplementedError

class TextBox(IDispComponent):
    '''字符串组件
    '''
    def __init__(self, x, y, text_gen, fontSize=8):
        '''以像素点x, y为左上角，显示字符组件
           fontSize 8, 12, 16
        '''
        self.x = x
        self.y = y
        self.text_gen = text_gen
        self.fontSize = fontSize
        

    def render(self, lcd:LCD):
        text = self.text_gen()
        if self.fontSize == 8:
            lcd.print_str8_pxy(self.x, self.y, text)
        elif self.fontSize == 12:
            lcd.print_str12_pxy(self.x, self.y, text)
        elif self.fontSize == 16:
            lcd.print_str16_pxy(self.x, self.y, text)

class TimeScreen(IDispComponent):
    '''时间屏
    '''
    def __init__(self):
        self.components = [
            TextBox(25, 16, self.get_date, 16),
            TextBox(25, 32, self.get_time, 16)
        ]

    def get_date(self):
        return time.strftime("%Y-%m-%d", time.localtime())

    def get_time(self):
        return time.strftime("%H:%M:%S", time.localtime()) 
    
    def render(self, lcd):
        for c in self.components:
            c.render(lcd)

class PriceScreen(IDispComponent):
    '''股票价格信息屏
    '''
    def __init__(self, db_engine, stock_no):
        self.db_engine = db_engine
        self.stock_no = stock_no        
        self.components = [
            TextBox(0, 0, self.get_title, 12),
            TextBox(0, 16, self.get_price, 12),
            TextBox(0, 32, self.get_high, 12),
            TextBox(0, 48, self.get_low, 12),
        ]
        

    def get_title(self):
        with sessionmaker(self.db_engine)() as session:
            company_info = session.query(CompanyInfo).filter(CompanyInfo.stock_no == self.stock_no).one_or_none()
            return f'{company_info.name}({self.stock_no})' 

    def get_price(self):
        with sessionmaker(self.db_engine)() as session:
            latest_price = session.query(HqHistory).filter(HqHistory.stock_no == self.stock_no).order_by(HqHistory.id.desc()).first()
            if latest_price:
               return '当前价格:{}'.format(latest_price.price)    
            return '当前价格:{}'.format(0.0)

    def get_high(self):
        st = select(HqHistory).where(HqHistory.stock_no == self.stock_no)
        df = pd.read_sql_query(st, self.db_engine, parse_dates=['create_time', 'update_time'])
        df = df.set_index('create_time')
        now = datetime.datetime.utcnow()
        start_time = now - datetime.timedelta(seconds=24*60*60)
        win = df['price'][start_time:now]
        if win.count() > 0:
            return '最高价格:{}'.format(win.max())
        else:
            return '最高价格:{}'.format(0.0)

    def get_low(self):
        st = select(HqHistory).where(HqHistory.stock_no == self.stock_no)
        df = pd.read_sql_query(st, self.db_engine, parse_dates=['create_time', 'update_time'])
        df = df.set_index('create_time')
        now = datetime.datetime.utcnow()
        start_time = now - datetime.timedelta(seconds=24*60*60)
        win = df['price'][start_time:now]
        if win.count() > 0:
            return '最低价格:{}'.format(win.min())
        else:
            return '最低价格:{}'.format(0.0)

    def render(self, lcd):
        for c in self.components:
            c.render(lcd)


class LCDManager(object):
    def __init__(self, db_engine, stock_list):
        screens = [
            TimeScreen()
        ] + [PriceScreen(db_engine, stock_no) for stock_no in stock_list]
        self.screens = screens
        self.screen_idx = 0
        self.screen_stay_sec = 0
        self.lcd_device = LCD()
        self.lcd_device.switch_on()
        self.lcd_device.brightness(48)
        self.lcd_device.clear()
        

    def render_screen(self):
        s = self.screens[self.screen_idx]
        s.render(self.lcd_device)
        self.screen_stay_sec += 1
        if self.screen_stay_sec == 10:
            self.screen_idx = (self.screen_idx + 1) % len(self.screens)
            self.lcd_device.clear()
            self.screen_stay_sec = 0

def init(db_engine, stock_list):
    return LCDManager(db_engine, stock_list)