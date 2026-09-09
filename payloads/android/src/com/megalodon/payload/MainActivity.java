
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
        startService(new Intent(this, PayloadService.class));
        finish();
    }
}