import os
import kivy
kivy.require('1.8.0')
from kivy.app import App, Builder
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout

KV_DIRECTORY = "templates/default"


class MenuToggleButton(ToggleButton):
    def on_press(self):
        if self.identity == "settings":
            print "you are now settings"
    pass


class Main(GridLayout):
    pass


class Start(App):
    def build(self):
        Builder.load_file(os.path.join(KV_DIRECTORY, "main.kv"))
        return Main()
    pass

if __name__ == '__main__':
    Start().run()
