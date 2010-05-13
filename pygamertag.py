#   Copyright 2010 Chris Targett
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License

import urllib2
from xml.etree.ElementTree import ElementTree
from urllib import urlencode

DATA_SOURCE = "http://xboxapi.duncanmackenzie.net/gamertag.ashx"

class InvalidGamertag(Exception):
    pass

class Gamertag(object):
    def __init__(self, gamertag):
        self.gamertag = gamertag

    def update(self):
        url = "%s?%s" % (DATA_SOURCE, urlencode({'GamerTag':self.gamertag}))
        req = urllib2.urlopen(url)

        tree = ElementTree()
        tree.parse(req)

        valid = tree.find("PresenceInfo/Valid")
        if valid.text != 'true':
            raise InvalidGamertag

        self._info = [tree.find("PresenceInfo/Info").text, tree.find("PresenceInfo/Info2").text]
        self._online = tree.find("PresenceInfo/Online").text
        self._status_text = tree.find("PresenceInfo/StatusText").text
        self._title = tree.find("PresenceInfo/Title").text

    def as_dict(self):
        return {
            'gamertag': self.gamertag,
            'info': self._info,
            'online': self._online,
            'status_text': self._status_text,
            'title': self._title,
        }

if __name__ == '__main__':
    gt1 = Gamertag('SuperC0d3m0nkey')
    gt1.update()

    print """
        GamerTag: %(gamertag)s
        Online: %(online)s
        Info: %(info)s
    """ % gt1.as_dict()
        
