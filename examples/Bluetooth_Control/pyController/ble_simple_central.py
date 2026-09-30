# This example finds and connects to a peripheral running the
# UART service (e.g. ble_simple_peripheral.py).

import bluetooth
import random
import struct
import time
import micropython

import binascii,tftlcd,controller

from ble_advertising import decode_services, decode_name

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)

_UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_CHAR_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_CHAR_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")


#LCD初始化
l = tftlcd.LCD15()

#定义常用颜色
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)

DEEPGREEN = (0,139,0)

#手柄按键初始化
gamepad = controller.CONTROLLER()

#存放搜索到的蓝牙设备数据
macs = []
macs_str = []
names=[]
rssis=[]
addr_types=[]
select = 0 #蓝牙设备选择


class BLESimpleCentral:
    def __init__(self, ble):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        self._reset()

    def _reset(self):
        # Cached name and address from a successful scan.
        self._name = None
        self._addr_type = None
        self._addr = None

        # Callbacks for completion of various operations.
        # These reset back to None after being invoked.
        self._scan_callback = None
        self._conn_callback = None
        self._read_callback = None

        # Persistent callback for when new data is notified from the device.
        self._notify_callback = None

        # Connected device.
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._tx_handle = None
        self._rx_handle = None

        #清屏，白色
        l.fill((255,255,255))

        #画线框
        for i in range(4):
            
            l.drawRect(0, 48*(i+1), 239, 2, BLACK, border=1, fillcolor=BLACK)

    def _irq(self, event, data):
        
        global select
        
        if event == _IRQ_SCAN_RESULT:
            
            addr_type, addr, adv_type, rssi, adv_data = data
            
            if adv_type in (_ADV_IND, _ADV_DIRECT_IND) and _UART_SERVICE_UUID in decode_services(adv_data) and ('pyDrone' in decode_name(adv_data)):
                
                # Found a potential device, remember it and stop scanning.                
                if bytes(addr) not in macs :
                    
                    addr_types.append(addr_type)
                    macs.append(bytes(addr))
                    s = binascii.hexlify(addr)
                    macs_str.append(chr(s[0])+chr(s[1])+':' + chr(s[2])+chr(s[3]) + ':' +chr(s[4])+chr(s[5])+':' + \
                            chr(s[6])+chr(s[7])+':'+chr(s[8])+chr(s[9])+':'+chr(s[10])+chr(s[11]))
                    print(macs_str)
                    names.append(decode_name(adv_data))
                    print(names)
                    rssis.append(str(rssi))
                
                rssis[macs.index(bytes(addr))]=str(rssi) #刷新RSSI

                #列表显示,最多显示5个
                for i in range(min(len(macs),5)):
                    
                    l.printStr(names[i],2,2+i*49,color=(0,0,0),size=2)
                    l.printStr(rssis[i]+' ' if (-10 < rssi) else rssis[i],140,8+i*49,color=(0,0,0),size=2)
                    l.printStr(macs_str[i],2,28+i*49,color=(0,0,0),size=1)
                
                if -40 <= rssi <0:
                    l.Picture(180, 2+macs.index(bytes(addr))*49, 'picture/signal_3.jpg')
                if -75 <= rssi < -40:
                    l.Picture(180, 2+macs.index(bytes(addr))*49, 'picture/signal_2.jpg')
                if -99 <= rssi < -75:
                    l.Picture(180, 2+macs.index(bytes(addr))*49, 'picture/signal_1.jpg')
                
                if select==0:
                    
                    l.Picture(219, 9+0*49, 'picture/arrow.jpg')                    
                
                key_value = gamepad.read()
                if key_value[5] == 0 : #上键
                
                    l.Picture(219, 9+select*49, 'picture/arrow_none.jpg')
                    select = select - 1            
                    if select < 0:
                        select =0
                    l.Picture(219, 9+select*49, 'picture/arrow.jpg')

                if key_value[5] == 4 : #下键
                    l.Picture(219, 9+select*49, 'picture/arrow_none.jpg')
                    select = select + 1            
                    if select>min(len(macs)-1,4):                
                        select = min(len(macs)-1,4)
                    l.Picture(219, 9+select*49, 'picture/arrow.jpg')
                
                if key_value[6] == 32: #start键
                    
                    print(select)
                    self._addr_type = addr_types[select]
                    self._addr = macs[select] # Note: addr buffer is owned by caller so need to copy it.
                    self._name = names[select] or "?"
                    self._ble.gap_scan(None)                    

        elif event == _IRQ_SCAN_DONE:
            
            if self._scan_callback:
                if self._addr:
                    # Found a device during the scan (and the scan was explicitly stopped).
                    self._scan_callback(self._addr_type, self._addr, self._name)
                    self._scan_callback = None
                else:
                    # Scan timed out.
                    self._scan_callback(None, None, None)

        elif event == _IRQ_PERIPHERAL_CONNECT:
            
            # Connect successful.
            conn_handle, addr_type, addr = data
            if addr_type == self._addr_type and addr == self._addr:
                self._conn_handle = conn_handle
                self._ble.gattc_discover_services(self._conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            
            # Disconnect (either initiated by us or the remote end).
            conn_handle, _, _ = data
            if conn_handle == self._conn_handle:
                # If it was initiated by us, it'll already be reset.
                self._reset()

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            print("service", data)
            if conn_handle == self._conn_handle and uuid == _UART_SERVICE_UUID:
                self._start_handle, self._end_handle = start_handle, end_handle

        elif event == _IRQ_GATTC_SERVICE_DONE:
            
            # Service query complete.
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(
                    self._conn_handle, self._start_handle, self._end_handle
                )
            else:
                print("Failed to find uart service.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self._conn_handle and uuid == _UART_RX_CHAR_UUID:
                self._rx_handle = value_handle
            if conn_handle == self._conn_handle and uuid == _UART_TX_CHAR_UUID:
                self._tx_handle = value_handle

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            
            #l.Picture(0, 0, 'picture/Car.jpg')
            #填充白色
            l.fill(WHITE)
            # Characteristic query complete.
            if self._tx_handle is not None and self._rx_handle is not None:
                # We've finished connecting and discovering device, fire the connect callback.
                if self._conn_callback:
                    self._conn_callback()
            else:
                print("Failed to find uart rx characteristic.")

        elif event == _IRQ_GATTC_WRITE_DONE:
            
            conn_handle, value_handle, status = data
            print("TX complete")

        elif event == _IRQ_GATTC_NOTIFY:
            
            conn_handle, value_handle, notify_data = data            
            if conn_handle == self._conn_handle and value_handle == self._tx_handle:
                if self._notify_callback:
                    self._notify_callback(notify_data)

    # Returns true if we've successfully connected and discovered characteristics.
    def is_connected(self):
        return (
            self._conn_handle is not None
            and self._tx_handle is not None
            and self._rx_handle is not None
        )

    # Find a device advertising the environmental sensor service.
    def scan(self, callback=None):
        self._addr_type = None
        self._addr = None
        self._scan_callback = callback
        #self._ble.gap_scan(2000, 30000, 30000)
        self._ble.gap_scan(0, 30000, 30000) #一直扫描，不停止。

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type=None, addr=None, callback=None):
        self._addr_type = addr_type or self._addr_type
        self._addr = addr or self._addr
        self._conn_callback = callback
        if self._addr_type is None or self._addr is None:
            return False
        self._ble.gap_connect(self._addr_type, self._addr)
        return True

    # Disconnect from current device.
    def disconnect(self):
        if not self._conn_handle:
            return
        self._ble.gap_disconnect(self._conn_handle)
        self._reset()

    # Send data over the UART
    def write(self, v, response=False):
        if not self.is_connected():
            return
        self._ble.gattc_write(self._conn_handle, self._rx_handle, v, 1 if response else 0)

    # Set handler for when data is received over the UART.
    def on_notify(self, callback):
        self._notify_callback = callback

#扫描连接函数
def ble_connect():
    
    ble = bluetooth.BLE()
    central = BLESimpleCentral(ble)

    not_found = False
    
    def on_scan(addr_type, addr, name):
        if addr_type is not None:
            print("Found peripheral:", addr_type, addr, name)
            central.connect()
        else:
            global not_found
            not_found = True
            print("No peripheral found.")

    central.scan(callback=on_scan)

    # Wait for connection...
    while not central.is_connected():
        time.sleep_ms(100)
        if not_found:
            break

    print("Connected")

    
    #接收信息处理
    def on_rx(v):
        
        #print("RX", len(v))
        state_buf = [None]*9
        
        #解码接收到的9个数据
        for i in range(9):
                
                state_buf[i] = v[i*2]*256+v[i*2+1] - 32768
                
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

    central.on_notify(on_rx)

    with_response = False

    while central.is_connected():

        try:
            a = gamepad.read() #读取手柄数据
            #print("TX", a) #打印手柄原始数据
            central.write(bytes(a), with_response) #发送手柄数据
        except:
            print("TX failed")
        time.sleep_ms(400 if with_response else 50) #50ms发送一次
        
    print("Disconnected")

if __name__ == "__main__":
    ble_connect()
