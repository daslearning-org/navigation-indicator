from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.utils import platform

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivy.parser import parse_color


Builder.load_string('''

<NavMainBox>:
    orientation: 'vertical'
    spacing: dp(4)

    MDGridLayout: # other symbols buttons
        cols: 4
        size_hint_y: 0.3
        spacing: dp(4)
        padding: 14, 4, 14, 4 # left, top, right, bottom

        MDIconButton:
            id: left_u_turn_btn
            icon: "arrow-u-down-left-bold"
            theme_icon_color: "Custom"
            icon_color: "black"
            icon_size: sp(32)
            md_bg_color: 'gray'
            #pos_hint: {"center_x": .5, "center_y": .5}
            size_hint_x: 0.25
            size_hint_y: 0.9
            on_release: app.indicatior_light(self, "left-u")

        MDIconButton:
            id: park_btn
            icon: "car-brake-parking"
            theme_icon_color: "Custom"
            icon_color: "black"
            icon_size: sp(32)
            md_bg_color: 'gray'
            #pos_hint: {"center_x": .5, "center_y": .5}
            size_hint_x: 0.25
            size_hint_y: 0.9
            on_release: app.indicatior_light(self, "park")

        MDIconButton:
            id: stop_btn
            icon: "hand-back-right"
            theme_icon_color: "Custom"
            icon_color: "black"
            icon_size: sp(32)
            md_bg_color: 'gray'
            #pos_hint: {"center_x": .5, "center_y": .5}
            size_hint_x: 0.25
            size_hint_y: 0.9
            on_release: app.indicatior_light(self, "stop")

        MDIconButton:
            id: right_u_turn_btn
            icon: "arrow-u-down-right-bold"
            theme_icon_color: "Custom"
            icon_color: "black"
            icon_size: sp(32)
            md_bg_color: 'gray'
            #pos_hint: {"center_x": .5, "center_y": .5}
            size_hint_x: 0.25
            size_hint_y: 0.9
            on_release: app.indicatior_light(self, "right-u")

    MDGridLayout: # indicator buttons
        cols: 4
        size_hint_y: 0.3
        spacing: dp(4)
        padding: 14, 4, 14, 4 # left, top, right, bottom

        MDIconButton:
            id: left_turn_btn
            icon: "arrow-left-top-bold"
            theme_icon_color: "Custom"
            icon_color: "black"
            icon_size: sp(48)
            md_bg_color: 'gray'
            pos_hint: {"center_x": .5, "center_y": .5}
            size_hint_x: 0.5
            size_hint_y: 0.9
            on_release: app.indicatior_light(self, "left")

        MDIconButton:
            id: right_turn_btn
            icon: "arrow-right-top-bold"
            theme_icon_color: "Custom"
            icon_color: "black"
            icon_size: sp(48)
            md_bg_color: 'gray'
            #pos_hint: {"center_x": .5, "center_y": .5}
            size_hint_x: 0.5
            size_hint_y: 0.9
            on_release: app.indicatior_light(self, "right")

    MDGridLayout: # server buttons
        cols: 2
        size_hint_y: 0.2
        spacing: dp(4)
        padding: 14, 0, 14, 0 # left, top, right, bottom

        MDFillRoundFlatIconButton:
            id: start_app_server_btn
            text: "Start Server"
            icon: "play"
            font_size: sp(18)
            md_bg_color: 'gray'
            #pos_hint: {"center_x": .5, "center_y": .5}
            size_hint_x: 0.7
            #size_hint_y: 0.7
            on_release: app.toggle_api_server()

    BoxLayout: # result display
        size_hint_y: 0.2
        id: nav_result_box
        orientation: 'vertical'
        spacing: dp(4)
        padding: dp(4)

        MDLabel:
            id: btn_text
            halign: "center"
            markup: True
            text: "Button updates will be shown here."
            #adaptive_height: True

        MDLabel:
            id: result_text
            halign: "center"
            markup: True
            text: "Your Navigation will be shown here."
            #adaptive_height: True

''')

class NavMainBox(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "nav_main_bx"
