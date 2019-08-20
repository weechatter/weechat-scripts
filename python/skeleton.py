# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2019 by nils_2 <weechatter@arcor.de>
#
# Description here: This is a python skeleton script for weechat.
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
# 2012-mm-dd: nils_2, (freenode.#weechat)
#       0.1 : initial release
#
# 2019-03-17: nils_2, (freenode.#weechat)
#       0.2 : py3-ok
#           : add hdata() example server search
#           : add hdata() example hdata_update (FlashCode)
#           : add own config file example
# 2019-06-02: nils_2, (freenode.#weechat)
#       0.3 : improve substitute_colors to work with split windows
# 2019-06-24: nils_2, (freenode.#weechat)
#       0.4 : add localvar
#
# requires: WeeChat version 0.3.x
#
# Development is currently hosted at
# https://github.com/weechatter/weechat-scripts

try:
    import weechat,re

except Exception:
    print('This script must be run under WeeChat.')
    print('Get WeeChat now at: https://www.weechat.org/')
    quit()

SCRIPT_NAME     = 'skeleton'
SCRIPT_AUTHOR   = 'nils_2 <weechatter@arcor.de>'
SCRIPT_VERSION  = '0.3'
SCRIPT_LICENSE  = 'GPL'
SCRIPT_DESC     = 'script description for weechat'

OPTIONS         = {'option_name'        : ('value','help text for option'),
                   'password'           : ('${sec.data.my_password}','see /help secure'),
                  }

# eval_expression():  to match ${color:nn} tags
regex_color=re.compile('\$\{color:([^\{\}]+)\}')

# ==========================[ eval_expression() ]========================
def substitute_colors(text,window):
    if int(version) >= 0x00040200:
        buffer_ptr = weechat.window_get_pointer(window,"buffer")
        return weechat.string_eval_expression(text, {"window": window, "buffer": buffer_ptr}, {}, {})
    # substitute colors in output
    return re.sub(regex_color, lambda match: weechat.color(match.group(1)), text)

# this is for WeeChat >= 0.4.2
# get value from your 'password' option and return the encoded text
password = weechat.string_eval_expression(weechat.config_get_plugin('password'), {}, {}, {})

# this is how to easily use weechat colors in your script
window = weechat.current_window()
text = substitute_colors('my text ${color:yellow}yellow${color:default} colored.',window)


# ================================[ item ]===============================
def bar_item_cb (data, item, window):
    # check for root input bar!
    if not window:
        window = weechat.current_window()

    # get current buffer (for example for split windows!)
    ptr_buffer = weechat.window_get_pointer(window,'buffer')
    if ptr_buffer == '':
        return ''

def update_cb(data, signal, signal_data):
    weechat.bar_item_update(SCRIPT_NAME)
    return weechat.WEECHAT_RC_OK

# ==============================[ hdata() ]==============================
# search for a server in list of servers (with wildcard)
def hdata_server(server_to_search):
    hdata = weechat.hdata_get('irc_server')
    hdata_servers = weechat.hdata_get_list(hdata,'irc_servers')
    server = weechat.hdata_search(hdata, hdata_servers,'${irc_server.name} =* %s' % server_to_search, 1)
    if server:
        is_connected = weechat.hdata_integer(hdata, server, 'is_connected')
        nick_modes = weechat.hdata_string(hdata, server, 'nick_modes')
        buffer_ptr = weechat.hdata_pointer(hdata, server, 'buffer')
    return

def hdata_update_history_cmd(data, buffer, args):
    hdata = weechat.hdata_get('history')

    # add to global history
    weechat.hdata_update(hdata, '', { 'text': 'test global 1' })
    weechat.hdata_update(hdata, '', { 'text': 'test global 2' })

    # add to history of core buffer
    core_buffer = weechat.buffer_search_main()
    weechat.hdata_update(hdata, '', { 'buffer': core_buffer, 'text': 'test core buffer 1' })
    weechat.hdata_update(hdata, '', { 'buffer': core_buffer, 'text': 'test core buffer 2' })

    return weechat.WEECHAT_RC_OK

# =============================[ infolist() ]============================
def infolist_relay():
    infolist_relay = weechat.infolist_get('relay', '', '')
    if infolist_relay:
        while weechat.infolist_next(infolist_relay):
            status = weechat.infolist_integer(infolist_relay, 'status')
            status_string = weechat.infolist_string(infolist_relay, 'status_string')
#            weechat.prnt('', '%d %s' % (status, status_string))
        weechat.infolist_free(infolist_relay)                           # don't forget to free() infolist!
    return weechat.WEECHAT_RC_OK


#
# =============================[ localvars() ]============================
    weechat.buffer_set(buffer, 'localvar_set_<name_of_localvar>', '%s' % value)
    weechat.buffer_get_string(buffer,'localvar_<name_of_localvar>')

# ==========================[ own .conf file ]==========================
def init_own_config_file():
    # set up configuration options and load config file
    global CONFIG_FILE, CONFIG_SECTIONS
    CONFIG_FILE = weechat.config_new(SCRIPT_NAME, '', '')
    CONFIG_SECTIONS = {}
    CONFIG_SECTIONS['section_name'] = weechat.config_new_section(
        CONFIG_FILE, 'section_name', 0, 0, '', '', '', '', '', '', '', '', '', '')

    for option, typ, desc, default in [
            ('option_name',
             'boolean',
             'option description',
             'off'),
            ('option_name2',
             'boolean',
             'option name2 description ',
             'on'),
            ('option_name3',
             'string',
             'option name3 description',
             ''),
            ('option_name4',
             'string',
             'option name4 description',
             'set an default string here'),
        ]:
        weechat.config_new_option(
            CONFIG_FILE, CONFIG_SECTIONS['section_name'], option, typ, desc, '', 0,
            0, default, default, 0, '', '', '', '', '', '')

    weechat.config_read(CONFIG_FILE)

def free_all_config():
    # free all config options, sections and config file
    for section in list(CONFIG_SECTIONS.values()):
        weechat.config_section_free_options(section)
        weechat.config_section_free(section)

    weechat.config_free(CONFIG_FILE)

# ===================[ weechat options & description ]===================
def init_options():
    for option,value in list(OPTIONS.items()):
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, value[0])
            OPTIONS[option] = value[0]
        else:
            OPTIONS[option] = weechat.config_get_plugin(option)
        weechat.config_set_desc_plugin(option,'%s (default: "%s")' % (value[1], value[0]))

def toggle_refresh(pointer, name, value):
    global OPTIONS
    option = name[len('plugins.var.python.' + SCRIPT_NAME + '.'):]        # get optionname
    OPTIONS[option] = value                                               # save new value
    return weechat.WEECHAT_RC_OK

def shutdown_cb():
    weechat.config_write(CONFIG_FILE)
    free_all_config()
    return weechat.WEECHAT_RC_OK
# ================================[ main ]===============================
if __name__ == '__main__':
    global version
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, 'shutdown_cb', ''):
        version = weechat.info_get('version_number', '') or 0

        # get weechat version (0.3.6) and store it
        if int(version) >= 0x00030600:
            # init options from your script
            init_options()

            # init your own config file for your script
            init_own_config_file()

            # create a hook for your options
            weechat.hook_config( 'plugins.var.python.' + SCRIPT_NAME + '.*', 'toggle_refresh', '' )
            # create a new bar item (for scripts running on weechat >= 0.4.2 see script API for additional arguments)
            bar_item = weechat.bar_item_new(SCRIPT_NAME, 'bar_item_cb','')
            # create a hook with signal "buffer_switch" for your item
            weechat.hook_signal('buffer_switch','update_cb','')
            weechat.hook_command('hdata_update_history', 'Add text to history with hdata', '', '', '', 'hdata_update_history_cmd', '')
        else:
            weechat.prnt('','%s%s %s' % (weechat.prefix('error'),SCRIPT_NAME,': needs version 0.3.6 or higher'))
            weechat.command('','/wait 1ms /python unload %s' % SCRIPT_NAME)
