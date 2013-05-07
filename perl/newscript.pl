#
# Copyright (c) 2013 by Nils Görs <weechatter@arcor.de>
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
# History:
# 2012-mm-dd: nils_2, (freenode.#weechat)
#       0.1 : initial release
#
# requires: WeeChat version 0.3.x
#
# Development is currently hosted at
# https://github.com/weechatter/weechat-scripts

use strict;
my $SCRIPT_NAME     = "prgname";
my $SCRIPT_VERSION     = "0.1";
my $SCRIPT_AUTHOR      = "Nils Görs <weechatter\@arcor.de>";
my $SCRIPT_LICENCE     = "GPL3";
my $SCRIPT_DESCR       = "description of script";

# internal values
my $weechat_version = "";

# default values
my %options = ("my_option_1"       => "on",
               "my_option_2"       => "on",
               );

my %options_descr = ("my_option_1"      => "description for my_option_1",
                     "my_option_2"      => "description for my_option_2",
                     );

# -----------------------------[ config ]-----------------------------------
sub init_config
{
    foreach my $option (keys %options)
    {
        if (($weechat_version ne "") && ($weechat_version >= 0x00030500))
        {
            weechat::config_set_desc_plugin( $option,$options_descr{$option} );
        }

        if (!weechat::config_is_set_plugin($option))
        {
            weechat::config_set_plugin($option, $options{$option});
        }
        else
        {
            $options{$option} = weechat::config_get_plugin($option);
        }
    }
}

sub toggle_config_by_set
{
    my ($pointer, $name, $value) = @_;
    $name = substr($name, length("plugins.var.perl.$SCRIPT_NAME."), length($name));
    $options{$name} = $value;
# insert a refresh here
    return weechat::WEECHAT_RC_OK;
}
# -------------------------------[ init ]-------------------------------------
# first function called by a WeeChat-script.
weechat::register($SCRIPT_NAME, $SCRIPT_AUTHOR, $SCRIPT_VERSION,
                  $SCRIPT_LICENCE, $SCRIPT_DESCR, "", "");

weechat::hook_config("plugins.var.perl.$SCRIPT_NAME.*", "toggle_config_by_set", "");

$weechat_version = weechat::info_get("version_number", "");
init_config();