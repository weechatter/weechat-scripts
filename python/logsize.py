# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2019 by nils_2 <weechatter@arcor.de>
#
# Display size of current logfile in item-bar
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
# 2025-03-06: orkim (libera.#weechat)
#       0.5 : script always updates on buffer/window switch now
#           : optionally, a timer can update the item in the background (e.g. while staying in one buffer)
#           : fixed hook_process() call to update results on completion
#           : fixed timer for updating log size without switching buffers/windows
#           : fixed options help text displaying
#           : fixed update for fset/script buffers/etc without logs
#           : clear output on buffer/window switch
#           : adjusted defaults
#           : adjusted help text
#           : added a "auto" to file size units
#           : removed unused/unreachable code
#           : general cleanup/comments/renames/etc
# 2019-07-12: nils_2 (freenode.#weechat)
#       0.4 : option "display" is evaluated
#           : use hook_process("wc") to not stall weechat anymore
#           : new function: refresh only on buffer/window switch
#           : make script compatible with Python 3.x
# 2013-01-07: nils_2 (freenode.#weechat)
#       0.3 : missing logfile caused a crash (thanks swimmer)
#           : add support of more than one window
#           : two new options "log_disabled" and "file_not_found"
# 2012-11-22: nils_2 (freenode.#weechat)
#       0.2 : bug on first startup removed (thanks swimmer)
# 2012-01-14: nils_2 (freenode.#weechat)
#       0.1 : initial release
#
# How to use:
# add item "logsize" to option "weechat.bar.status.items"
#
# Development is currently hosted at
# https://github.com/weechatter/weechat-scripts

from __future__ import print_function
from builtins import str

try:
    import weechat, re

except Exception:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: https://weechat.org")
    quit()

SCRIPT_NAME     = "logsize"
SCRIPT_AUTHOR   = "nils_2 <weechatter@arcor.de>"
SCRIPT_VERSION  = "0.5"
SCRIPT_LICENSE  = "GPL"
SCRIPT_DESC     = "display size of current logfile in item-bar"
OPTIONS         = { "refresh"       : ("60","Refresh timer (in seconds). Setting 0 = refresh only on buffer or window switch."),
                    "size"          : ("A","File size units in B/KB/MB/GB/TB or A for 'Auto'."),
                    "display"       : ("%F","Possible item: %W = words in log, %L = lines in log, or %F for file size (in units). (Content is evaluated, e.g. you can use colors with format \"${color:xxx}\", see /help eval)."),
                    "log_disabled"  : ("","Displays in item, when logger is disabled for buffer."),
                    "file_not_found": ("","Displays in item, when logfile wasn't found."),
                    }

hooks           = { "timer": "" }
output          = ""

# regexp to match ${color} tags
regex_color=re.compile('\$\{([^\{\}]+)\}')

# regexp to match ${optional string} tags
regex_optional_tags=re.compile('%\{[^\{\}]+\}')


# ================================[ size ]===============================
def sizecheck(filesize):
    filesize = int(filesize)
    if OPTIONS["size"].lower() == "a":
        units = ['b', 'K', 'M', 'G', 'T']
        divides = 0
        while filesize > 1024 and divides < 4:
            filesize = filesize / 1024
            divides += 1
        filesize = "%.2f" % filesize
        size = units[divides]
    elif OPTIONS["size"].lower() == "kb":
        filesize = "%.2f" % (filesize / 1024)
        size = "K"
    elif OPTIONS["size"].lower() == "mb":
        filesize = "%.2f" % (filesize / 1024 / 1024)
        size = "M"
    elif OPTIONS["size"].lower() == "gb":
        filesize = "%.2f" % (filesize / 1024 / 1024 / 1024)
        size = "G"
    elif OPTIONS["size"].lower() == "tb":
        filesize = "%.2f" % (filesize / 1024 / 1024 / 1024 / 1024)
        size = "T"
    else:
        filesize = "%.0f" % filesize
        size = "b"
    return "%s%s" % (filesize,size)


# ================================[ weechat item ]===============================
def show_item (data, item, window):
    global output
    return output


def get_logfile(ptr_buffer):
    log_filename = ""
    log_enabled = 0
    infolist = weechat.infolist_get('logger_buffer','','')
    while weechat.infolist_next(infolist):
        bpointer = weechat.infolist_pointer(infolist, 'buffer')
        if ptr_buffer == bpointer:
            log_filename = weechat.infolist_string(infolist, 'log_filename')
            log_enabled = weechat.infolist_integer(infolist, 'log_enabled')
            log_level = weechat.infolist_integer(infolist, 'log_level')
    weechat.infolist_free(infolist)                  # free infolist()

    return (log_filename,log_enabled)


def get_file_information(ptr_buffer):
    global output

    (logfile,log_enabled) = get_logfile(ptr_buffer)
    if not log_enabled:
        output = OPTIONS["log_disabled"]
        weechat.bar_item_update(SCRIPT_NAME)
        return

    if logfile != '':
        # fork process to get data for item
        weechat.hook_process("wc %s" % logfile, 5000, "my_hook_process_cb", "")
    else:
        # even though logging is not disabled, it may not be logging
        #  example: fset buffer/script buffer/etc

        # logfile is empty, clear item
        output = ''
        weechat.bar_item_update(SCRIPT_NAME)

    return


def substitute_colors(text):
    if int(version) >= 0x00040200:
        return weechat.string_eval_expression(text,{},{},{})
    # substitute colors in output
    return re.sub(regex_color, lambda match: weechat.color(match.group(1)), text)


def item_update(data, remaining_calls):
    get_file_information(weechat.current_buffer())
    return weechat.WEECHAT_RC_OK


# ================================[ hook process]===============================
def my_hook_process_cb(data, command, return_code, out, err):
    global output
    if return_code == weechat.WEECHAT_HOOK_PROCESS_ERROR:
        weechat.prnt("", "Error with command '%s'" % command)
        return weechat.WEECHAT_RC_OK
#    if return_code >= 0:
#        weechat.prnt("", "return_code = %d" % return_code)
    if out != "":
        out_split = out.split()
        # newline / word / bytes / filename
        lines = out_split[0]
        words = out_split[1]
        flength = sizecheck(out_split[2])

        tags = {'%L': str(lines),
                '%W': str(words),
                '%F': str(flength)}

        output = substitute_colors(OPTIONS['display'])
        # replace mandatory tags
        for tag in list(tags.keys()):
            output = output.replace(tag, tags[tag])

        weechat.bar_item_update(SCRIPT_NAME)
    if err != "":
        weechat.prnt("", "stderr: %s" % err)
    return weechat.WEECHAT_RC_OK


# ================================[ weechat hook ]===============================
def window_switch_cb(data, signal, signal_data):
    global output
    output = ''
    weechat.bar_item_update(SCRIPT_NAME)
    get_file_information(weechat.current_buffer())
    return weechat.WEECHAT_RC_OK


def buffer_switch_cb(data, signal, signal_data):
    global output
    output = ''
    weechat.bar_item_update(SCRIPT_NAME)
    get_file_information(weechat.current_buffer())
    return weechat.WEECHAT_RC_OK


def unhook_timer():
    global hooks
    if hooks["timer"] != "":
        weechat.unhook(hooks["timer"])
        hooks["timer"] = ""


def hook_timer():
    global hooks
    hooks["timer"] = weechat.hook_timer(int(OPTIONS["refresh"]) * 1000, 0, 0, 'item_update', '')
    if hooks["timer"] == 0:
        weechat.prnt('',"%s: can't enable %s, hook failed" % (weechat.prefix("error"), SCRIPT_NAME))
        return 0
    return 1


# ================================[ weechat options and description ]===============================
def monitor_config_options(pointer, name, value):
    global hooks
    option = name[len('plugins.var.python.' + SCRIPT_NAME + '.'):]        # get optionname
    OPTIONS[option] = value                                               # save new value

    # monitor the 'refresh' option
    if option == 'refresh':                                               # option "refresh" changed by user?
        if hooks["timer"] != "":                                          # timer currently running?
            if OPTIONS['refresh'] != "0":                                 # new user setting not zero?
                unhook_timer()
                hook_timer()
            else:
                unhook_timer()                                            # user switched timer off
        elif hooks["timer"] == "":                                        # hook is empty
            if OPTIONS['refresh'] != "0":                                 # option is not zero!
                hook_timer()                                              # install hook

    return weechat.WEECHAT_RC_OK


def init_options():
    global OPTIONS

    for option, value in list(OPTIONS.items()):
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, value[0])
            OPTIONS[option] = value[0]
        else:
            OPTIONS[option] = weechat.config_get_plugin(option)

        # set description for option
        weechat.config_set_desc_plugin(option, '%s (default: "%s")' % (value[1], value[0]))


# ================================[ main ]===============================
if __name__ == "__main__":
  if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
      version = weechat.info_get("version_number", "") or 0

      # initially set (or read in) current options
      init_options()

      # monitor any config options updates
      weechat.hook_config( 'plugins.var.python.' + SCRIPT_NAME + '.*', 'monitor_config_options', '' )

      # our logsize bar item
      weechat.bar_item_new(SCRIPT_NAME, 'show_item','')

      # optional: update on a timer
      if OPTIONS["refresh"] != "0":
          hook_timer()

      # udpate on window/buffer switch
      weechat.hook_signal("buffer_switch","buffer_switch_cb","")
      weechat.hook_signal("window_switch","window_switch_cb","")

      # do initial logsize update
      get_file_information(weechat.current_buffer())
