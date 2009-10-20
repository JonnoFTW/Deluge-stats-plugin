#
# webui.py
#
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007, 2008 Andrew Resch <andrewresch@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA    02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception

import os
from deluge.common import fspeed
from deluge.log import LOG as log
from deluge.ui.client import sclient, aclient
from deluge.plugins.webuipluginbase import WebUIPluginBase
from deluge import component
import graph

api = component.get("WebPluginApi")
forms = api.forms

#pages:
class graph_page:
    @api.deco.deluge_page
    def GET(self, args):
        return api.render.stats.graph()

class network_png:
    @api.deco.check_session
    def GET(self, args):
        self.data = ''
        vars = api.web.input(width = 600, height = 150)
        api.web.header("Content-Type", "image/png")
        g = graph.Graph()
        g.add_stat('download_rate', color=graph.green)
        g.add_stat('upload_rate', color=graph.blue)
        g.set_left_axis(formatter=fspeed, min=10240)
        g.set_interval(1)
        g.sync_request()
        surface = g.draw(int(vars.width), int(vars.height))
        surface.write_to_png(self)
        print self.data

    def write(self, str): #file like object for pango; write_to_png
        self.data += str

class connections_png:
    @api.deco.check_session
    def GET(self, args):
        "testing, not a final graph"
        self.data = ''
        vars = api.web.input(width = 600, height = 150)
        api.web.header("Content-Type", "image/png")
        g = graph.Graph()
        g.add_stat('dht_nodes', color=graph.orange)
        g.add_stat('dht_cache_nodes', color=graph.blue)
        g.add_stat('dht_torrents', color=graph.green)
        g.add_stat('num_connections', color=graph.darkred) #testing : non dht
        g.set_left_axis(formatter=str, min=10)
        g.set_interval(1)
        g.sync_request()
        surface = g.draw(int(vars.width), int(vars.height))
        surface.write_to_png(self)
        print self.data

    def write(self, str): #file like object for pango; write_to_png
        self.data += str

class WebUI(WebUIPluginBase):
    #map url's to classes: [(url,class), ..]
    urls = [
        ('/graph', graph_page),
        ('/graph/network.png', network_png),
        ('/graph/connections.png', connections_png)
    ]

    def enable(self):
        api.config_page_manager.register('plugins', 'stats' ,ConfigForm)
        api.menu_manager.register_admin_page("stats", _("Stats"), "/graph") #<--top menu

    def disable(self):
        api.config_page_manager.deregister('stats')
        api.menu_manager.deregister_admin_page("stats") #<--top menu


class ConfigForm(forms.Form):
    #meta:
    title = _("Graph")

    #load/save:
    def initial_data(self):
        return sclient.stats_get_config()

    def save(self, data):
        cfg = dict(data)
        sclient.stats_set_config(cfg)

    #django newforms magic: define config fields:
    test = forms.CharField(label=_("Test config value"))
