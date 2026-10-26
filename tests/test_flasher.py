"""Installer checks use a fake image and never access a serial device."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,sys,tempfile,types,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tinylm_flash',ROOT/'ready-to-flash/flash.py')
flash=importlib.util.module_from_spec(spec);spec.loader.exec_module(flash)
class InstallerTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'tmp').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'tmp');self.folder=Path(self.temp.name)
        (self.folder/'image.bin').write_bytes(b'fake image, never flashed')
        digest=hashlib.sha256((self.folder/'image.bin').read_bytes()).hexdigest()
        (self.folder/'firmware.json').write_text(json.dumps({'file':'image.bin','sha256':digest}))
        self.serial=types.ModuleType('serial');self.tools=types.ModuleType('serial.tools')
        self.tools.list_ports=types.SimpleNamespace(comports=lambda:[])
    def tearDown(self):self.temp.cleanup()
    def run_installer(self,args):
        with patch.object(flash,'ROOT',self.folder), patch.object(sys,'argv',['flash.py']+args), \
             patch.dict(sys.modules,{'serial':self.serial,'serial.tools':self.tools}), \
             patch.object(flash.importlib.metadata,'version',return_value='5.6.0'), \
             patch.object(flash.subprocess,'run') as run, patch.dict(flash.os.environ), \
             patch.object(sys,'path',list(sys.path)), contextlib.redirect_stdout(io.StringIO()):
            flash.main();return run
    def test_check_never_accesses_device(self):
        self.assertFalse(self.run_installer(['--check']).called)
    def test_confirmed_flash_command(self):
        run=self.run_installer(['--port','TEST_PORT','--yes'])
        command=run.call_args.args[0]
        self.assertEqual(command[2:7],['-m','esptool','--chip','esp8266','--port'])
        self.assertIn('TEST_PORT',command);self.assertIn('4MB',command)
        self.assertEqual(command[-2],'0x0');self.assertTrue(run.call_args.kwargs['check'])
    def test_cancel_does_not_write(self):
        with patch('builtins.input',return_value='CANCEL'):
            self.assertFalse(self.run_installer(['--port','TEST_PORT']).called)
    def test_corrupt_image_rejected(self):
        (self.folder/'image.bin').write_bytes(b'corrupt')
        with self.assertRaisesRegex(RuntimeError,'checksum mismatch'):
            self.run_installer(['--port','TEST_PORT','--yes'])
if __name__=='__main__':unittest.main()
