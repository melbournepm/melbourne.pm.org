#! /usr/bin/perl

###
# Copyright (C) 2002, 2003 Rodd Clarkson
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###

use strict;
use lib "/home/groupleaders/melbourn/yacmas",".","/home/groupleaders/melbourn/yacmas/parts","/home/groupleaders/melbourn/perl/lib","/home/groupleaders/melbourn/perl/arch";
use CGI ":standard";
use DBI;

use Defs;
use PartsDB;

use PartsPerms;
use AdminPerm;
use MainAdmin;

use PartsCommon;

### Connect the Database

my $db = CONNECT_TO_DATABASE();
my $output = new CGI;

my $action = "";    $action = $output->param('action') or $action = "";
my $section = "";    $section = $output->param('section') or $section = "";
my $server_name = "";    $server_name = $output->param('server_name') or $server_name = "";
my $script_name = "";    $script_name = $output->param('script_name') or $script_name = "";
my $query_string = "";    $query_string = $output->param('query_string') or $query_string = "";

$query_string =~ s/[&?]result=[a-z]+//;

$server_name = "http://$server_name";
if (($script_name ne "/cms/admin/index.cgi" and $script_name ne "/cms/index.cgi") and $query_string ne "") {
	$script_name .= "?$query_string";
}

my ($header, $userID, $result) = PartsPerms::CHECK_LOGIN($db, $output, $action, $section. "");

if (!defined $header or $header eq "") { $header = header('text/html') }
if ($result) {
	if ($script_name =~ /\?/) { $script_name .= "&result=$result"; }
	else                     { $script_name .= "?result=$result"; }
}

open (TMP, ">> /tmp/header");
print TMP $header . "\n\n\n";
close TMP;

print qq[$header
<html>

<head>
	<meta http-equiv="refresh" content="0;url=$server_name$script_name">
</head>

<body bgcolor="#ffffff">

</body></html>];

### Disconnect the Database;
DISCONNECT_FROM_DATABASE($db);










