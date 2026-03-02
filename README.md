# 🧭 Automatic Navigation Indicator
Show automatic navigation indications like **left / right turn** indicator, **U-turn** indicator using your Android phone. Along with that, we can manually display some more indications like **no overtake**, **allow overtake** etc. using the buttons on our android app.

## 💡 How it works
The flow in simple words:

1. We are capturing the navigation notification from a navigation app like [OsmAnd](https://osmand.net/) using either [Termux](https://github.com/termux/termux-app) or [MacroDriod](https://www.macrodroid.com/) app. Then it sends the data (notification texts) to our [open-source dlNav app](https://github.com/daslearning-org/navigation-indicator/releases)

2. Our `dlNav` app processes the data & sends indicator signals to `ESP32` microcontroller to display that on a `WS2812B` 8x8 LED Matrix.

3. The app also has all manual controls to display the indicator symbols.
