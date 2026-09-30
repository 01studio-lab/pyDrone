# pyDrone

[English](README.md) | **中文**

![banner](assets/banner_zh.png)

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

pyDrone v1.1 [点击购买>>](https://item.taobao.com/item.htm?id=678913113280)

![img](hardware/overview/v1.1/front.png)

![img](hardware/overview/v1.1/back.png)

● 主控：ESP32-S3-WROOM-1 （N16R8; Flash:16MBytes,RAM:8MBytes）支持WiFi/BLE  
● 4 x LED（充电指示灯【橙色】，电源指示灯【红色】，校准指示灯【蓝色】，联网指示灯【绿色】）  
● 4 x 716空心杯电机  
● 2 x 按键（1个复位键+1个功能键）  
● 1 x IMU（QMI8658A）  
● 1 x 气压计（SPA06-003）  
● 1 x 电子罗盘（QMC5883P）  
● 1 x TYPE-C（下载/REPL调试/供电）  
● 1 x 模块扩展接口（2x8Pin 2.0mm间距排母）  
● 1 x 航模锂电池400mAh/3.7V（板载充电电路）  
● 1 x 电池盖板  
● 1 x 保护圈 

## 目录结构

```
pyDrone/
├── examples/          # 示例代码
├── hardware/          # 硬件设计资料（原理图、封装、3D 模型）
├── firmware/          # 固件
├── app/               # Android APP
├── CHANGELOG.md       # 更新日志
├── LICENSE
├── README.md          # 英文说明
└── README_zh.md       # 中文说明
```

## 开发资源

- [Wiki（教程文档）](https://wiki.01studio.cc/docs/pydrone)

## 更新日志

请参阅 [CHANGELOG.md](CHANGELOG.md)。

## 技术支持

遇到问题可通过以下方式获取支持：

**邮件联系**：发送邮件至 [support@01studio.cc](mailto:support@01studio.cc)。     