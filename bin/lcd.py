from smbus2 import SMBus, i2c_msg
import time

b = SMBus(1)

#print('reset')
#b.write_byte(0x00, 0x01)
#time.sleep(1)
print('open lcd')
b.write_byte(0x00, 0x11)
time.sleep(1)
print('clear screen')
b.write_byte(0x00, 0x10)
time.sleep(1)
print('switch light ', 0xff)
b.write_byte_data(0x00, 0x13, 0xff)


def print_char57_xy(x, y, c):
    ''' x 0~20 y 0~7
    ''' 
    px = x * 6
    py = y * 8
    b.i2c_rdwr(i2c_msg.write(0x00, [0x20, px, py]),
              i2c_msg.write(0x00, [0x24, c, 0x00]))

def print_char612_xy(x, y, c):
    ''' x 0~17  y 0~3
    '''
    px = x * 7
    py = y * 15
    b.i2c_rdwr(i2c_msg.write(0x00, [0x20, px, py]),
              i2c_msg.write(0x00, [0x25, ord(c), 0x00]))

def print_char1212_xy(x, y, c):
    ''' x 0~7 y 0~3
    '''
    px = x * 15
    py = y * 15
    data = [0x27] + [i for i in c.encode('gb2312')] + [0x00]
    print(px, py, data)
    b.i2c_rdwr(i2c_msg.write(0x00, [0x20, px, py]),
              i2c_msg.write(0x00, data))

def print_char1616_xy(x, y, c):
    ''' x 0~5 y 0~2
    '''
    px = x * 20
    py = y * 20
    data = [0x28] + [i for i in c.encode('gb2312')] + [0x00]
    print(px, py, data)
    b.i2c_rdwr(i2c_msg.write(0x00, [0x20, px, py]),
              i2c_msg.write(0x00, data))



text="0123456789abcdefgh"
for n, i in enumerate(text):
  time.sleep(0.3)
  x = n % 18
  y = n // 18
  print('move to ', x, y, 'write ', i)
  print_char612_xy(x, y, i)


text = "你好，蒋悦心"
for n, i in enumerate(text):
  time.sleep(0.3)
  x = n % 7
  y = n // 7 + 1
  print('move to ', x, y, 'write ', i)
  print_char1212_xy(x, y, i)

text = "你好，蒋大怪"
for n, i in enumerate(text):
  time.sleep(0.3)
  x = n % 6
  y = n // 6 + 2
  print('move to ', x, y, 'write ', i)
  print_char1616_xy(x, y, i)


