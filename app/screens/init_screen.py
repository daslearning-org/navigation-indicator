from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel

from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivy.utils import platform

Builder.load_string('''
<ConfigInput>:
    orientation: 'vertical'
    spacing: dp(4)
    padding: 0, 0, 0, self.bottom_pad

    MDGridLayout:
        cols: 2
        adaptive_height: True
        MDLabel:
            text: "SMS number"
            halign: "left"
            font_size: sp(18)
            size_hint_x: 0.2
        MDTextField:
            id: phone_num
            hint_text: "Enter the number"
            mode: "rectangle"
            helper_text: "ex: +919876543210"
            helper_text_mode: "persistent"
            size_hint_x: 0.8
            font_size: sp(14)
            multiline: False
            required: True
    MDGridLayout:
        cols: 2
        adaptive_height: True
        MDLabel:
            text: "SMS frequency (min)"
            halign: "left"
            font_size: sp(14)
            size_hint_x: 0.2
        MDTextField:
            id: sms_freq_input
            text: "10"
            hint_text: "number of minutes"
            mode: "rectangle"
            helper_text: "default: 10"
            helper_text_mode: "persistent"
            size_hint_x: 0.8
            font_size: sp(18)
            multiline: False
            input_filter: 'int'
    MDFillRoundFlatIconButton:
        text: "Save"
        icon: "floppy"
        pos_hint: {'center_x': 0.5}
        size_hint_x: 0.6
        font_size: sp(24)
        on_release: app.save_config(self, phone_num, sms_freq_input)
    Widget:
        size_hint_y: 1
''')

class ConfigInput(MDBoxLayout):
    """ Takes configuration inputs """
    top_pad = NumericProperty(0)
    bottom_pad = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform == "android":
            try:
                from android.display_cutout import get_height_of_bar
                self.top_pad = int(get_height_of_bar('status'))
                self.bottom_pad = int(get_height_of_bar('navigation'))
            except Exception as e:
                print(f"Failed android 15 padding: {e}")
                self.top_pad = 32
                self.bottom_pad = 48
