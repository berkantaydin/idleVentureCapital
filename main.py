import os
import kivy
kivy.require('1.8.0')
from kivy.app import App, Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

KV_DIRECTORY = "templates/default"

# Base Values
star = 0
resset_total = 0  # Resets total of entire game life
gained_on_now = 0  # Total gain in current game
gained_on_total = 0  # Total gain of entire game life
cash = 0  # Current available cash for spend ventures

Ventures = dict()
Ventures = {
    "allowance": {"name": "Allowance", "owned": 1, "period": 1, "cost": 0, "revenue": 4},
    "lemonade": {"name": "Lemonade Stand", "owned": 0, "period": 8, "cost": 10, "revenue": 4},
    "paper": {"name": "Paper Route", "owned": 0, "period": 16, "cost": 34, "revenue": 14},
    "fastfood": {"name": "Fast Food Joint", "owned": 0, "period": 32, "cost": 150, "revenue": 49},
    "coffee": {"name": "Coffee Shop", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "bar": {"name": "Bar", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "lawn": {"name": "Lawn Care", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "dining": {"name": "Fine Dining", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "startup": {"name": "Startup", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "construction": {"name": "Construction", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "insurance": {"name": "Insurance", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "record": {"name": "Record Label", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "studio": {"name": "Movie Studio", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "bank": {"name": "Bank", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "team": {"name": "ProSports Team", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "oil": {"name": "Oil & Gas", "owned": 0, "period": 0, "cost": 0, "revenue": 0},
    "government": {"name": "Small Government", "owned": 0, "period": 0, "cost": 0, "revenue": 0}
}


class MenuToggleButton(ToggleButton):
    def on_press(self):
        if self.identity == "settings":
            print "you are now settings"
    pass


class VentureItem(BoxLayout):
    key = StringProperty("")
    name = StringProperty("")
    cost = NumericProperty(0)
    owned = NumericProperty(0)
    period = NumericProperty(0)
    revenue = NumericProperty(0)

    # for garbage collector
    def __del__(self, *args, **kwargs):
        pass


class Main(GridLayout):
    ventures = ListProperty([])

    def args_converter(self, row_index, item):
        """
        args_converter, for displaying repositories
        To display a list of data this convertion style is
        requested for kivy Factory method.
        """
        return dict(
            key=item['key'],
            name=item['value']['name'],
            cost=item['value']['cost'],
            owned=item['value']['owned'],
            period=item['value']['period'],
            revenue=item['value']['revenue'],
        )

    def convert(self, data):
        result = []
        for k, v in data.items():
            tmp = dict(key=k, value=v)
            result.append(tmp)
        return result
    pass


class Start(App):
    def build(self):
        Builder.load_file(os.path.join(KV_DIRECTORY, "main.kv"))
        layout = Main()
        layout.ventures = layout.convert(Ventures)
        return layout
    pass

if __name__ == '__main__':
    Start().run()
