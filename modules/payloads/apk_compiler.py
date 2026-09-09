import os
import subprocess
import shutil
from pathlib import Path

def compile_apk():
    """
    Main entry point function called by the Megalodon framework.
    """
    base_dir = Path(__file__).parent.parent.parent / 'payloads' / 'android' / 'build'
    work_dir = base_dir / 'work'
    output_apk = base_dir / 'megalodon.apk'
    
    # Step 1: Validate dependencies
    try:
        subprocess.run(['apktool', '--version'], capture_output=True, check=True)
    except:
        return {'success': False, 'error': 'apktool not installed. Install: sudo apt install apktool'}

    # Step 2: Ensure work directory template structures are set up 
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # FIX: Explicitly inject apktool.yml right before compiling to prevent PathNotExist error
    apktool_yml_file = work_dir / 'apktool.yml'
    apktool_yml_content = '''version: 2.7.0
apkFileName: megalodon.apk
isFrameworkApk: false
usesFramework:
  ids:
  - 1
sdkInfo:
  minSdkVersion: '21'
  targetSdkVersion: '31'
'''
    with open(apktool_yml_file, 'w') as f:
        f.write(apktool_yml_content)
    
    # Verify Manifest placement fallback injection
    manifest_file = work_dir / 'AndroidManifest.xml'
    if not manifest_file.exists():
        fallback_manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://android.com" package="com.megalodon.payload">
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:allowBackup="true" android:label="System Update">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <service android:name=".PayloadService" android:exported="false" />
    </application>
</manifest>'''
        with open(manifest_file, 'w') as f:
            f.write(fallback_manifest)

    # Step 3: Run the Apktool compilation sequence
    print("[*] Building APK with apktool...")
    cmd = ['apktool', 'b', str(work_dir), '-o', str(output_apk)]
    
    # Fix 32-bit constraints on systems using older versions or warnings
    env = os.environ.copy()
    env["JAVA_TOOL_OPTIONS"] = "-Djava.awt.headless=true"
    
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    if r.returncode != 0:
        # Check if apktool requires explicit build targeting flags
        if "missing" in r.stderr or "AndroidManifest" in r.stderr or "not found" in r.stderr or "apktool.yml" in r.stderr:
            # Secondary pass targeting root fallback directly
            cmd_fallback = ['apktool', 'b', str(base_dir), '-o', str(output_apk)]
            r = subprocess.run(cmd_fallback, capture_output=True, text=True, env=env)
            if r.returncode == 0:
                print("[+] APK built successfully with root path fallback context.")
                return {'success': True, 'apk_path': str(output_apk)}
        
        print(f"[-] apktool error: {r.stderr}")
        return {'success': False, 'error': r.stderr}
        
    print("[+] APK built with apktool")
    return {'success': True, 'apk_path': str(output_apk)}

