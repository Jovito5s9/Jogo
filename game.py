from screens.menu_screen import MenuScreen
from screens.game_screen import GameScreen
from screens.config_screen import ConfiguracoesScreen
from screens.splash_screen import SplashScreen
#from screens.conquistas_screen import ConquistasScreen ###### entra na proxima atualização
from kivy.uix.screenmanager import ScreenManager, NoTransition

GameScreenManager=ScreenManager(transition=NoTransition())

GameScreenManager.add_widget(SplashScreen(name='splash', GameScreenManager=GameScreenManager))
GameScreenManager.add_widget(MenuScreen(name='menu', GameScreenManager=GameScreenManager))
GameScreenManager.add_widget(ConfiguracoesScreen(name='configurações', GameScreenManager=GameScreenManager))
GameScreenManager.add_widget(GameScreen(name='game',GameScreenManager=GameScreenManager))
#GameScreenManager.add_widget(ConquistasScreen(name='conquistas', GameScreenManager=GameScreenManager)) ###### entra na proxima atualização
GameScreenManager.get_screen('splash').init_screen()