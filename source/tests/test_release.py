"""Release contract checks independent of device and training dependencies."""
from pathlib import Path
import ast,gzip,hashlib,json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
class ReleaseTests(unittest.TestCase):
    def test_required_source_and_data(self):
        for name in ('LICENSE','NOTICE','CREDITS.md','THIRD_PARTY_NOTICES.md','CONTRIBUTING.md',
                     'train_gru.py','export_gru.py','prepare_focused.py','web/index.html',
                     'firmware/RecurrentLM/weights.h','model/gru-best.pt','model/gru-int8.npz',
                     'data/train-00000-of-00001.parquet','data/prepared-training.json',
                     'third_party/esp8266-arduino-core-3.0.2.zip'):
            self.assertTrue((ROOT/name).is_file(),name)
    def test_apache_license_and_notice(self):
        for root in (ROOT,ROOT.parent/'firmware'):
            self.assertIn('Apache License',(root/'LICENSE').read_text())
            self.assertIn('Sri Hariharan U',(root/'NOTICE').read_text())
            self.assertIn('Copyright 2026 Sri Hariharan U',(root/'LICENSE').read_text())
            self.assertNotIn('[yyyy]',(root/'LICENSE').read_text())
        self.assertEqual(json.loads((ROOT/'package.json').read_text())['license'],'Apache-2.0')
    def test_firmware_integrity(self):
        folder=ROOT.parent/'firmware';m=json.loads((folder/'firmware.json').read_text())
        self.assertEqual(hashlib.sha256((folder/m['file']).read_bytes()).hexdigest(),m['sha256'])
        self.assertEqual(m['chip'],'esp8266');self.assertEqual(m['offset'],'0x0')
    def test_embedded_page_matches_source(self):
        header=(ROOT/'firmware/RecurrentLM/web_ui.h').read_text()
        blob=bytes(map(int,re.search(r'\{([\d,]+)\}',header).group(1).split(',')))
        self.assertEqual(gzip.decompress(blob),(ROOT/'web/index.html').read_bytes())
    def test_python_syntax(self):
        for p in ROOT.rglob('*.py'):
            if not any(x in p.parts for x in ('.venv','node_modules','tools','.git')):
                ast.parse(p.read_text(encoding='utf-8'),filename=str(p.relative_to(ROOT)))
    def test_no_private_paths_or_report_builders(self):
        for p in ROOT.rglob('*'):
            if not p.is_file() or '.git' in p.parts:continue
            self.assertNotEqual(p.suffix.lower(),'.pdf',str(p))
            if p.suffix in ('.py','.ps1','.cjs','.h','.ino','.md','.json','.yml','.cmd'):
                text=p.read_text(encoding='utf-8')
                for value in ('C:'+chr(92)+'Users'+chr(92), 'C:'+'/Users/', 'D:'+chr(92)+'RESEARCH'+chr(92)):
                    self.assertNotIn(value,text,str(p.relative_to(ROOT)))
if __name__=='__main__':unittest.main()
