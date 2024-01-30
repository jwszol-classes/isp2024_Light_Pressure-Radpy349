import os, sys, io
import M5
from M5 import *
from hardware import *
from unit import DLightUnit
from unit import ENVUnit
import time



i2c0 = None
i2c1 = None
env3_0 = None
dlight_0 = None


def setup():
  global i2c0, i2c1, env3_0, dlight_0

  M5.begin()
  Widgets.fillScreen(0x222222)

  i2c0 = I2C(0, scl=Pin(36), sda=Pin(26), freq=100000)
  i2c1 = I2C(1, scl=Pin(13), sda=Pin(14), freq=100000)
  dlight_0 = DLightUnit(i2c0)
  env3_0 = ENVUnit(i2c=i2c1, type=3)
  dlight_0.configure(dlight_0.CONTINUOUSLY, dlight_0.H_RESOLUTION_MODE)


def loop():
  global i2c0, i2c1, env3_0, dlight_0
  M5.update()
  print(str((env3_0.read_pressure())))
  print(str((dlight_0.get_lux())))
  time.sleep(1)


if name == 'main':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
        print("please update to latest firmware")