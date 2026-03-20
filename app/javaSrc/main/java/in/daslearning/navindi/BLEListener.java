package in.daslearning.navindi;

public interface BLEListener {
    void onConnected();
    void onReady();
    void onMessage(String msg);
}