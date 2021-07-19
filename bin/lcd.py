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


def print_char_xy(x, y, c):
   msg1 = i2c_msg()
   msg1.write(0x00, [0x20, x, y]) 
   msg2 = i2c_msg()
   msg2.write(0x00, [0x24, c, 0x00])
   b.i2c_rdwr(msg1, msg2)

j = 0
for i in range(0, 62):
  time.sleep(1)
  #x = 5 * (i % 25) + 1
  x = 10 * (i % 3) + 1
  #y = 7 * (i // 25) + 1
  y = 10 * (i % 3) + 1
  print('move to ', x, y, 'write ', chr(0x30+j))
  print_char_xy(x, y, 0x30+j)
  j = j + 1
  if j == ord('z'):
     j == 0