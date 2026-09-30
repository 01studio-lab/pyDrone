'''
实验名称：WiFi遥控四轴飞行器（pyController手柄代码）
版本：v1.0
日期：2022.6
作者：01Studio
说明：通过Socket UDP连接四轴，周期发送控制信息，将接收到四轴的姿态信息
      显示在LCD屏。
'''

#导入相关模块
import network,usocket,time,controller
from machine import Pin,Timer
import tftlcd

# # 公司WiFi热点、IP和端口信息。
SSID = 'pyDrone'
PASSWORD = ''
addr=('192.168.4.1',2390) #服务器IP和端口

#自身IP
ip_local = ''

#构建手柄对象
gamepad = controller.CONTROLLER()

#LCD初始化
l = tftlcd.LCD15()

#定义常用颜色
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)
DEEPGREEN = (0,139,0)

#清屏，白色
l.fill(WHITE)

#WIFI连接函数
def WIFI_Connect():
    
    global ip_local
    
    WIFI_LED=Pin(46, Pin.OUT) #初始化WIFI指示灯

    wlan = network.WLAN(network.STA_IF) #STA模式
    wlan.active(True)                   #激活接口
    start_time=time.time()              #记录时间做超时判断

    if not wlan.isconnected():
        print('Connecting to network...')
        l.printStr('Connecting WiFi...',10,10,color=BLUE,size=2)
        l.printStr('SSID: pyDrone',10,60,color=BLACK,size=2)
        l.printStr('KEY: None',10,100,color=BLACK,size=2)
        wlan.connect(SSID,PASSWORD) #输入WIFI账号密码

        while not wlan.isconnected():

            #LED闪烁提示
            WIFI_LED.value(1)
            time.sleep_ms(300)
            WIFI_LED.value(0)
            time.sleep_ms(300)

            #超时判断,15秒没连接成功判定为超时
            if time.time()-start_time > 15 :
                print('WIFI Connected Timeout!')
                wlan.active(False)
                break

    if wlan.isconnected():
        #LED点亮
        WIFI_LED.value(1)

        #串口打印信息
        print('network information:', wlan.ifconfig())
        
        ip_local = wlan.ifconfig()[0]
        
        return True

    else:
        return False

#判断WIFI是否连接成功
while not WIFI_Connect():
    
    pass

#清屏，白色
l.fill(WHITE)

#创建socket UDP接口。
s=usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
s.bind((ip_local, 2390)) #本地端口2390
s.setblocking(False) #非阻塞模式
s.connect(addr)

#Socket接收数据
def Socket_fun(tim):

    try:
        text = s.recv(128) #单次最多接收128字节
#         print(text)
        
        state_buf = [None]*9
        
        #解码接收到的9个数据
        for i in range(9):
                
                state_buf[i] = text[i*2]*256+text[i*2+1] - 32768
                
        print(state_buf)
        
        #飞控姿态 ROL、PIT、YAW数据显示。
        l.printStr('ROL: '+str('%.2f'%(state_buf[0]/100))+'  ',10,10,color=BLACK,size=2)
        l.printStr('PIT: '+str('%.2f'%(state_buf[1]/100))+'  ',10,40,color=BLACK,size=2)
        l.printStr('YAW: '+str('%.2f'%(state_buf[2]/100))+'  ',10,70,color=BLACK,size=2)

        #遥控器控制量显示 ROL、PIT、YAW、THRUST
        l.printStr('ROL: '+str(int(state_buf[3]/10))+'   ',10,110,color=BLUE,size=2)
        l.printStr('PIT: '+str(int(state_buf[4]/10))+'   ',130,110,color=BLUE,size=2)
        l.printStr('YAW: '+str(int(state_buf[5]/200))+'   ',10,140,color=BLUE,size=2)
        l.printStr('THR: '+str(state_buf[6]*2-100)+'   ',130,140,color=BLUE,size=2)

        #四轴相对高度
        l.printStr('ALT: ' + str('%.2f'%(state_buf[8]/100))+' M   ',10,180,color=DEEPGREEN,size=2)
        
        #电池电量显示，低于3.1V表示低电量，红色字体显示。
        if state_buf[7] > 310 :
            l.printStr('BAT: '+str('%.2f'%(state_buf[7]/100))+' V      ',10,210,color=DEEPGREEN,size=2)
            
        else: #低电量
            l.printStr('BAT: '+str('%.2f'%(state_buf[7]/100))+' V (LOW)',10,210,color=RED,size=2)
            
    except OSError:
        pass


#开启定时器，周期50ms，执行socket通信接收任务
tim = Timer(1)
tim.init(period=50, mode=Timer.PERIODIC,callback=Socket_fun)


while True:
    
    v = gamepad.read() #获取手柄数据
    
    s.send(bytes(v)) #Socket发送数据
    
    time.sleep_ms(50) #发送间隔


    
    
