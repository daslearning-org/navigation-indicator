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
  * ServiceRecord{34ad9ef u0 in.daslearning.navindi/.ServiceNavindiservice c:in.daslearning.navindi}
    intent={cmp=in.daslearning.navindi/.ServiceNavindiservice}
    packageName=in.daslearning.navindi
    processName=in.daslearning.navindi:service_navindiservice
    baseDir=/data/app/~~kEZ28eyzGycFHsAXgFkP_g==/in.daslearning.navindi-mvlP5Gqtt0XFWegHjNuYjw==/base.apk
    dataDir=/data/user/0/in.daslearning.navindi
    recentCallingPackage=in.daslearning.navindi
    infoAllowStartForeground=[callingPackage: in.daslearning.navindi; callingUid: 10714; uidState: TOP ; uidBFSL: [BFSL]; intent: Intent { cmp=in.daslearning.navindi/.ServiceNavindiservice (has extras) }; code:PROC_STATE_TOP; tempAllowListReason:<null>; targetSdkVersion:36; callerTargetSdkVersion:36; startForegroundCount:0; bindFromPackage:null: isBindService:false]
      callingInfo: callingPid=13682 callingUid=10714 callingPackage=in.daslearning.navindi
      intent=Intent { cmp=in.daslearning.navindi/.ServiceNavindiservice (has extras) }
  * ServiceRecord{5e52482 u0 in.daslearning.navindi/.NavindiService c:in.daslearning.navindi}
    intent={cmp=in.daslearning.navindi/.NavindiService}
    packageName=in.daslearning.navindi
    processName=in.daslearning.navindi
    baseDir=/data/app/~~kEZ28eyzGycFHsAXgFkP_g==/in.daslearning.navindi-mvlP5Gqtt0XFWegHjNuYjw==/base.apk
    dataDir=/data/user/0/in.daslearning.navindi
    app=ProcessRecord{fca13e4 13682:in.daslearning.navindi/u0a714}
    recentCallingPackage=in.daslearning.navindi
    infoAllowStartForeground=[callingPackage: in.daslearning.navindi; callingUid: 10714; uidState: TOP ; uidBFSL: [BFSL]; intent: Intent { cmp=in.daslearning.navindi/.NavindiService }; code:PROC_STATE_TOP; tempAllowListReason:<null>; targetSdkVersion:36; callerTargetSdkVersion:36; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    isForeground=true foregroundId=1 types=0x00000008 foregroundNoti=Notification(channel=navindi_service shortcut=null contentView=null vibrate=null sound=null defaults=0 flags=NO_CLEAR|FOREGROUND_SERVICE color=0x00000000 vis=PRIVATE)
  * Restarting ServiceRecord{34ad9ef u0 in.daslearning.navindi/.ServiceNavindiservice c:in.daslearning.navindi}
    intent={cmp=in.daslearning.navindi/.ServiceNavindiservice}
    packageName=in.daslearning.navindi
    processName=in.daslearning.navindi:service_navindiservice
    baseDir=/data/app/~~kEZ28eyzGycFHsAXgFkP_g==/in.daslearning.navindi-mvlP5Gqtt0XFWegHjNuYjw==/base.apk
    dataDir=/data/user/0/in.daslearning.navindi
    recentCallingPackage=in.daslearning.navindi
    infoAllowStartForeground=[callingPackage: in.daslearning.navindi; callingUid: 10714; uidState: TOP ; uidBFSL: [BFSL]; intent: Intent { cmp=in.daslearning.navindi/.ServiceNavindiservice (has extras) }; code:PROC_STATE_TOP; tempAllowListReason:<null>; targetSdkVersion:36; callerTargetSdkVersion:36; startForegroundCount:0; bindFromPackage:null: isBindService:false]
      callingInfo: callingPid=13682 callingUid=10714 callingPackage=in.daslearning.navindi
      intent=Intent { cmp=in.daslearning.navindi/.ServiceNavindiservice (has extras) }
  #0: in.daslearning.navindi


```

4. Check the notification listener service
```bash
adb shell dumpsys notification | grep navindi
```
