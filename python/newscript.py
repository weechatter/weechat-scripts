# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 by nils_2 <weechatter@arcor.de>
#
# description
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

SCRIPT_NAME     = ""
SCRIPT_AUTHOR   = "nils_2 <weechatter@arcor.de>"
SCRIPT_VERSION  = "0.1"
SCRIPT_LICENSE  = "GPL"
SCRIPT_DESC     = "description"

OPTIONS         = { 'new_option'        : ('option','help text'),
                  }


# ================================[ weechat options & description ]===============================
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

#        if int(version) >= 0x00030600:
#            init_options()
#            weechat.hook_config( 'plugins.var.python.' + SCRIPT_NAME + '.*', 'toggle_refresh', '' )
#        else:
#            weechat.prnt("","%s%s %s" % (weechat.prefix("error"),SCRIPT_NAME,": needs version 0.3.6 or higher"))
#            weechat.command("","/wait 1ms /python unload %s" % SCRIPT_NAME)
