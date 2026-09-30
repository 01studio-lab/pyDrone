'''
实验名称：pyDrone蓝牙遥控（pyDrone四轴代码）
版本：v1.0
日期：2022.6
作者：01Studio
说明：pyController做蓝牙主机，pyDrone做从机，手柄搜索到'pyDrone'后发起连接，然后控制。
'''

import bluetooth,ble_simple_peripheral,time
import drone

#无头方式
d = drone.DRONE(flightmode = 0)

#水平放置四轴，等待校准通过后蓝灯常亮
while True:
    
    #打印校准信息，当返回3个值均少于5000时校准通过。
    print(d.read_cal_data())
    
    #校准通过
    if d.read_calibrated():
        
        print(d.read_cal_data())
        
        break
    
    time.sleep_ms(100)

#初始化蓝牙BLE从机,广播名称为pyCar
ble = bluetooth.BLE()
p = ble_simple_peripheral.BLESimplePeripheral(ble,name='pyDrone')

#接收到蓝牙数据处理函数
def on_rx(text):
    
    control_data = [None]*4
    
    #接收的蓝牙数据
    #print("RX:", text)
    
    #对收到的手柄8字节数据进行判断
    for i in range(len(text)):
        print(i,text[i])
        
    #将摇杆值转化为飞控控制值。
    for i in range(4):
        if  100 < text[i+1] < 155 :
            control_data[i] = 0
            
        elif text[i+1] <= 100 :      
            control_data[i] = text[i+1] - 100
            
        else:
            control_data[i] = text[i+1] - 155
    
    print('control:',control_data)
            
    #rol:[-100:100],rol:[-100:100],yaw:[-100:100],thr:[-100:100]
    d.control(rol = control_data[0], pit = control_data[1], yaw = control_data[2], thr = control_data[3])

    
    #检测X/Y/A/B按键
    if text[5] == 24: #Y键按下
        print('Y')
        #起飞，起飞后120cm位置悬停。distance范围:30~2000 cm
        d.take_off(distance = 120)
        
    if text[5] == 72: #A键按下
        print('A')
        #降落，允许control
        d.landing()

    if text[5] == 40: #B键按下，可以自己添加功能。
        print('B')
        
    if text[5] == 136: #X键按下,紧急停止
        print('X')
        #降落，不允许control
        d.stop()
        
    
    states = d.read_states()
    print('states: ',states)
    state_buf = [None]*18
    for i in range(9):
        for j in range(2):
            if j == 0:
                state_buf[i*2+j] = int((states[i]+32768)/256)
            else:
                state_buf[i*2+j] = int((states[i]+32768)%256)
                
    p.send(bytes(state_buf)) #蓝牙回传数据
    

#注册从机接收回调函数，收到数据会进入on_rx函数。
p.on_write(on_rx)

#系统会自动广播, 连接断开后重新自动广播。
# while True:
#     
#     time.sleep_ms(200)



