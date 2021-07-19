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
    b.i2c_rdwr(i2c_msg.write(0x00, [0x20, x, y]),
              i2c_msg.write(0x00, [0x25, c, 0x00]))

def print_char1212_xy(x, y, c):
    ''' x 0~7 y 0~3
    '''
    px = x * 15
    py = y * 15
    data = [0x25] + c.encode('gb2312') + [0x00]
    b.i2c_rdwr(i2c_msg.write(0x00, [0x20, x, y]),
              i2c_msg.write(0x00, data))


for i in range(0, 30):
  time.sleep(1)
  x = i % 18
  y = i // 18
  print('move to ', x, y, 'write ', chr(0x30+i))
  print_char612_xy(x, y, 0x30+i)


text = "中华人民共和国"
for i in text:
  time.sleep(1)
  x = i % 7
  y = i // 7 + 2
  print('move to ', x, y, 'write ', i)
  print_char1212_xy(x, y, i)

