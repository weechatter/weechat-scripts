# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 by nils_2 <weechatter@arcor.de>
#
# Description here: This is a python skeleton script for weechat
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
# requires: WeeChat version 0.3.x
#
# Development is currently hosted at
# https://github.com/weechatter/weechat-scripts

try:
    import weechat,re

except Exception:
    print "This script must be run under WeeChat."
    print "Get WeeChat now at: http://www.weechat.org/"
    quit()

SCRIPT_NAME     = "skeleton"
SCRIPT_AUTHOR   = "nils_2 <weechatter@arcor.de>"
SCRIPT_VERSION  = "0.1"
SCRIPT_LICENSE  = "GPL"
SCRIPT_DESC     = "script description for weechat"

OPTIONS         = {'option_name'        : ('value','help text for option'),
                   'password'           : ('${sec.data.my_password}','see /help secure'),
                  }

# eval_expression():  to match ${color:nn} tags
regex_color=re.compile('\$\{color:([^\{\}]+)\}')

# ==========================[ eval_expression() ]========================
# this is for WeeChat >= 0.4.2
# get value from your 'password' option and return the encoded text
password = weechat.string_eval_expression(weechat.config_get_plugin('password'),{},{},{})

# this is how to easily use weechat colors in your script
text = substitute_colors('my text ${color:yellow}yellow${color:default} colored.')
def substitute_colors(text):
    if int(version) >= 0x00040200:
        return weechat.string_eval_expression(text,{},{},{})
    # substitute colors in output
    return re.sub(regex_color, lambda match: weechat.color(match.group(1)), text)

# ================================[ item ]===============================
def bar_item_cb (data, item, window):
    # check for root input bar!
    if not window:
        window = weechat.current_window()

    # get current buffer (for example for split windows!)
    ptr_buffer = weechat.window_get_pointer(window,"buffer")
    if ptr_buffer == '':
        return ''

def update_cb(data, signal, signal_data):
    weechat.bar_item_update(SCRIPT_NAME)
    return weechat.WEECHAT_RC_OK

# ===================[ weechat options & description ]===================
def init_options():
    for option,value in OPTIONS.items():
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, value[0])
            OPTIONS[option] = value[0]
        else:
            OPTIONS[option] = weechat.config_get_plugin(option)
        weechat.config_set_desc_plugin(option, '%s (default: "%s")' % (value[1], value[0]))

def toggle_refresh(pointer, name, value):
    global OPTIONS
    option = name[len('plugins.var.python.' + SCRIPT_NAME + '.'):]        # get optionname
    OPTIONS[option] = value                                               # save new value
    return weechat.WEECHAT_RC_OK

# ================================[ main ]===============================
if __name__ == "__main__":
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
        version = weechat.info_get("version_number", "") or 0

        # get weechat version (0.3.6) and store it
        if int(version) >= 0x00030600:
            # init options from your script
            init_options()
            # create a hook for your options
            weechat.hook_config( 'plugins.var.python.' + SCRIPT_NAME + '.*', 'toggle_refresh', '' )
            # create a new bar item (for scripts running on weechat >= 0.4.2 see script API for additional arguments)
            bar_item = weechat.bar_item_new(SCRIPT_NAME, 'bar_item_cb','')
            # create a hook with signal "buffer_switch" for your item
            weechat.hook_signal("buffer_switch","update_cb","")
        else:
            weechat.prnt("","%s%s %s" % (weechat.prefix("error"),SCRIPT_NAME,": needs version 0.3.6 or higher"))
            weechat.command("","/wait 1ms /python unload %s" % SCRIPT_NAME)
