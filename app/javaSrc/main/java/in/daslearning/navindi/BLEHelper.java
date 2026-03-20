package in.daslearning.navindi;

import android.bluetooth.*;
import android.content.Context;
import java.util.UUID;
import android.util.Log;
import android.os.Handler;
import android.os.Looper;

public class BLEHelper {

    //private BLEListener listener;
    private BluetoothGatt gatt;
    private BluetoothGattCharacteristic writeChar;

    //public static void setListner(BLEListener blePy) {
    //    listener = blePy;
    //    Log.d("NAVINDI", "BLE Helper regiserted");
    //}

    public BLEHelper() {
    }

    public void connect(Context context, String mac) {

        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        BluetoothDevice device = adapter.getRemoteDevice(mac);

        if (gatt != null) {
            gatt.disconnect();
            gatt.close();
            gatt = null;
        }

        gatt = device.connectGatt(context, false, new BluetoothGattCallback() {

            @Override
            public void onConnectionStateChange(BluetoothGatt g, int status, int newState) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    Log.d("NAVINDI", "Connected" + status);
                    new Handler(Looper.getMainLooper()).postDelayed(() -> {
                        g.discoverServices();
                    }, 500);
                }
            }

            @Override
            public void onServicesDiscovered(BluetoothGatt g, int status) {

                for (BluetoothGattService service : g.getServices()) {

                    for (BluetoothGattCharacteristic ch : service.getCharacteristics()) {

                        int props = ch.getProperties();

                        if ((props & BluetoothGattCharacteristic.PROPERTY_WRITE) != 0 ||
                            (props & BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE) != 0) {

                            writeChar = ch;
                            Log.d("NAVINDI", "BLE Ready");
                            return;
                        }
                    }
                }
            }
        },
        BluetoothDevice.TRANSPORT_LE
        );
    }

    public void send(String msg) {

        if (gatt == null || writeChar == null) return;

        writeChar.setValue(msg.getBytes());
        gatt.writeCharacteristic(writeChar);
    }
}

// to be added
new Handler(Looper.getMainLooper()).postDelayed(() -> {

    gatt = device.connectGatt(
        context,
        false,
        callback,
        BluetoothDevice.TRANSPORT_LE
    );

}, 500);  // 500 ms delay