'''
实验名称：WiFi遥控四轴飞行器（pyDrone四轴代码）
版本：v1.0
日期：2022.6
作者：01Studio
说明：通过Socket UDP连接，周期接收手柄发来的控制信息，并回传自身姿态信息。
'''

#导入相关模块
import network,socket,time
from machine import Timer
import drone

#构建四轴对象，无头方式
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

#开启AP热点
def startAP():
    
    wlan_ap = network.WLAN(network.AP_IF)
    
    print('Connect pyDrone AP to Config WiFi.')

    #启动热点，名称为pyDrone，不加密。
    wlan_ap.active(True)
    wlan_ap.config(essid='pyDrone',authmode=0)

    while not wlan_ap.isconnected(): #等待AP接入
        
        pass

#启动AP
startAP()

#创建socket UDP接口。
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 2390)) #本地IP：192.168.4.1;端口:2390

#等待设备Socket接入，获取对方IP地址和端口
data,addr = s.recvfrom(128)
print(addr)

#连接对方IP地址和端口
s.connect(addr)
s.setblocking(False) #非阻塞模式

#Socket接收数据
def Socket_fun(tim):
    
    try:
        text=s.recv(128) #单次最多接收128字节
        
        control_data = [None]*4
        
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
                    
        s.send(bytes(state_buf)) #WiFi回传数据
        
    except OSError:
        pass

#开启定时器,周期50ms，执行socket通信接收任务
tim = Timer(1)
tim.init(period=50, mode=Timer.PERIODIC,callback=Socket_fun)


# while True:
#     
#     time.sleep_ms(200)


    
    
