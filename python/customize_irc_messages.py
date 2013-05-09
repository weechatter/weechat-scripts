# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 by nils_2 <weechatter@arcor.de>
#
# to customise IRC messages (like join/part/quit/kill)
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
# 2012-05-23 > 2013-03-03: nils_2, (freenode.#weechat)
#       0.1 : under dev
#
# requires: WeeChat version 0.3.5
#
# filter the original IRC messages:
# /filter add joinquit * irc_join,irc_part,irc_quit *
#
# Development is currently hosted at
# https://github.com/weechatter/weechat-scripts

try:
    import weechat,re

except Exception:
    print "This script must be run under WeeChat."
    print "Get WeeChat now at: http://www.weechat.org/"
    quit()

SCRIPT_NAME     = "customize_irc_messages"
SCRIPT_AUTHOR   = "nils_2 <weechatter@arcor.de>"
SCRIPT_VERSION  = "0.1"
SCRIPT_LICENSE  = "GPL"
SCRIPT_DESC     = "customise IRC messages (like join/part/quit/kill)"

OPTIONS         = { 'debug'             : ('off','show debug messages'),
                    'join_message'      : ('${blue}%N${default} (${lightcyan}%U@%H${default}) ${green}has joined ${white}%C',
                                           'customize join message. possible items: %N = nick, %U = user, %H = host, %C = channel'),
                    'part_message'      : ('${blue}%N${default} (${lightcyan}%U@%H${default}) ${red}has left ${white}%C ${green}(${default}%M${green})',
                                           'customize part message. possible items: %N = nick, %U = user, %H = host, %C = channel, %M = message'),
                    'quit_message'      : ('${blue}%N${default} (${lightcyan}%U@%H${default}) ${red}has quit ${green}(${default}%M${green})',
                                           'customize quit message. possible items: %N = nick, %U = user, %H = host, %M = message'),
                    'kick_message'      : ('${white}%N${default} ${red}has kicked${default} ${blue}%K${default} ${green}(${default}%M${green})',
                                           'customize kill message. possible items: %N = nick, %U = user, %H = host, %K = kicked user, %C = channel, %M = message'),
                    'action_message'    : ('${white}%N${default} ${red}has kicked${default} ${blue}%K${default} ${green}(${default}%M${green})',
                                           'customize action message. possible items: %N = nick, %U = user, %H = host, %K = kicked user, %C = channel, %M = message'),
                    'no_log'            : ('on','don\'t log customize messages'),
                  }
# ================================[ regex ]===============================
# regexp to match ${color} tags
regex_color=re.compile('\$\{([^\{\}]+)\}')
# regexp to match ${optional string} tags
regex_optional_tags=re.compile('%\{[^\{\}]+\}')

#(nick!~user@host)
regex_get_user=re.compile(r"""
(
    (?P<from>
        (?P<from_nick>.+?)
        !
        (?P<from_user>.+?)
        @
        (?P<from_host>.+)
    )
)
""", re.VERBOSE)
# ================================[ hook_modifier() ]===============================
# modifier_data = internal server name
def customize_join_cb(data, modifier, modifier_data, string):
    message = weechat.config_get_plugin('join_message')
    if message == '':
        return string

    parsed = get_hashtable(string)
    if parsed['nick'] == own_nick(modifier_data):
        return string

    parsed['message'] = ""                      # dummy. no message for irc_JOIN
    parsed['kicked_nick'] = ''                  # dummy. no irc_KICK here
    message = create_output(message,parsed,'join')

    if OPTIONS['debug'] == 'on':
        weechat.prnt("",string)
        weechat.prnt("",parsed['channel'])
        weechat.prnt("",parsed['message'])

    buffer_ptr = weechat.buffer_search('irc',"%s.%s" % (modifier_data,parsed['channel']))

    prefix = weechat.config_string(weechat.config_get('weechat.look.prefix_join'))
    prefix_color = weechat.color(weechat.config_color(weechat.config_get('weechat.color.chat_prefix_join')))
    prefix = substitute_colors(prefix)
    message_tags = ''

    if weechat.config_get_plugin('no_log').lower() == 'on':
        message_tags = 'no_log'
    weechat.prnt_date_tags(buffer_ptr,0,message_tags,'%s%s\t%s' % (prefix_color,prefix,message))
               
    return string

# modifier_data = internal server name
def customize_part_cb(data, modifier, modifier_data, string):
    message = weechat.config_get_plugin('part_message')
    if message == '':
        return string

    parsed = get_hashtable(string)
    if parsed['nick'] == own_nick(modifier_data):
        return string

    parsed['kicked_nick'] = ''                  # dummy. no irc_KICK here
    message = create_output(message,parsed,'part')

    if OPTIONS['debug'] == 'on':
        weechat.prnt("","debug mode: irc_part")
        weechat.prnt("","string: %s" % string)
        weechat.prnt("",parsed['channel'])
        weechat.prnt("",parsed['message'])

    buffer_ptr = weechat.buffer_search('irc',"%s.%s" % (modifier_data,parsed['channel']))

    prefix = weechat.config_string(weechat.config_get('weechat.look.prefix_quit'))
    prefix_color = weechat.color(weechat.config_color(weechat.config_get('weechat.color.chat_prefix_quit')))
    prefix = substitute_colors(prefix)
    message_tags = ''

    if weechat.config_get_plugin('no_log').lower() == 'on':
        message_tags = 'no_log'
    weechat.prnt_date_tags(buffer_ptr,0,message_tags,'%s%s\t%s' % (prefix_color,prefix,message))
        
    return string

def customize_quit_cb(data, modifier, modifier_data, string):
    message = weechat.config_get_plugin('quit_message')
    if message == '':
        return string

    parsed = get_hashtable(string)
    if parsed['nick'] == own_nick(modifier_data):
        return string

    parsed['kicked_nick'] = ''                  # dummy. no irc_KICK here
    message = create_output(message,parsed,'quit')

    if OPTIONS['debug'] == 'on':
        weechat.prnt("","debug mode: irc_quit")
        weechat.prnt("","string: %s" % string)
        weechat.prnt("",parsed['channel'])
        weechat.prnt("",parsed['message'])

    buffer_ptr = weechat.buffer_search('irc',"%s.%s" % (modifier_data,parsed['channel']))

    prefix = weechat.config_string(weechat.config_get('weechat.look.prefix_quit'))
    prefix_color = weechat.color(weechat.config_color(weechat.config_get('weechat.color.chat_prefix_quit')))
    prefix = substitute_colors(prefix)
    message_tags = ''


    ptr_infolist = weechat.infolist_get("buffer", "", "")
    while weechat.infolist_next(ptr_infolist):
        ptr_buffer = weechat.infolist_pointer(ptr_infolist, "pointer")
        if weechat.buffer_get_string(ptr_buffer, 'plugin') != 'irc':
            continue
        localvar_type = weechat.buffer_get_string(ptr_buffer, 'localvar_type')
        localvar_server = weechat.buffer_get_string(ptr_buffer, 'localvar_server')
        if localvar_type != 'channel' or localvar_server != modifier_data:
            continue
#        localvar_channel = weechat.buffer_get_string(buffer, 'localvar_channel')
        if (weechat_nicklist_search_nick(ptr_buffer,parsed['nick'])):
            if weechat.config_get_plugin('no_log').lower() == 'on':
                message_tags = 'no_log'
                weechat.prnt_date_tags(ptr_buffer,0,message_tags,'%s%s\t%s' % (prefix_color,prefix,message))
    weechat.infolist_free(ptr_infolist)

    return string

def customize_kick_cb(data, modifier, modifier_data, string):
    message = weechat.config_get_plugin('kick_message')
    if message == '':
        return string

    parsed = get_hashtable(string)
    try:
        parsed['kicked_nick'] = parsed['arguments'].split(' ', 1)[1]
        parsed['kicked_nick'] = parsed['kicked_nick'].split(' :', 1)[0]
    except:
        parsed['kicked_nick'] = ''

    message = create_output(message,parsed,'kick')

    if OPTIONS['debug'] == 'on':
        weechat.prnt("",string)
        weechat.prnt("",parsed['channel'])
        weechat.prnt("",parsed['message'])

    buffer_ptr = weechat.buffer_search('irc',"%s.%s" % (modifier_data,parsed['channel']))
    if not (buffer_ptr):
        return string

    prefix = weechat.config_string(weechat.config_get('weechat.look.prefix_quit'))
    prefix_color = weechat.color(weechat.config_color(weechat.config_get('weechat.color.chat_prefix_quit')))
    message_tags = ''

    if weechat.config_get_plugin('no_log').lower() == 'on':
        message_tags = 'no_log'
    weechat.prnt_date_tags(buffer_ptr,0,message_tags,'%s%s\t%s' % (prefix_color,prefix,message))

    return string

def customize_cb(data, modifier, modifier_data, string):
    if OPTIONS['debug'] == 'on':
        weechat.prnt("",data)
        weechat.prnt("",modifier)
        weechat.prnt("",modifier_data)
        weechat.prnt("",string)
    return string
# ================================[ sub routines ]===============================
def own_nick(server_name):
    return weechat.info_get('irc_nick',server_name)

#  pointer to nick found, NULL if not found
def weechat_nicklist_search_nick(ptr_buffer,nick):
    return weechat.nicklist_search_nick(ptr_buffer, "", nick)

def substitute_colors(text):
    # substitute colors in output
    return re.sub(regex_color, lambda match: weechat.color(match.group(1)), text)

def create_output(message,parsed,irc_mode):
    if irc_mode == 'quit':
        parsed['arguments'] = parsed['arguments'][1:]
        tags = {'%N': parsed['nick'],
                '%U': parsed['user'],
                '%H': parsed['host'],
                '%M': parsed['arguments'],
                '%K': parsed['kicked_nick'],
                '%C': parsed['channel']}
    else:
        tags = {'%N': parsed['nick'],
                '%U': parsed['user'],
                '%H': parsed['host'],
                '%M': parsed['message'],
                '%K': parsed['kicked_nick'],
                '%C': parsed['channel']}

    message = substitute_colors(message)
    for tag in tags.keys():
        message = message.replace(tag, tags[tag])

    return message

def get_hashtable(string):
    parsed = weechat.info_get_hashtable('irc_message_parse', dict(message=string))
    try:
        parsed['message'] = parsed['arguments'].split(' :', 1)[1]
    except:
        parsed['message'] = ""
    match = regex_get_user.match(parsed['host'])
    result = match.groupdict()

    parsed['user'] = result['from_user']
    parsed['host'] = result['from_host']

    if OPTIONS['debug'] == 'on':
        weechat.prnt("","debug_mode: hashtable")
        weechat.prnt("","string: %s" % string)
        weechat.prnt("","nick: %s" % parsed['nick'])
        weechat.prnt("","from_user: %s" % parsed['user'])
        weechat.prnt("","from_host: %s" % parsed['host'])
        weechat.prnt("","channel: %s" % parsed['channel'])
        weechat.prnt("","message: %s" % parsed['message'])
        weechat.prnt("","arguments: %s" % parsed['arguments'])
        regex_get_channel=re.match(r'#(.*)',parsed['arguments'])
        if channel != '':
            weechat.prnt("",regex_get_channel.group())
        weechat.prnt("","---end---")
    return parsed
# ================================[ weechat options & description ]===============================
def init_options():
    for option,value in OPTIONS.items():
        if not weechat.config_get_plugin(option):
            weechat.config_set_plugin(option, value[0])
        else:
            OPTIONS[option] = weechat.config_get_plugin(option)
        weechat.config_set_desc_plugin(option, '%s (default: "%s")' % (value[1], value[0]))

def customize_join_cb_signal(data, signal, signal_data):
    weechat.prnt("","data: %s   signal: %s  signal_data: %s" % (data,signal,signal_data))
    message = weechat.config_get_plugin('join_message')
    if message == '':
        return weechat.WEECHAT_RC_OK

    parsed = get_hashtable(signal_data)
    if parsed['nick'] == own_nick(signal.split(',', 1)[0]):
        return weechat.WEECHAT_RC_OK

    parsed['message'] = "" # dummy. no message for JOIN
    parsed['kicked_nick'] = '' # dummy. no KICK here
    message = create_output(message,parsed,'join')

    buffer_ptr = weechat.buffer_search('irc',"%s.%s" % (signal.split(',', 1)[0],parsed['channel']))

    prefix = weechat.config_string(weechat.config_get('weechat.look.prefix_join'))
    prefix_color = weechat.color(weechat.config_color(weechat.config_get('weechat.color.chat_prefix_join')))
    message_tags = ''

    if weechat.config_get_plugin('no_log').lower() == 'on':
        message_tags = 'no_log'
    weechat.prnt_date_tags(buffer_ptr,0,message_tags,'%s%s\t%s' % (prefix_color,prefix,message))

    return weechat.WEECHAT_RC_OK
# ================================[ main ]===============================
if __name__ == "__main__":
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
        version = weechat.info_get("version_number", "") or 0
        if int(version) >= 0x00030500:
            init_options()
#            weechat.hook_modifier("weechat_print","customize_cb","")
#            weechat.hook_signal("*,irc_raw_in_JOIN","customize_join_cb_signal","")
            weechat.hook_modifier("irc_in2_JOIN","customize_join_cb","")
            weechat.hook_modifier("irc_in2_PART","customize_part_cb","")
            weechat.hook_modifier("irc_in_QUIT","customize_quit_cb","")
            weechat.hook_modifier("irc_in2_KICK","customize_kick_cb","")
        else:
            weechat.prnt("","%s%s %s" % (weechat.prefix("error"),SCRIPT_NAME,": needs version 0.3.4 or higher"))
            weechat.command("","/wait 1ms /python unload %s" % SCRIPT_NAME)
