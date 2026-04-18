from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from screens.shared import STD_font_size

class ConquistasScreen(Screen):
    def __init__(self, GameScreenManager=None, **kwargs):
        super().__init__(**kwargs)
        self.GameScreenManager = kwargs.get('GameScreenManager')
        self.ui_texts = kwargs.get('ui_texts', {})
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.add_widget(self.layout)

        self.title_label = Label(
            text="conquistas",
            font_size=STD_font_size * 1.5,
            color=(0.2, 0.2, 0.2, 1),
            bold=True
        )
        self.layout.add_widget(self.title_label)
        self.conquistas_list = BoxLayout(orientation='vertical', spacing=10)
        self.layout.add_widget(self.conquistas_list)