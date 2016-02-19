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

use Defs;
use PartsPerms;
use ContentList;

use ModDownload;

my $output = new CGI;

my ($check, $tid, $file, $printForm) = split /:/, $output->unescape($ENV{QUERY_STRING}), 4;

my $crypt = PartsPerms::GENERATE_PAGE_CRYPT($file, $tid);

if ($crypt ne $check or $file eq "" or $tid eq "") { goAway(); }

if ($tid) {
	my $contentRef = \%ContentList::CONTENT_LIST;
	my $cookie = "";    if ($output->cookie('SITE_ALLOWS')) { $cookie = '|'.$output->cookie('SITE_ALLOWS').'|'; }
	my $groups = $contentRef->{$tid}{'groups'};

	if ($cookie !~ /\|($groups)\|/ and $cookie !~ /SU/ and $groups) { goAway(); }
}

if ($printForm) {
	use PartsWrapper;
	PartsWrapper::PRINT_DOWNLOADER_FORM($output, $printForm, $check, $tid, $file);
}
else {
	ModDownload::DOWNLOAD_FILE($output, $file);
}

### SUB-ROUTINES ###

sub goAway {
	exit 0;
}
