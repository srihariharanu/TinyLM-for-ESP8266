from pathlib import Path
import gzip, hashlib, re
ROOT=Path(__file__).resolve().parent
(ROOT/'tmp').mkdir(exist_ok=True)
source=(ROOT/'web'/'index.html').read_bytes()
assert b'Sri Hariharan U' in source and b'srihariharanu@gmail.com' in source
assert not re.search(rb'(?:src|href)=["\']https?://',source), 'Remote asset found'
compressed=gzip.compress(source,compresslevel=9,mtime=0)
# Preserve the released gzip OS marker independently of the build host.
compressed=compressed[:9]+bytes([10])+compressed[10:]
assert gzip.decompress(compressed)==source
header=ROOT/'firmware'/'RecurrentLM'/'web_ui.h'
header.write_text('#pragma once\n#include <pgmspace.h>\nalignas(4) const uint8_t WEB_UI[] PROGMEM = {'+','.join(map(str,compressed))+'};\nconstexpr size_t WEB_UI_SIZE=sizeof(WEB_UI);\n',encoding='ascii',newline='\n')
(ROOT/'tmp'/'web-script.js').write_text(re.search(r'<script>(.*?)</script>',source.decode('utf-8'),re.S).group(1),encoding='utf-8')
print(f'Offline page: {len(source)} bytes; flash gzip: {len(compressed)} bytes; SHA256: {hashlib.sha256(source).hexdigest()}')
