from screens.menu_screen import MenuScreen
from screens.game_screen import GameScreen
from screens.config_screen import ConfiguracoesScreen
from kivy.uix.screenmanager import ScreenManager

GameScreenManager=ScreenManager()

GameScreenManager.add_widget(MenuScreen(name='menu', GameScreenManager=GameScreenManager))
GameScreenManager.add_widget(ConfiguracoesScreen(name='configurações', GameScreenManager=GameScreenManager))
GameScreenManager.add_widget(GameScreen(name='game',GameScreenManager=GameScreenManager))