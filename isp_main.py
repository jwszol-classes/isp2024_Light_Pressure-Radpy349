from m5stack import *
from m5stack_ui import *
from uiflow import *
from m5ui import M5ChartGraph, M5BarGraph
from IoTcloud.AWS import AWS
from libs.json_py import *
import time
import unit


screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xFFFFFF)
dlight_0 = unit.get(unit.DLIGHT, (14,13))
bpsv11_0 = unit.get(unit.BPS_QMP, unit.PORTA)


test = None



graph0 = M5ChartGraph(45, 0, 200, 100, 40, 0, 300, M5ChartGraph.LINE, 0xFFFFFF, 0x0288FB, 0.5, 5)
graph1 = M5ChartGraph(45, 120, 200, 100, 40, 900, 1100, M5ChartGraph.LINE, 0xFFFFFF, 0x0288FB, 0.5, 5)




rtc.settime('ntp', host='us.pool.ntp.org', tzone=2)
aws = AWS(things_name='M5stack_sobota', host='a2pvn903w589z0-ats.iot.us-east-1.amazonaws.com', port=8883, keepalive=60, cert_file_path="/flash/res/sobotacertificate.pem.crt", private_key_path="/flash/res/sobotaprivate.pem.key")
aws.start()
while True:
  graph0.addSample(dlight_0.get_lux())
  graph1.addSample(bpsv11_0.pressure)
  aws.publish(str('core2'),str((py_2_json({'light':(dlight_0.get_lux()),'pressure':(bpsv11_0.pressure),'temp':(bpsv11_0.temperature),'timestamp':(rtc.datetime())}))))
  wait(4)
  wait_ms(2)