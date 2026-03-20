package in.daslearning.navindi;

import android.bluetooth.*;
import android.content.Context;
import java.util.UUID;
import android.util.Log;

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

        gatt = device.connectGatt(context, false, new BluetoothGattCallback() {

            @Override
            public void onConnectionStateChange(BluetoothGatt g, int status, int newState) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    Log.d("NAVINDI", "Connected");
                    g.discoverServices();
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