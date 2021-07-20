#!/usr/bin/env python
import sys
import time
sys.path.append('../src')
from stockpi import LCD 

lcd = LCD()
print('open lcd')
lcd.switch_on()
time.sleep(1)
print('clear screen')
lcd.clear()
lcd.brightness(200)

#time.sleep(1)
#text = "0123456789abcdefghijklmnopqrstuvwxyz"
#lcd.print_str8_xy(0, 0, text)

#time.sleep(1)
#text = "中华人民共和国"
#lcd.print_str12_xy(0, 1, text)

#time.sleep(1)
#text = "你好，蒋悦心"
#lcd.print_str16_xy(0, 2, text)

#时钟
while True:
  time.sleep(1)
  text = time.strftime("%Y-%m-%d %H:%M:%S", time.time())
  lcd.print_str16_pxy(0, 16, text)
