from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle


class SmartGridLayout(GridLayout):

    def __init__(self, **kwargs):
        super(SmartGridLayout, self).__init__(**kwargs)

    def resize_v(self, *args):
        container_height = 0
        for index, child in enumerate(self.children, 0):
            if index % self.cols == 0:
                container_height += child.height + self.spacing[1]
        # container_height -= self.spacing[1]

        self.height = container_height

    def resize_h(self, *args):

        container_width = 0
        for child in self.children:
            container_width += child.width + self.spacing[0]
        # container_width -= self.spacing[0]

        self.width = container_width
