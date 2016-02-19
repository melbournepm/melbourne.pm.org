#! /usr/bin/perl -Tw

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
use Time::Local;

use Defs;
use PartsDB;

use PartsPerms;
use PartsContent;
use MainPage;
use MainImage;

use PartsCommon;
use PartsDate;
use PartsWrapper;

### Connect the Database
my $db = CONNECT_TO_DATABASE();
my $output = new CGI;

my $treeLevel = 0;
my $treeDots = PartsCommon::GET_TREE_DOTS($treeLevel);

my %document = (
	treeLevel => $treeLevel,
	title => "$Defs::SITE_NAME_SHORT - Site Map",
	content => [0, "$Defs::SITE_NAME_SHORT - Site Map"],
	pageInfo => ['sitemap'],
	showFull => 1
);
my $documentRef = \%document;

if ($output->cookie('TEXTONLY')) { $documentRef->{'showFull'} = 0; }

my $cookie = "";
if ($output->cookie('SITE_ALLOWS')) { $cookie = '|'.$output->cookie('SITE_ALLOWS').'|'; }
my $contentRef = \%ContentList::CONTENT_LIST;

$documentRef->{'body'}{'main'} = (PartsCommon::GET_THREAD_DETAILS("", $contentRef, 0, -1, 0, 0, $cookie, 1, 1, 1))[3];

my %wrapper = ();  my $wrapRef = \%wrapper;

$wrapRef->{'content'}[0] = 0;
$wrapRef->{'body'} = $documentRef->{'body'}{'main'};
$wrapRef->{'icon'}[0] = "";
$wrapRef->{'content'}[1] = $documentRef->{'title'};

$documentRef->{'body'}{'main'} = PartsWrapper::PREPARE_CONTENT($documentRef, $wrapRef);

PRINT_MAIN_WRAPPER($db, $output, $documentRef);

### Disconnect the Database;
DISCONNECT_FROM_DATABASE($db);
