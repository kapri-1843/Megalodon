package com.megalodon.payload;

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
            fw.write("[" + ts + "] ACT: " + msg + "\n");
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
