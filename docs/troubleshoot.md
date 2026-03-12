# Troubleshooting the issues

## Check the logs from Service
Get the `pid` from adb

```bash
adb shell ps | grep navindi
adb logcat --pid=23490 # your pid of service
```
