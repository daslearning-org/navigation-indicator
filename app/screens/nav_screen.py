from kivy.lang import Builder
from kivy.metrics import dp, sp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivy.parser import parse_color


Builder.load_string('''

<NavMainBox@MDBoxLayout>:
    orientation: 'vertical'
    spacing: dp(4)

    MDGridLayout: # navigation buttons
        cols: 4
        size_hint_y: 0.6
        spacing: dp(4)
        padding: 14, 0, 14, 0 # left, top, right, bottom

        MDIconButton:
            id: left_turn_btn
            icon: "arrow-left-top-bold"
            theme_icon_color: "Custom"
            icon_color: "orange"
            icon_size: sp(18)
            md_bg_color: 'gray'
            pos_hint: {"center_x": .5, "center_y": .5}
            #size_hint_x: 0.2
            #on_release: app.popup_preference()

        MDIconButton:
            id: left_u_turn_btn
            icon: "arrow-u-left-down-bold"
            theme_icon_color: "Custom"
            icon_color: "orange"
            icon_size: sp(18)
            md_bg_color: 'gray'
            pos_hint: {"center_x": .5, "center_y": .5}
            #size_hint_x: 0.2
            #on_release: app.popup_preference()

        MDIconButton:
            id: right_u_turn_btn
            icon: "arrow-u-right-down-bold"
            theme_icon_color: "Custom"
            icon_color: "orange"
            icon_size: sp(18)
            md_bg_color: 'gray'
            pos_hint: {"center_x": .5, "center_y": .5}
            #size_hint_x: 0.2
            #on_release: app.popup_preference()

        MDIconButton:
            id: right_turn_btn
            icon: "arrow-u-right-down-bold"
            theme_icon_color: "Custom"
            icon_color: "orange"
            icon_size: sp(18)
            md_bg_color: 'gray'
            pos_hint: {"center_x": .5, "center_y": .5}
            #size_hint_x: 0.2
            #on_release: app.popup_preference()

    MDGridLayout: # server buttons
        cols: 2
        size_hint_y: 0.2
        spacing: dp(4)
        padding: 14, 0, 14, 0 # left, top, right, bottom

        MDFillRoundFlatIconButton:
            id: btn_capture
            text: "Start Server"
            icon: "play"
            font_size: sp(18)
            md_bg_color: 'orange'
            #pos_hint: {"center_x": .5, "center_y": .5}
            size_hint_x: 0.7
            on_release: app.capture_n_onnx_detect()

    BoxLayout:
        size_hint_y: 0.2
        id: nav_result_box
        orientation: 'vertical'
        spacing: dp(4)
        padding: dp(4)

        MDLabel:
            id: result_text
            halign: "center"
            markup: True
            text: "Your Navigation will be shown here."
            adaptive_height: True

''')

class NavMainBox(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "nav_main_bx"
