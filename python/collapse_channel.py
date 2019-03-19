# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 by nils_2 <weechatter@arcor.de>
#
# collapse channel buffers from servers without focus
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# 2019-03-13: nils_2, (freenode.#weechat)
#       0.1 : initial release, py3k-ok
#
# 2019-03-19: nils_2, (freenode.#weechat)
#       0.2 : add function exclude hotlist
#
# idea and testing by DJ-ArcAngel

try:
    import weechat,re

except Exception:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: http://www.weechat.org/")
    quit()

SCRIPT_NAME     = "collapse_channel"
SCRIPT_AUTHOR   = "nils_2 <weechatter@arcor.de>"
SCRIPT_VERSION  = "0.2"
SCRIPT_LICENSE  = "GPL"
SCRIPT_DESC     = "collapse channel buffers from servers without focus"

OPTIONS         = { 'server_exclude'        : ('','exclude some server, comma separated list (wildcard "*" is allowed)'),
                    'channel_exclude'       : ('','exclude some channel, comma separated list. This is server independent (wildcard "*" is allowed)'),
                    'single_channel_exclude': ('','exclude specific channels, space separated list (eg. freenode.#weechat)'),
                    'hotlist'               : ('0','unhide buffer by its activity when buffer is added to hotlist (0=off (default), 1=message, 2=private message, 3=highlight, 4=all)'),
                  }

# ================================[ buffer ]===============================
def buffer_opened_closed_cb(data, signal, signal_data):
    global OPTIONS

    # localvar not set in this moment? :-(
#    server = weechat.buffer_get_string(signal_data, 'localvar_server')          # get internal servername
    infolist = weechat.infolist_get('buffer', signal_data, '')
    weechat.infolist_next(infolist)
    plugin_name = weechat.infolist_string(infolist, "plugin_name")
    name = weechat.infolist_string(infolist, "name")
    weechat.infolist_free(infolist)

    # TODO how about matrix script or other non-irc channel buffer? no idea! help is welcome
    if plugin_name != "irc":                                                    # for example /fset, /color etc.pp buffer
        return weechat.WEECHAT_RC_OK

    arg1,arg2 = name.split('.')                                                 # server.freenode or freenode.#weechat
    if arg1 == "server":
        server = arg2
    else:
        server = arg1

    # don't remove /wait
    weechat.command("","/wait 1ms /allchan -exclude=%s /buffer hide" % OPTIONS['channel_exclude'])
    weechat.command(server,"/wait 1ms /allchan -current /buffer unhide")
    exclude_server('')
    single_channel_exclude()
    exclude_hotlist()
    return weechat.WEECHAT_RC_OK

def buffer_switch_cb(data, signal, signal_data):
    global OPTIONS

    server = weechat.buffer_get_string(signal_data, 'localvar_server')          # get internal servername

    # hide all channel but use -exclude
    weechat.command("","/allchan -exclude=%s /buffer hide" % OPTIONS['channel_exclude'])
    if server != '':    # a buffer with server
        weechat.command(server,"/allchan -current /buffer unhide")
    exclude_server('')
    single_channel_exclude()
    exclude_hotlist()
    return weechat.WEECHAT_RC_OK

def window_switch_cb(data, signal, signal_data):
    bufpointer = weechat.window_get_pointer(signal_data,'buffer')
    buffer_switch_cb(data,signal,bufpointer)
    return weechat.WEECHAT_RC_OK

def exclude_server(server):
    global OPTIONS
    for server_exclude in OPTIONS['server_exclude'].split(','):
        if server_exclude == "*":                                               # show buffer for all server
            weechat.command('','/buffer unhide -all')                           # simply unload script, no!? :-)
            break

        # search exclude server in list of servers
        hdata = weechat.hdata_get("irc_server")
        servers = weechat.hdata_get_list(hdata, "irc_servers")
        server = weechat.hdata_search(hdata, servers, "${irc_server.name} =* %s" % server_exclude, 1)
        if server:
#            is_connected    = weechat.hdata_integer(hdata, server, "is_connected")
#            nick_modes      = weechat.hdata_string(hdata, server, "nick_modes")
            buffer_ptr = weechat.hdata_pointer(hdata, server, "buffer")
            weechat.command(buffer_ptr,"/allchan -current /buffer unhide")
    return

def single_channel_exclude():
    if OPTIONS['single_channel_exclude']:
        # space separated list for /buffer unhide
        weechat.command('','/buffer unhide %s' % OPTIONS['single_channel_exclude'])
    return
# ================================[ server ]===============================
def irc_server_disconnected_cb(data, signal, signal_data):
    buffer_switch_cb(data,signal,signal_data)
    return weechat.WEECHAT_RC_OK

def irc_server_connected_cb(data, signal, signal_data):
    buffer_switch_cb(data,signal,signal_data)
    return weechat.WEECHAT_RC_OK

# ================================[ hotlist ]==============================
def hotlist_changed_cb(data, signal, signal_data):
    if not signal_data:
        plugin_name = weechat.buffer_get_string(weechat.current_buffer(), 'localvar_plugin')
        # TODO how about matrix script or other non-irc channel buffer? no idea! help is welcome
        if plugin_name != "irc":                                                    # for example /fset, /color etc.pp buffer
                weechat.command('', '/allchan buffer hide')
    exclude_server('')
    single_channel_exclude()
    exclude_hotlist()
    return weechat.WEECHAT_RC_OK

def exclude_hotlist():
    if OPTIONS['hotlist'] == '0' or OPTIONS['hotlist'] =='':
        return weechat.WEECHAT_RC_OK
    infolist = weechat.infolist_get('hotlist', '', '')
    while weechat.infolist_next(infolist):
        buffer_number = weechat.infolist_integer(infolist, 'buffer_number')
        priority = weechat.infolist_integer(infolist, 'priority')
        if int(OPTIONS['hotlist']) == priority or OPTIONS['hotlist'] == '4':
            weechat.command('','/buffer unhide %s' % buffer_number)
    weechat.infolist_free(infolist)
    return weechat.WEECHAT_RC_OK
# ================================[ weechat options & description ]===============================
def init_options():
    for option,value in list(OPTIONS.items()):
        weechat.config_set_desc_plugin(option, '%s (default: "%s")' % (value[1], value[0]))
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, value[0])
            OPTIONS[option] = value[0]
        else:
            OPTIONS[option] = weechat.config_get_plugin(option)

def toggle_refresh(pointer, name, value):
    global OPTIONS
    option = name[len('plugins.var.python.' + SCRIPT_NAME + '.'):]        # get optionname
    OPTIONS[option] = value                                               # save new value

    # TODO how about matrix script or other non-irc channel buffer? no idea! help is welcome
    server = weechat.buffer_get_string(weechat.current_buffer(), 'localvar_server')
    server_ptr = weechat.buffer_search('irc', 'server.%s' % server)
    buffer_switch_cb('', '', server_ptr)
    return weechat.WEECHAT_RC_OK

# unhide all buffers when script unloads
def shutdown_cb():
    weechat.command("","/buffer unhide -all")
    return weechat.WEECHAT_RC_OK
# ================================[ main ]===============================
if __name__ == "__main__":
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, 'shutdown_cb', ''):
        version = weechat.info_get("version_number", "") or 0
        init_options()
        weechat.hook_config('plugins.var.python.' + SCRIPT_NAME + '.*', 'toggle_refresh', '' )

        # hide all channels
        weechat.command("","/allchan -exclude=%s /buffer hide" % OPTIONS['channel_exclude'])
        # show channel from current server
        server = weechat.buffer_get_string(weechat.current_buffer(), 'localvar_server')
        if server:
            weechat.command(server,"/allchan -current /buffer unhide")
        exclude_hotlist()
        exclude_server('')
        single_channel_exclude()

        weechat.hook_signal('buffer_switch', 'buffer_switch_cb', '')
        weechat.hook_signal('buffer_opened', 'buffer_opened_closed_cb', '')
        weechat.hook_signal('buffer_closed', 'buffer_opened_closed_cb', '')
        weechat.hook_signal('window_switch', 'window_switch_cb', '')
        weechat.hook_signal('irc_server_connected', 'irc_server_connected_cb', '')
        weechat.hook_signal('irc_server_disconnected', 'irc_server_disconnected_cb', '')
        weechat.hook_signal('hotlist_changed', 'hotlist_changed_cb', '')
