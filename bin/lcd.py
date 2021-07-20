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
time.sleep(1)
lcd.brightness(200)

text = "0123456789abcdefghijklmnopqrstuvwxyz"
lcd.print_str8_xy(0, 0, text)

text = "中华人民共和国"
lcd.print_char12_xy(0, 1, text)

text = "你好，蒋悦心"
lcd.print_char16_xy(0, 2, text)
