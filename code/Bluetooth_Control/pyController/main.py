'''
实验名称：pyDrone蓝牙遥控（pyController手柄代码）
版本：v1.0
日期：2022.6
作者：01Studio
说明：pyController做蓝牙主机，pyDrone做从机，手柄搜索到'pyDrone'后发起连接，然后控制。
'''

#导入BLE主机模块
import ble_simple_central

while True:
    
    #执行主机扫描连接代码
    ble_simple_central.ble_connect()