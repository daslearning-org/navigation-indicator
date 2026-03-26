## Changes

### 1.1.0
- Introducing `BLE` (Bluetooth Low Energy) capability in the Android app.
- Now the `Stearing` position setting will be remembered in the app.
- Some improvements.

### 1.0.0
#### ✅ The much required update to listen to Google Maps notification
- Now we are capturing the indicator icons (GMaps doesn't provide text based turn directions) & applying logic to understand whether they are left / right  or u-turns.

### 0.1.0
- Adding feature to read notifications directly from our app, just start `Auto Mode`. (Need to have required permissions)
- App will try connect the last connected bluetooth device if disconnected.

> Note: No need to rely on other apps, although you still can use `Macrodroid` or `Termux` as the `API Server` feature from our app can listen from those apps.

### 0.0.3
- Now app will use a service, so that app may not need to stay on foreground.
- Now automatic nagivation start threashold is 60m (earlier 50m).
- Will show an error if Bluetooth connection fails.
- Updated correct demo & documentation link.
- Adding android api 36 (android 16) support.
- Some bug fixes.

### 0.0.2
- Introducing the `Bluetooth` connectivity for ESP32.
- Adding the navigation app API logic.

### 0.0.1
- Initial project version with working mobile app (no ESP32).
