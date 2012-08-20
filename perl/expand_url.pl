#
# Copyright (c) 2011-2012 by Nils Görs <weechatter@arcor.de>
#
# Get information on a short URL. Find out where it goes.
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
# 0.5  : fix expand_own() tag "prefix_nick_ccc" (thanks roughnecks)
#      : add new options: "prefix" and "color_prefix"
#      : improved option "expander". Now more than one expander can be used (Thanks FiXato for some information about URLs)
# 0.4  : some code optimizations
# 0.3  : fixed: script won't worked if more than one URL per message exists.
#      : fixed: output buffer wasn't correctly set for each message.
#      : fixed: missing return in callback for hook_config()
#      : added: if an URI exists twice in a message script will only print URI once.
#      : added: option "expand_own" (default: off).
#      : added: only private and public messages with string "://" will be caught
# 0.2  : add "://" in call to hook_print() (thanks to xt)
# 0.1  : internal release
#
# "expand" option is a space separated list.
#
# requirements:
# - URI::Find

use strict;
use URI::Find;

my $PRGNAME	= "expand_url";
my $version	= "0.5";
my $AUTHOR      = "Nils Görs <weechatter\@arcor.de>";
my $LICENSE     = "GPL3";
my $DESC	= "Get information on a short URL. Find out where it goes.";
# default values
my %options = (	"shortener"             =>      "goo.gl|tiny.cc|bit.ly|is.gd|tinyurl.com|ur1.ca",
                "expander"              =>      "http://untiny.me/api/1.0/extract?url= http://api.longurl.org/v1/expand?url= http://expandurl.com/api/v1/?url=",
                "color"                 =>      "blue",
                "prefix"                =>      "[url]",
                "color_prefix"          =>      "blue",
                "expand_own"            =>      "off",
);

my %uris;
my $uri_only;
my @url_expander;                       # used expander
my $url_expander;                       # store number of expander
my $expand_counter = -1;
my $weechat_version;

sub hook_print_cb{
my ( $data, $buffer, $date, $tags, $displayed, $highlight, $prefix, $message ) = @_;
my $tags2 = ",$tags,";
#return weechat::WEECHAT_RC_OK if ( not $tags2 =~ /,notify_[^,]+,/ ); # return if message is not from a nick.
#weechat::print("",$tags);

if ( $options{expand_own} eq "off" ){
  # get servername from buffer
  my $infolist = weechat::infolist_get("buffer",$buffer,"");
  weechat::infolist_next($infolist);
  my ($servername, undef) = split( /\./, weechat::infolist_string($infolist,"name") );
  weechat::infolist_free($infolist);

  my $my_nick = weechat::info_get( "irc_nick", $servername );   # get own nick
#  if ( $tags2 =~ /,nick_[$my_nick,]+,/ ){
  if ( $tags2 =~ m/(^|,)nick_[$my_nick,]+,/ ){
      return weechat::WEECHAT_RC_OK;
  }
}

  %uris = ();
  my $finder = URI::Find->new( \&uri_find_cb );
  my $how_many_found = $finder->find(\$message);                # search uri in message. result in $uri_only

  if ( $how_many_found >= 1 ){                                  # does message contains an url?
    my @uris = keys %uris;
    foreach my $uri (@uris) {
        if ($uri =~ m/$options{shortener}/) {                   # known shortener used?
            if ( $url_expander >= 1 ){
                $expand_counter = 1;
                my $hook_process = weechat::hook_process("url:".$url_expander[0].$uri, 10000 ,"hook_process_cb","$buffer $uri");
            }
        }
    }
  }
return weechat::WEECHAT_RC_OK;
}

# callback from hook_process()
sub hook_process_cb {
my ($data, $command, $return_code, $out, $err) = @_;
    my ($buffer,$uri) = split(" ",$data);
    my $expand_URI;
    my $how_many_found = 0;
    # output not empty. Try to catch long URI
    if ($out ne ""){
        my @array = split(/\n/,$out);
        foreach ( @array ){
            $uri_only = "";
            my $finder = URI::Find->new( \&uri_find_one_cb );
            $how_many_found = $finder->find(\$_);
            if ( $how_many_found >= 1 ){                              # does message contains an url?
                weechat::print($buffer, weechat::color($options{color_prefix}).
                                        $options{prefix}."\t".
                                        weechat::color($options{color}).
                                        $uri_only);
                last;
            }
        }
        return weechat::WEECHAT_RC_OK;
    }

    return weechat::WEECHAT_RC_OK if ($expand_counter == -1);

    if ($return_code > 0 or $out eq "" or $expand_counter > 0){
        $expand_URI = $url_expander[$expand_counter];
        $expand_counter++;
    }
    if ($expand_counter > $url_expander){
        $expand_counter = -1;
        return weechat::WEECHAT_RC_OK;
    }
    if (defined $expand_URI and $return_code > 0 or $out eq "" or $expand_counter > 0){
        weechat::hook_process("url:".$expand_URI.$uri, 10000 ,"hook_process_cb","$buffer $uri");
    }
return weechat::WEECHAT_RC_OK;
}

# callback from URI::Find
sub uri_find_cb {
my ( $uri_url, $uri ) = @_;
  $uris{$uri}++;
return "";
}

sub uri_find_one_cb {
my ( $uri_url, $uri ) = @_;
  $uri_only = $uri;
return "";
}

# get settings or set them if they do not exists.
sub init_config{
    foreach my $option (keys %options){
        if (!weechat::config_is_set_plugin($option)){
            weechat::config_set_plugin($option, $options{$option});
        }
        else{
            $options{$option} = weechat::config_get_plugin($option);
            if ($option eq "expander"){
                @url_expander = split(/ /,$options{expander});      # split expander
                $url_expander = @url_expander;
            }
        }
    }
}
# changes in settings hooked by hook_config()?
sub toggle_config_by_set{
my ( $pointer, $name, $value ) = @_;
    $name = substr($name,length("plugins.var.perl.$PRGNAME."),length($name));
    $options{$name} = $value;
    if ($name eq "expander"){
        @url_expander = split(/ /,$options{expander});      # split expander
        $url_expander = @url_expander;
    }
return weechat::WEECHAT_RC_OK ;
}

# first function called by a WeeChat-script.
weechat::register($PRGNAME, $AUTHOR, $version,$LICENSE, $DESC, "", "");

  $weechat_version = weechat::info_get("version_number", "");
  if (( $weechat_version eq "" ) or ( $weechat_version < 0x00030700 )){
    weechat::print("",weechat::prefix("error")."$PRGNAME: needs WeeChat >= 0.3.7. Please upgrade: http://www.weechat.org/");
    weechat::command("","/wait 1ms /perl unload $PRGNAME");
  }

init_config();

#weechat::hook_print("", "", "://", 1, "hook_print_cb", "");       # only public messages with string "://" will be caught!
weechat::hook_print("", "notify_message", "://", 1, "hook_print_cb", "");       # only public messages with string "://" will be caught!
weechat::hook_print("", "notify_private", "://", 1, "hook_print_cb", "");       # only private messages with string "://" will be caught!
weechat::hook_print("", "notify_highlight", "://", 1, "hook_print_cb", "");     # only highlight messages with string "://" will be caught!
weechat::hook_print("", "notify_none", "://", 1, "hook_print_cb", "");          # check own messages
weechat::hook_config("plugins.var.perl.$PRGNAME.*", "toggle_config_by_set", "");# options changed?
