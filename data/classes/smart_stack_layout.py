from kivy.uix.stacklayout import StackLayout


class SmartStackLayout(StackLayout):

    def resize_v(self, *args):
        if len(self.children) == 1:
            self.height = self.children[0].height + self.padding[1] * 2

        elif len(self.children) > 1:
            container_height = max(self.children, key=lambda x: x.top).top - min(self.children, key=lambda x: x.y).y
            self.height = container_height + self.padding[0] * 2

    def __init__(self, **kwargs):
        super(SmartStackLayout, self).__init__(**kwargs)
