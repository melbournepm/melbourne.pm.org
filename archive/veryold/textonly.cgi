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

my $output = new CGI;

my $showFull = 1;    if ($output->cookie('TEXTONLY')) { $showFull = 0; }
my $return = "";    $return = $output->param('return') or $return = "";

my $textOnly_cookie = $output->cookie( -name=>'TEXTONLY', -value=>$showFull, -domain=>"$Defs::DOMAIN", -path=>'/', -secure=>0 );

print $output->header( -cookie=>[$textOnly_cookie] );

print qq[<html>
<head><meta http-equiv="refresh" content="0;url=$return"></head>
<body bgcolor="#ffffff"></body></html>];

