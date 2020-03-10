package com.example.cpen291robotcontrol;

import androidx.appcompat.app.AppCompatActivity;

import android.bluetooth.*;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;

import java.io.IOException;
import java.io.OutputStream;
import java.util.Set;
import java.util.UUID;

import static android.content.ContentValues.TAG;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_ENABLE_BT = 1;
    private ConnectThread thread;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // Get bluetooth adapter on this device
        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        // Return an error if bluetooth is not supported
        if (bluetoothAdapter == null) {
            Log.e(TAG, "Bluetooth is not present on this device");
            return;
        }
        // Turn on bluetooth if it is not already enabled
        if (!bluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }

        // Get the set of connected devices (should only be 1) and set that as pi
        Set<BluetoothDevice> connectedDevices = bluetoothAdapter.getBondedDevices();

        BluetoothDevice pi = null;
        for (BluetoothDevice d: connectedDevices) {
            pi = d;
        }
        if (pi == null) {
            Log.e(TAG, "Could not find device");
        }
        //
        this.thread = new ConnectThread(pi);

        thread.start();
    }

    @Override
    public void onBackPressed() {
        thread.cancel();
        moveTaskToBack(true);
        android.os.Process.killProcess(android.os.Process.myPid());
        System.exit(1);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        thread.cancel();
    }

    public void stopSignal(View view) {
        byte[] bytes = new byte[1];
        bytes[0] = 1;
        thread.write(bytes);
    }

    public void moveForward(View view) {
        byte[] bytes = new byte[1];
        bytes[0] = 2;
        thread.write(bytes);
    }

    public void moveBackward(View view) {
        byte[] bytes = new byte[1];
        bytes[0] = 3;
        thread.write(bytes);
    }

    public void turnLeft(View view) {
        byte[] bytes = new byte[1];
        bytes[0] = 4;
        thread.write(bytes);
    }

    public void turnRight(View view) {
        byte[] bytes = new byte[1];
        bytes[0] = 5;
        thread.write(bytes);
    }

    public void rotateLeft(View view) {
        byte[] bytes = new byte[1];
        bytes[0] = 6;
        thread.write(bytes);
    }

    public void rotateRight(View view) {
        byte[] bytes = new byte[1];
        bytes[0] = 7;
        thread.write(bytes);
    }

    public void exitSignal(View view) {
        byte[] bytes = new byte[1];
        bytes[0] = 0;
        thread.write(bytes);
        onBackPressed();
    }


}

class ConnectThread extends Thread {
    private final BluetoothSocket mmSocket;
    private final BluetoothDevice mmDevice;
    private OutputStream mmOutStream;


    public ConnectThread(BluetoothDevice device) {
        // Use a temporary object that is later assigned to mmSocket
        // because mmSocket is final.
        BluetoothSocket tmp = null;
        mmDevice = device;

        try {
            // Get a BluetoothSocket to connect with the given BluetoothDevice.
            // MY_UUID is the app's UUID string, also used in the server code.
            tmp = device.createRfcommSocketToServiceRecord(UUID.fromString("bbcc40a1-adae-41d7-a13f-676f427c9c41"));
        } catch (IOException e) {
            Log.e(TAG, "Socket's create() method failed", e);
        }
        mmSocket = tmp;
    }

    public void run() {
        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        // Cancel discovery because it otherwise slows down the connection.
        bluetoothAdapter.cancelDiscovery();
        OutputStream tmpOut = null;

        try {
            // Connect to the remote device through the socket. This call blocks
            // until it succeeds or throws an exception.
            mmSocket.connect();
        } catch (IOException connectException) {
            // Unable to connect; close the socket and return.
            try {
                mmSocket.close();
            } catch (IOException closeException) {
                Log.e(TAG, "Could not close the client socket", closeException);
            }
            return;
        }

        try {
            tmpOut = mmSocket.getOutputStream();
        } catch (IOException e) {
            Log.e(TAG, "Error occurred when creating output stream", e);
        }

        mmOutStream = tmpOut;

        // The connection attempt succeeded. Perform work associated with
        // the connection in a separate thread.
    }

    public void write(byte[] bytes) {
        try {
            mmOutStream.write(bytes);
        } catch (IOException e) {
            Log.e(TAG, "Error occurred when sending data", e);
        }
    }

    // Closes the client socket and causes the thread to finish.
    public void cancel() {
        try {
            mmSocket.close();
            Log.d(TAG, "Successfully closed client socket");
        } catch (IOException e) {
            Log.e(TAG, "Could not close the client socket", e);
        }
    }
}
