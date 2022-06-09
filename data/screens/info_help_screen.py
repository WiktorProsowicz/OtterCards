from kivy.uix.screenmanager import Screen


class InfoHelpScreen(Screen):

    def on_pre_enter(self, *args):
        self.ids["slider"].scroll_y = 1
    
    def __init__(self, **kwargs):
        super(InfoHelpScreen, self).__init__(**kwargs)
