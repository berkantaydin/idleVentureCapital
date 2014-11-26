import os
import time
import threading
import kivy
kivy.require('1.8.0')
from kivy.app import App, Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

KV_DIRECTORY = "templates/default"
DB = JsonStore('db.json')


class Game():
    ventures = ListProperty([])

    def __init__(self):
        try:
            # Initialize data from database
            data = DB.get('game')
            self.star = data['star']
            self.resset_total = data['resset_total']
            self.gained_on_now = data['gained_on_now']
            self.gained_on_total = data['gained_on_total']
            self.cash = data['cash']
            self.ventures = data['ventures']
        except KeyError:
            # Base Values for First Run
            now = int(time.time())
            self.star = 0
            self.resset_total = 0  # Resets total of entire game life
            self.gained_on_now = 0  # Total gain in current game
            self.gained_on_total = 0  # Total gain of entire game life
            self.cash = 0  # Current available cash for spend ventures
            self.ventures = {
                # rat mean recent_acquisition_time
                "allowance": {"name": "Allowance", "owned": 1, "period": 1, "cost": 0, "revenue": 4, "rat": now},
                "lemonade": {"name": "Lemonade Stand", "owned": 3, "period": 8, "cost": 10, "revenue": 4, "rat": now},
                "paper": {"name": "Paper Route", "owned": 0, "period": 16, "cost": 34, "revenue": 14, "rat": now},
                "fastfood": {"name": "Fast Food Joint", "owned": 0, "period": 32, "cost": 150, "revenue": 49, "rat": now},
                "coffee": {"name": "Coffee Shop", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "bar": {"name": "Bar", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "lawn": {"name": "Lawn Care", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "dining": {"name": "Fine Dining", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "startup": {"name": "Startup", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "construction": {"name": "Construction", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "insurance": {"name": "Insurance", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "record": {"name": "Record Label", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "studio": {"name": "Movie Studio", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "bank": {"name": "Bank", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "team": {"name": "ProSports Team", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "oil": {"name": "Oil & Gas", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now},
                "government": {"name": "Small Government", "owned": 0, "period": 0, "cost": 0, "revenue": 0, "rat": now}
            }
            DB.put('game', star=self.star, resset_total=self.resset_total, gained_on_now=self.gained_on_now,
                   gained_on_total=self.gained_on_total, cash=self.cash, ventures=self.ventures)

    def convert(self, data):
        result = []
        for k, v in data.items():
            tmp = dict(key=k, value=v)
            result.append(tmp)
        return result

    def calculate(self, instance=None):
        ventures = self.ventures
        try:
            rat = DB.get('app')['closed_time']
            del DB.get('app')['closed_time']
        except KeyError:
            rat = int(time.time())

        for key, venture in ventures.items():
            # calculate difference
            try:
                if venture['owned'] > 0:
                    tdiff = rat - venture['rat']
                    if tdiff > 0:
                        times = tdiff / venture['period']
                        # add revenue
                        if times > 0:
                            gained = times * venture['revenue']
                            if gained > 0:
                                self.cash += gained
                                self.gained_on_now += gained
                                self.gained_on_total += gained
                                del gained

                        timeleft = tdiff % venture['period']
                        print timeleft
                        m, s = divmod(timeleft, 60)
                        h, m = divmod(m, 60)
                        ventures[key]['timeleft'] = "%d:%02d:%02d" % (h, m, s)
                    ventures[key]['timeleft'] = "Almost !!"
                else:
                    ventures[key]['timeleft'] = "0:00:00"

                # update recent acquisition time
                ventures[key]['rat'] = rat

            except ZeroDivisionError:
                pass

        DB.put('game', star=self.star, resset_total=self.resset_total, gained_on_now=self.gained_on_now,
               gained_on_total=self.gained_on_total, cash=self.cash, ventures=ventures)

        self.ventures = ventures

        # Update GUI
        try:
            instance.cash.text = '$ {:,.0f}'.format(self.cash)
        except Exception as e:
            print e
            pass

        # return self


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
    timeleft = StringProperty("0:00:00")

    # for garbage collector
    def __del__(self, *args, **kwargs):
        pass


class Main(GridLayout):
    stop = threading.Event()
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
            timeleft=item['value']['timeleft'],
        )

    def infinite_loop(self):
        while True:
            if self.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            Game().calculate(instance=self)
            time.sleep(1)
    pass


class Start(App):
    def on_start(self):
        threading.Thread(target=self.root.infinite_loop).start()

    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        DB.put('app', closed_time=int(time.time()))
        self.root.stop.set()

    def build(self):
        Builder.load_file(os.path.join(KV_DIRECTORY, "main.kv"))
        layout = Main()
        game = Game()
        layout.ventures = game.convert(game.ventures)
        game.calculate()
        return layout
    pass

if __name__ == '__main__':
    Start().run()
