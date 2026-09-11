import base64
import struct
from pathlib import Path

JPEG_SOI = b'\xFF\xD8'
JPEG_COMMENT = b'\xFF\xFE'
PNG_SIG = b'\x89PNG\r\n\x1a\n'


def extract_from_jpeg(data):
    if not data.startswith(JPEG_SOI):
        return None
    pos = 2
    while pos < len(data) - 1:
        if data[pos:pos + 2] != JPEG_COMMENT:
            break
        length = struct.unpack('>H', data[pos + 2:pos + 4])[0]
        marker = data[pos + 4:pos + 2 + length]
        if marker.startswith(b'<!--APK:'):
            b64 = marker[len(b'<!--APK:'):-3]
            return base64.b64decode(b64)
        pos += 2 + length
    return None


def extract_from_png(data):
    if not data.startswith(PNG_SIG):
        return None
    pos = 8
    while pos < len(data) - 8:
        length = struct.unpack('>I', data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        cdata = data[pos + 8:pos + 8 + length]
        if ctype == b'tEXt' and cdata.startswith(b'apk\x00'):
            return base64.b64decode(cdata[4:])
        pos += 12 + length
        if ctype == b'IEND':
            break
    return None


def extract_from_mp4(data):
    pos = 0
    while pos < len(data) - 8:
        size = int.from_bytes(data[pos:pos + 4], 'big')
        ctype = data[pos + 4:pos + 8]
        if size == 0 or size > len(data):
            break
        if ctype == b'free':
            payload = data[pos + 8:pos + size]
            if payload.startswith(b'MEGALODON_APK:'):
                return base64.b64decode(payload[len(b'MEGALODON_APK:'):])
        pos += size
    return None
def extract(path):
    p = Path(path)
    if not p.exists():
        return {'success': False, 'error': f'File not found: {path}'}

    data = p.read_bytes()
    suffix = p.suffix.lower()

    apk = None
    if suffix in ('.jpg', '.jpeg'):
        apk = extract_from_jpeg(data)
    elif suffix == '.png':
        apk = extract_from_png(data)
    elif suffix == '.mp4':
        apk = extract_from_mp4(data)

    if apk is None:
        return {'success': False, 'error': 'No APK found in file'}

    out = p.with_name(p.stem + '_extracted.apk')
    out.write_bytes(apk)

    return {
        'success': True,
        'apk_path': str(out),
        'size_kb': round(len(apk) / 1024, 1)
    }


def run(path):
    result = extract(path)
    if result['success']:
        print(f"[+] Extracted APK: {result['apk_path']}")
        print(f"[+] Size: {result['size_kb']} KB")
    else:
        print(f"[-] {result['error']}")
    return result
