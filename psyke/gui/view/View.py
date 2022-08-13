from kivy.graphics import Color, Rectangle, Line
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

from psyke.gui.view.DataPanel import DataPanel
from psyke.gui.view.ExtractorPanel import ExtractorPanel
from psyke.gui.view.PredictorPanel import PredictorPanel


class View(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MainScreen(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_panel = None
        self.predictor_panel = None
        self.extractor_panel = None

        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos=[0, 0], size=Window.size)
            Color(0, 0, 0)
            Rectangle(pos=[4, 4], size=[Window.width - 8, 244])
            Rectangle(pos=[4, 252], size=[Window.width - 8, 296])
            Rectangle(pos=[4, 552], size=[Window.width - 8, 196])
            Color(1, 1, 1)
            Line(points=[300, 0, 300, Window.height])
            Line(points=[520, 0, 520, Window.height])
            Line(points=[800, 0, 800, Window.height])

    def init(self, controller):
        self.data_panel = DataPanel(controller)
        self.predictor_panel = PredictorPanel(controller)
        self.extractor_panel = ExtractorPanel(controller)

        layout = GridLayout(cols=1, spacing=0, rows_minimum={0: 200, 1: 300, 2: 250})
        layout.add_widget(self.data_panel)
        layout.add_widget(self.predictor_panel)
        layout.add_widget(self.extractor_panel)
        self.add_widget(layout)
