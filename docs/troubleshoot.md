# Troubleshooting the issues

## Wireless debugging

1. Connect via wireless debugging (optional if you use usb cable)
```
adb connect <IP>:<port>
```

2. Check the logs from Service
Get the `pid` from adb

```bash
adb shell ps | grep navindi
adb logcat --pid=23490 # your pid of service
```

3. Check the Service details
```bash
somnath@dell-5530:~$ adb shell dumpsys activity services | grep navindi
  * ServiceRecord{5776b8b u0 in.daslearning.navindi/.ServiceNavindisvc c:in.daslearning.navindi}
    intent={cmp=in.daslearning.navindi/.ServiceNavindisvc}
    packageName=in.daslearning.navindi
    processName=in.daslearning.navindi:service_navindisvc
    baseDir=/data/app/~~L3NctgLt8NFtgU_G4CZIXQ==/in.daslearning.navindi-Xe1p0dwww49-cfxM0dErHw==/base.apk
    dataDir=/data/user/0/in.daslearning.navindi
    app=ProcessRecord{f1f5468 6908:in.daslearning.navindi:service_navindisvc/u0a710}
    recentCallingPackage=in.daslearning.navindi
    infoAllowStartForeground=[callingPackage: in.daslearning.navindi; callingUid: 10710; uidState: TOP ; uidBFSL: [BFSL]; intent: Intent { cmp=in.daslearning.navindi/.ServiceNavindisvc (has extras) }; code:PROC_STATE_TOP; tempAllowListReason:<null>; targetSdkVersion:36; callerTargetSdkVersion:36; startForegroundCount:0; bindFromPackage:null: isBindService:false]

```
