import os
import shutil
import subprocess
import zipfile
from pathlib import Path


def check_tools():
    tools = {}
    for t in ['javac', 'dx', 'apksigner', 'keytool']:
        try:
            subprocess.run([t, '--version'], capture_output=True, check=True)
            tools[t] = True
        except Exception:
            tools[t] = False

    try:
        r = subprocess.run(['zipalign'], capture_output=True)
        if r.returncode == 0 or b'Zip' in r.stdout or b'Zip' in r.stderr:
            tools['zipalign'] = True
        else:
            tools['zipalign'] = False
    except Exception:
        tools['zipalign'] = False

    return tools


def ensure_keystore(base_dir):
    keystore = base_dir / 'debug.keystore'
    if keystore.exists():
        return keystore
    print('[*] Creating debug keystore...')
    subprocess.run([
        'keytool', '-genkey', '-v',
        '-keystore', str(keystore),
        '-alias', 'megalodon',
        '-storepass', 'android',
        '-keypass', 'android',
        '-keyalg', 'RSA',
        '-keysize', '2048',
        '-validity', '10000',
        '-dname', 'CN=Megalodon, OU=Dev, O=Dev, L=X, S=X, C=US'
    ], check=True, capture_output=True)
    return keystore


def find_android_jar():
    candidates = [
        '/usr/lib/android-sdk/platforms/android-34/android.jar',
        '/usr/lib/android-sdk/platforms/android-33/android.jar',
        '/usr/lib/android-sdk/platforms/android-31/android.jar',
        '/opt/android-sdk/platforms/android-34/android.jar',
        str(Path.home() / 'Android/Sdk/platforms/android-34/android.jar'),
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def compile_java(src_dir, build_tmp, android_jar):
    classes_dir = build_tmp / 'classes'
    classes_dir.mkdir(parents=True, exist_ok=True)

    java_files = list(src_dir.rglob('*.java'))
    if not java_files:
        return False, 'No .java files found', classes_dir

    print(f'[*] Compiling {len(java_files)} java file(s)...')
    cmd = [
        'javac',
        '--release', '8',
        '-g:none',
        '-cp', android_jar,
        '-d', str(classes_dir),
    ] + [str(f) for f in java_files]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return False, f'javac failed: {r.stderr}', classes_dir
    return True, None, classes_dir


def convert_to_dex(classes_dir, build_tmp, android_jar):
    dex_dir = build_tmp / 'dex'
    dex_dir.mkdir(parents=True, exist_ok=True)

    class_files = list(classes_dir.rglob('*.class'))
    if not class_files:
        return False, 'No .class files found', dex_dir

    print(f'[*] Converting {len(class_files)} class file(s) to dex (using dx)...')
    cmd = [
        'dx',
        '--dex',
        '--min-sdk-version=21',
        '--output=' + str(dex_dir / 'classes.dex'),
        str(classes_dir),
    ]

    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(classes_dir))
    if r.returncode != 0:
        return False, f'dx failed: {r.stderr}', dex_dir
    return True, None, dex_dir


def inject_dex_into_apk(template_apk, dex_dir, out_apk):
    classes_dex = dex_dir / 'classes.dex'
    if not classes_dex.exists():
        return False, 'classes.dex not produced'

    print('[*] Injecting classes.dex into template APK...')

    with open(classes_dex, 'rb') as f:
        new_dex_data = f.read()

    with zipfile.ZipFile(template_apk, 'r') as zin:
        with zipfile.ZipFile(out_apk, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'classes.dex':
                    continue
                data = zin.read(item.filename)
                zout.writestr(item, data)
            zout.writestr('classes.dex', new_dex_data)

    print('[+] Template rebuilt with new classes.dex')
    return True, None


def zipalign_apk(apk_path, tools):
    if not tools.get('zipalign'):
        print('[!] zipalign not available - skipping alignment')
        return apk_path

    aligned = apk_path.with_name(apk_path.stem + '_aligned.apk')
    r = subprocess.run(
        ['zipalign', '-f', '-p', '4', str(apk_path), str(aligned)],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f'[!] zipalign failed: {r.stderr.strip()}')
        return apk_path
    return aligned


def sign_apk(apk_path, keystore, out_path):
    print('[*] Signing APK...')
    r = subprocess.run([
        'apksigner', 'sign',
        '--ks', str(keystore),
        '--ks-pass', 'pass:android',
        '--key-pass', 'pass:android',
        '--ks-key-alias', 'megalodon',
        '--out', str(out_path),
        str(apk_path)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        return False, r.stderr
    return True, None


def compile_apk():
    base_dir = Path(__file__).parent.parent.parent / 'payloads' / 'android' / 'build'
    src_dir = Path(__file__).parent.parent.parent / 'payloads' / 'android' / 'src'
    build_tmp = base_dir / 'build_tmp'
    output_apk = base_dir / 'megalodon.apk'
    signed_apk = base_dir / 'megalodon_signed.apk'

    tools = check_tools()
    required = ['javac', 'dx', 'apksigner', 'keytool']
    missing = [t for t in required if not tools.get(t)]
    if missing:
        return {
            'success': False,
            'error': (
                f'Missing required tools: {", ".join(missing)}\n'
                'Install dx: sudo apt install dalvik-exchange'
            )
        }

    if not tools.get('zipalign'):
        print('[!] zipalign missing - proceeding without alignment')

    android_jar = find_android_jar()
    if not android_jar:
        return {
            'success': False,
            'error': 'android.jar not found. Install android-sdk-platform-34'
        }
    print(f'[+] Using android.jar: {android_jar}')

    template_apk = base_dir / 'template.apk'
    if not template_apk.exists():
        return {
            'success': False,
            'error': (
                f'template.apk not found at {template_apk}.\n'
                'Run: ./make_template.sh   (from Megalodon root)'
            )
        }

    if build_tmp.exists():
        shutil.rmtree(build_tmp)
    build_tmp.mkdir(parents=True, exist_ok=True)

    ok, err, classes_dir = compile_java(src_dir, build_tmp, android_jar)
    if not ok:
        return {'success': False, 'error': err}

    ok, err, dex_dir = convert_to_dex(classes_dir, build_tmp, android_jar)
    if not ok:
        return {'success': False, 'error': err}

    ok, err = inject_dex_into_apk(template_apk, dex_dir, output_apk)
    if not ok:
        return {'success': False, 'error': err}

    aligned = zipalign_apk(output_apk, tools)

    keystore = ensure_keystore(base_dir)
    ok, err = sign_apk(aligned, keystore, signed_apk)
    if not ok:
        return {'success': False, 'error': f'Signing failed: {err}'}

    size = signed_apk.stat().st_size
    if size < 10240:
        return {
            'success': False,
            'error': f'Signed APK too small ({size} bytes). Template may be broken.'
        }

    print(f'[+] Signed APK: {signed_apk} ({size / 1024:.1f} KB)')
    return {
        'success': True,
        'apk_path': str(signed_apk),
        'size_kb': round(size / 1024, 1)
    }
