# pyDrone
由01Studio发起的MicroPython开源四轴飞行器项目。  
![pyDrone](https://www.01studio.cc/data/picture/pyDrone.jpg)

## 项目简介
Micropython是指使用python做各类嵌入式硬件设备编程。MicroPython发展势头强劲，01Studio一直致力于Python嵌入式编程，特此推出pyDrone开源项目，旨在让MicroPython变得更加流行。使用MicroPython，你可以轻松地实现四轴飞行器的起飞、降落、悬停、移动、自转等各种姿态和动作。

例：
```python
from drone import DRONE

#构建四轴对象
d = DRONE(flightmode = 0) #无头模式

#使用方法

#起飞
d.takeoff()

#降落
d.landing()

#四轴飞行器姿态控制
d.control(rol = 0, pit = 0, yaw = 0, thr = 0)

...
```

## 硬件资源
● 主控：ESP32-S3-WROOM-1 （N8R8; Flash:8MBytes,RAM:8MBytes）支持WiFi/BLE  
● 4 x LED（充电指示灯【橙色】，电源指示灯【红色】，校准指示灯【蓝色】，联网指示灯【绿色】）  
● 4 x 716空心杯电机  
● 2 x 按键（1个复位键+1个功能键）  
● 1 x 六轴加速度计（MPU6050）  
● 1 x 气压计（SPL06-001）  
● 1 x 电子罗盘（QMC5883L）  
● 1 x OV2640摄像头接口（FPC-24P-0.5MM）  
● 1 x MicroUSB（下载/REPL调试/供电）  
● 1 x 模块扩展接口（2x8Pin 2.0mm间距排母）  
● 1 x 航模锂电池400mAh/3.7V（板载充电电路）  
● 1 x 电池盖板  
● 1 x 保护圈      

## 贡献说明
本项目预设以下文件夹：

### code
示例代码。

### docs
pyCar官方说明文档、MicroPython库文档。  
https://pyDrone.01studio.cc/zh_CN/latest/manual/quickref.html

### firmware
pyDrone的MicroPython固件。  
https://github.com/01studio-lab/micropython/tree/master/ports/esp32/boards/PYDRONE

### hardware
硬件资料，原理图、尺寸图等。

## 贡献用户
【CaptainJacky】 pyDrone项目发起人，负责硬件和MicroPython软件设计。    
【Spring641】pyDrone MicroPython底层开发。    

欢迎参与项目贡献！

## 联系方式
jackey@01studio.cc