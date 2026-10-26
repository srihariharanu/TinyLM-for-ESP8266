import ctypes as c
from ctypes import wintypes as w
import time

class GUID(c.Structure):
    _fields_=[('d1',w.DWORD),('d2',w.WORD),('d3',w.WORD),('d4',c.c_ubyte*8)]
class Interface(c.Structure):
    _fields_=[('guid',GUID),('description',w.WCHAR*256),('state',w.DWORD)]
class SSID(c.Structure):
    _fields_=[('length',w.DWORD),('data',c.c_ubyte*32)]
class ConnectionHead(c.Structure):
    _fields_=[('state',w.DWORD),('mode',w.DWORD),('profile',w.WCHAR*256),('ssid',SSID)]
class Params(c.Structure):
    _fields_=[('mode',c.c_int),('profile',w.LPCWSTR),('ssid',c.c_void_p),('bssids',c.c_void_p),('bss',c.c_int),('flags',w.DWORD)]
class TemporaryWifi:
    def __init__(self):
        self.dll=c.WinDLL('wlanapi.dll');self.handle=w.HANDLE()
        self.dll.WlanOpenHandle.argtypes=[w.DWORD,c.c_void_p,c.POINTER(w.DWORD),c.POINTER(w.HANDLE)]
        self.dll.WlanEnumInterfaces.argtypes=[w.HANDLE,c.c_void_p,c.POINTER(c.c_void_p)]
        self.dll.WlanQueryInterface.argtypes=[w.HANDLE,c.POINTER(GUID),w.DWORD,c.c_void_p,c.POINTER(w.DWORD),c.POINTER(c.c_void_p),c.POINTER(w.DWORD)]
        self.dll.WlanConnect.argtypes=[w.HANDLE,c.POINTER(GUID),c.POINTER(Params),c.c_void_p]
        self.dll.WlanFreeMemory.argtypes=[c.c_void_p]
        self.dll.WlanCloseHandle.argtypes=[w.HANDLE,c.c_void_p]
        version=w.DWORD();self.check(self.dll.WlanOpenHandle(2,None,c.byref(version),c.byref(self.handle)))
        pointer=c.c_void_p();self.check(self.dll.WlanEnumInterfaces(self.handle,None,c.byref(pointer)))
        try:
            count=c.cast(pointer,c.POINTER(w.DWORD))[0]
            interfaces=[Interface.from_buffer_copy(c.string_at(pointer.value+8+i*c.sizeof(Interface),c.sizeof(Interface))) for i in range(count)]
            connected=[x for x in interfaces if x.state==1]
            if not connected: raise RuntimeError('No connected Wi-Fi interface is available to restore after testing.')
            self.guid=connected[0].guid
        finally:self.dll.WlanFreeMemory(pointer)
        original=self.current()
        self.original_profile=original['profile'];self.original_ssid=original['ssid'];self.switched=False
        if not self.original_profile:raise RuntimeError('The original network has no saved profile. Network test skipped.')
    def check(self,status):
        if status:raise OSError(status,c.FormatError(status))
    def current(self):
        size=w.DWORD();pointer=c.c_void_p();typ=w.DWORD()
        status=self.dll.WlanQueryInterface(self.handle,c.byref(self.guid),7,None,c.byref(size),c.byref(pointer),c.byref(typ))
        if status:return {'profile':'','ssid':'','state':0}
        try:
            obj=c.cast(pointer,c.POINTER(ConnectionHead)).contents
            return {'profile':obj.profile,'ssid':bytes(obj.ssid.data[:obj.ssid.length]).decode('utf-8',errors='replace'),'state':obj.state}
        finally:self.dll.WlanFreeMemory(pointer)
    def connect(self,mode,profile):
        args=Params(mode,profile,None,None,1,0)
        self.check(self.dll.WlanConnect(self.handle,c.byref(self.guid),c.byref(args),None))
    def wait_for(self,ssid,timeout=18):
        until=time.monotonic()+timeout
        while time.monotonic()<until:
            if self.current()['ssid']==ssid:return True
            time.sleep(.25)
        return False
    def __enter__(self):
        xml='''<?xml version="1.0"?><WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1"><name>TinyLM-Temporary-Test</name><SSIDConfig><SSID><name>TinyLM-Offline</name></SSID></SSIDConfig><connectionType>ESS</connectionType><connectionMode>manual</connectionMode><MSM><security><authEncryption><authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX></authEncryption><sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>TinyLM8266</keyMaterial></sharedKey></security></MSM></WLANProfile>'''
        self.switched=True
        try:
            self.connect(1,xml)
            if not self.wait_for('TinyLM-Offline'):raise TimeoutError('ESP8266 Wi-Fi hotspot did not connect.')
            return self
        except BaseException:
            self.restore();raise
    def restore(self):
        if self.switched:
            self.connect(0,self.original_profile)
            if not self.wait_for(self.original_ssid):raise RuntimeError('Original Wi-Fi did not reconnect automatically.')
            self.switched=False
    def __exit__(self,*args):
        try:self.restore()
        finally:self.dll.WlanCloseHandle(self.handle,None)
if __name__=='__main__':
    obj=TemporaryWifi()
    print('Temporary-profile API ready; original Wi-Fi connection can be restored.')
    obj.dll.WlanCloseHandle(obj.handle,None)
