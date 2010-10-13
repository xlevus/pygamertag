import threading
from time import sleep

import pynotify
import pygtk
pygtk.require('2.0')
import gtk
import gobject
gobject.threads_init()

from pygamertag import Gamertag

class _IdleObject(gobject.GObject):
    def emit(self, *args):
        gobject.idle_add(gobject.GObject.emit,self,*args)

class LiveConnectionManager(threading.Thread, _IdleObject):
    __gsignals__ = {
        'update': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT]),
    }

    def __init__(self):
        threading.Thread.__init__(self)
        _IdleObject.__init__(self)

        self.gamertags = []
        self.index = 0
        self.wait = 0
        
        self.stopped = False

    def add_gamertag(self, gt):
        self.gamertags.insert(self.index, Gamertag(gt))
    
    def stop(self):
        self.stopped = True

    def update_next(self):
        if len(self.gamertags) == 0:
            return
        
        if self.index >= len(self.gamertags):
            self.index = 0

        gt = self.gamertags[self.index]
        gt.update()
        print gt
        self.emit('update', gt)
    
    def run(self):
        while not self.stopped:
            if self.wait <= 0:
                self.wait = 60
                self.update_next()
            self.wait -= 0.1
            sleep(0.1)

class Gui(object):
    def __init__(self):
        pynotify.init('xblnotify')
        self.lcm = LiveConnectionManager()
        self.lcm.connect('update', self.update)
        self.lcm.start()

        self._create_left_menu()
        self._create_right_menu()
        self._create_tray()

        self.lcm.add_gamertag('xlevus')

    def _create_tray(self):
        self.tray = gtk.StatusIcon()
        self.tray.set_from_icon_name('live-notify')
        self.tray.connect('popup-menu', self.on_popup_menu)
        self.tray.connect('activate', self.on_activate)
        self.tray.set_visible(True)

    def _create_left_menu(self):
        self.lmenu = gtk.Menu()
        self.lmenu.show_all()

    def _create_right_menu(self):
        self.rmenu = gtk.Menu()

        quit = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
        self.rmenu.append(quit)
        quit.connect("activate", self.exit)

        self.rmenu.show_all()

    def on_activate(self, *args):
        self.lmenu.popup(
                None, None, 
                gtk.status_icon_position_menu, 1,
                gtk.get_current_event_time(), self.tray
        )

    def on_popup_menu(self, status, button, time):
        self.rmenu.popup(
                None, None,
                gtk.status_icon_position_menu, 1,
                time, self.tray,
        )

    def exit(self, *args):
        gtk.main_quit()
        self.lcm.stop()

    def __send_notification(self, title, message, pic, timeout, url):
        #attach the libnotification bubble to the tray
        n = pynotify.Notification(title, message, pic)
        n.attach_to_status_icon(self.tray)
        n.set_timeout(timeout)
        n.show()
        return False

    def send_notification(self, title, message, pic, timeout, url):
        gobject.idle_add(self.__send_notification, title, message, pic, timeout, url)

    def update(self, sender, gamertag):
        print sender, gamertag
        return None
        username = gamertag.gamertag
        self.send_notification("%s online" % username, "%s is online" % username, None, 60, None)

    def main(self):
        gtk.main()

if __name__ == '__main__':
    gui = Gui()
    gui.main()
