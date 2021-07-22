#!/usr/bin/env python
import sys
import time
sys.path.append('../src')
from stockpi import LCD, Screen, TextBox 

lcd = LCD()
print('open lcd')
lcd.switch_on()
time.sleep(1)
print('clear screen')
lcd.clear()
lcd.brightness(128)

#time.sleep(1)
#text = "0123456789abcdefghijklmnopqrstuvwxyz"
#lcd.print_str8_xy(0, 0, text)

#time.sleep(1)
#text = "中华人民共和国"
#lcd.print_str12_xy(0, 1, text)

#time.sleep(1)
#text = "你好，蒋悦心"
#lcd.print_str16_xy(0, 2, text)

screens = []
s1 = Screen()
text_gen = lambda: time.strftime("%Y-%m-%d", time.localtime())
s1.add_component(TextBox(30, 16, text_gen, 16))
text_gen = lambda: time.strftime("%H:%M:%S", time.localtime())
s1.add_component(TextBox(30, 32, text_gen, 16))
screens.append(s1)

s2 = Screen()
text_gen = lambda: '卧龙电驱(sh000001)'
s2.add_component(TextBox(0, 0, text_gen, 12))
text_gen = lambda: '当前价格: 12.30'
s2.add_component(TextBox(0, 16, text_gen, 12))
text_gen = lambda: '最高价格: 19.30'
s2.add_component(TextBox(0, 32, text_gen, 12))
text_gen = lambda: '最低价格: 19.30'
s2.add_component(TextBox(0, 48, text_gen, 12))
screens.append(s2)

screen_hold = 10 #每屏停留时间秒
idx = 0
screen_stay_cnt = 0
while True:
  s = screens[idx]
  s.render(lcd)
  time.sleep(1)
  screen_stay_cnt += 1
  if screen_stay_cnt == screen_hold:
    idx = (idx + 1) % len(screens)
    lcd.clear()
    screen_stay_cnt = 0

      
