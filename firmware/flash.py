"""TinyLM ESP8266 installer. Copyright (c) 2026 Sri Hariharan U. Apache-2.0."""
import argparse,hashlib,importlib.metadata,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description='Install experimental TinyLM on a 4 MB ESP8266')
    p.add_argument('--setup',action='store_true',help='Install flashing tool locally; internet required once')
    p.add_argument('--port',help='USB port, e.g. COM3 or /dev/ttyUSB0')
    p.add_argument('--check',action='store_true',help='Verify image only, without device access')
    p.add_argument('--yes',action='store_true',help='Confirm replacing selected device firmware')
    a=p.parse_args()
    meta=json.loads((ROOT/'firmware.json').read_text())
    image=ROOT/meta['file']
    if hashlib.sha256(image.read_bytes()).hexdigest()!=meta['sha256']:
        raise RuntimeError('Firmware checksum mismatch. Download a fresh release.')
    print('TinyLM for ESP8266 - experimental\nFirmware integrity verified.')
    if a.check:return
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    for name in ('tmp','cache','tools'):(ROOT/name).mkdir(exist_ok=True)
    os.environ['TEMP']=os.environ['TMP']=str(ROOT/'tmp')
    sys.path.insert(0,str(ROOT/'tools'))
    if a.setup:
        subprocess.run([sys.executable,'-B','-m','pip','install','--upgrade','--target',str(ROOT/'tools'),
                        '--cache-dir',str(ROOT/'cache'),'-r',str(ROOT/'requirements-flash.txt')],check=True)
        importlib.invalidate_caches()
    try:
        version=importlib.metadata.version('esptool')
        from serial.tools import list_ports
    except ImportError:raise RuntimeError('Run with --setup once while online.')
    if version!='5.6.0':raise RuntimeError('Use --setup to install esptool 5.6.0 locally.')
    port=a.port
    if not port:
        ports=list(list_ports.comports())
        if not ports:raise RuntimeError('No USB serial port. Check the data cable and USB driver.')
        for i,item in enumerate(ports,1):print(f'{i}. {item.device}: {item.description}')
        selected=input('Choose the ESP8266 port number: ').strip()
        if not selected.isdigit() or not 1<=int(selected)<=len(ports):raise RuntimeError('Invalid port selection.')
        port=ports[int(selected)-1].device
    print(f'Target: {port}. Requires ESP8266 with 4 MB flash. Existing application will be replaced.')
    if not a.yes and input('Type FLASH to continue: ').strip()!='FLASH':
        print('Cancelled.');return
    env=dict(os.environ);env['PYTHONPATH']=str(ROOT/'tools')
    subprocess.run([sys.executable,'-B','-m','esptool','--chip','esp8266','--port',port,'--baud','115200',
                    'write-flash','--flash-mode','dout','--flash-size','4MB','0x0',str(image)],env=env,check=True)
    print('Done. Press RESET. Join TinyLM-Offline using TinyLM8266.')
    print('Open http://192.168.4.1/ and enter a display name.')
if __name__=='__main__':
    try:main()
    except (Exception,KeyboardInterrupt) as error:
        print(f'Installation stopped: {error}',file=sys.stderr);sys.exit(1)
