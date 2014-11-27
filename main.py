import os
import time
import threading
import kivy
kivy.require('1.8.0')
from kivy.adapters.listadapter import ListAdapter
from kivy.app import App, Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.listview import ListItemButton

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
            self.ventures = [
                # rat mean recent_acquisition_time
                {"name": "Allowance", "owned": 1, "period": 4, "cost": 0, "revenue": 4, "rat": now},
                {"name": "Lemonade Stand", "owned": 3, "period": 8, "cost": 10, "revenue": 4, "rat": now},
                {"name": "Paper Route", "owned": 0, "period": 16, "cost": 34, "revenue": 14, "rat": now},
                {"name": "Fast Food Joint", "owned": 0, "period": 32, "cost": 150, "revenue": 49, "rat": now},
                {"name": "Coffee Shop", "owned": 0, "period": 64, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Bar", "owned": 0, "period": 128, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Lawn Care", "owned": 0, "period": 256, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Fine Dining", "owned": 0, "period": 512, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Startup", "owned": 0, "period": 1028, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Construction", "owned": 0, "period": 2048, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Insurance", "owned": 0, "period": 4096, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Record Label", "owned": 0, "period": 8192, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Movie Studio", "owned": 0, "period": 16284, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Bank", "owned": 0, "period": 32568, "cost": 0, "revenue": 0, "rat": now},
                {"name": "ProSports Team", "owned": 0, "period": 65136, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Oil & Gas", "owned": 0, "period": 130272, "cost": 0, "revenue": 0, "rat": now},
                {"name": "Small Government", "owned": 0, "period": 260544, "cost": 0, "revenue": 0, "rat": now}
            ]
            DB.put('game', star=self.star, resset_total=self.resset_total, gained_on_now=self.gained_on_now,
                   gained_on_total=self.gained_on_total, cash=self.cash, ventures=self.ventures)

    # TODO : owned 0'dan  1'e ilk gecisinde o venture icin rat, now'a esitlenmeli. Sadece 0'dan 1'e gecerken
    def calculate(self, instance=None):
        ventures = self.ventures
        try:
            rat = DB.get('app')['closed_time']
            del DB.get('app')['closed_time']
        except KeyError:
            rat = int(time.time())

        for key, venture in enumerate(ventures):
            # calculate difference
            try:
                ventures[key]['key'] = key
                ventures[key]['cash'] = self.cash
                if venture['owned'] > 0:
                    tdiff = rat - venture['rat']
                    ventures[key]['tdiff'] = tdiff
                    # update recent acquisition time
                    ventures[key]['rat'] = int(rat - (tdiff % venture['period']))
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
                    if tdiff < venture['period']:
                        timeleft = venture['period'] - (tdiff % venture['period'])
                        m, s = divmod(timeleft, 60)
                        h, m = divmod(m, 60)
                        ventures[key]['timeleft'] = "%d:%02d:%02d" % (h, m, s)
                    else:
                        ventures[key]['timeleft'] = "Almost !!"
                else:
                    ventures[key]['timeleft'] = "0:00:00"

            except ZeroDivisionError:
                pass

        DB.put('game', star=self.star, resset_total=self.resset_total, gained_on_now=self.gained_on_now,
               gained_on_total=self.gained_on_total, cash=self.cash, ventures=ventures)

        self.ventures = ventures

        # Update GUI
        try:
            instance.cash.text = '$ {:,.0f}'.format(self.cash)
            instance.ventureList.adapter = ListAdapter(data=self.ventures,
                                                       args_converter=instance.args_converter,
                                                       cls=VentureItem)
        except Exception as e:
            print e
            pass

        # return self

    def save(self):
        DB.put('game', star=self.star, resset_total=self.resset_total, gained_on_now=self.gained_on_now,
               gained_on_total=self.gained_on_total, cash=self.cash, ventures=self.ventures)


class MenuToggleButton(ToggleButton):
    def on_press(self):
        if self.identity == "settings":
            print "you are now settings"
    pass


class VentureItem(BoxLayout, ListItemButton):
    background_color = [0, 0, 0, 0]
    key = NumericProperty(0)
    cash = NumericProperty(0)  # Already haved cash
    name = StringProperty("")
    cost = NumericProperty(0)
    owned = NumericProperty(0)
    period = NumericProperty(0)
    revenue = NumericProperty(0)
    timeleft = StringProperty("0:00:00")
    tdiff = NumericProperty(0)

    def do_action(self):
        game = Game()
        # 0 is Allowance, can be upgrade with only achieves
        if self.key != 0 and game.cash > game.ventures[self.key]['cost']:
            game.cash -= game.ventures[self.key]['cost']
            if game.ventures[self.key]['owned'] == 0:
                game.ventures[self.key]['rat'] = int(time.time())
            game.ventures[self.key]['owned'] += 1
            game.ventures[self.key]['revenue'] = int(game.ventures[self.key]['revenue'] + (game.ventures[self.key]['period'] * .25))
            game.ventures[self.key]['cost'] = int(game.ventures[self.key]['cost'] + (game.ventures[self.key]['period'] * 2.5))
            game.ventures[self.key]['period'] = int(game.ventures[self.key]['period'] * 2.5)
            game.save()

    def select(self):
        self.do_action()

    def deselect(self):
        self.select()

    def on_press(self):
        pass

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
            cash=item['cash'],
            name=item['name'],
            cost=item['cost'],
            owned=item['owned'],
            period=item['period'],
            revenue=item['revenue'],
            timeleft=item['timeleft'],
            tdiff=item['tdiff'] if 'tdiff' in item else 0
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
        layout.ventures = game.ventures
        game.calculate()
        return layout
    pass

if __name__ == '__main__':
    Start().run()
