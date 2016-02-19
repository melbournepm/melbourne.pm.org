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
no strict "refs";

use lib "/home/groupleaders/melbourn/yacmas",".","/home/groupleaders/melbourn/yacmas/parts","/home/groupleaders/melbourn/perl/lib","/home/groupleaders/melbourn/perl/arch";

use CGI ":standard";
use DBI;

use Defs;
use PartsDB;

use PartsPerms;
use AdminPerm;
use MainPage;
use MainImage;

use PartsCommon;
use PartsContent;
use PartsDate;
use PartsWrapper;

use ContentList;
use TextLinks;

my $contentRef = \%ContentList::CONTENT_LIST;
my $featuresRef = \%DefsContent::CONTENT_FEATURES;

### Load necessary modules ###
foreach (keys %{$featuresRef}) { eval 'use '.$featuresRef->{$_}{'module'}; }
use PartsModule;

### Connect the Database
my $db = PartsDB::CONNECT_TO_DATABASE();
my $output = new CGI;

my $contentID_IN = "";

my $treeLevel = 0;    my $treeDots = PartsCommon::GET_TREE_DOTS($treeLevel);
my %document = (
	treeLevel => $treeLevel,
	title => "$Defs::SITE_NAME_SHORT",
	content => [0, "404: Page Not Found"],
	pageInfo => ['404'],
	showFull => 1
);
my $documentRef = \%document;

if ($output->cookie('TEXTONLY')) { $documentRef->{'showFull'} = 0; }

my $textLink = "";
$textLink = $output->unescape($ENV{REQUEST_URI}) or $textLink = "";
$textLink = substr($textLink, 1) if $textLink;

if (defined $TextLinks::TEXT_LINKS{$textLink}) {
	$contentID_IN = $TextLinks::TEXT_LINKS{$textLink};

	$documentRef->{'content'} = [$contentID_IN, $contentRef->{$contentID_IN}{'title'}];
	$documentRef->{'pageInfo'} = ['content'];

	PartsWrapper::GENERATE_PAGE($documentRef, $contentRef, $featuresRef, $output, $db);
}
else {
	$documentRef->{'body'}{'main'} = qq[<p>The page you're looking for doesn't appear to exist.</p>];

	my %wrapper = ();  my $wrapRef = \%wrapper;

	$wrapRef->{'content'}[0] = 0;
	$wrapRef->{'body'} = $documentRef->{'body'}{'main'};
	$wrapRef->{'icon'}[0] = "";
	$wrapRef->{'content'}[1] = "404: Page Not Found";

	$documentRef->{'body'}{'main'} = PartsWrapper::PREPARE_CONTENT($documentRef, $wrapRef);
}

MainPage::PRINT_MAIN_WRAPPER($db, $output, $documentRef);

### Disconnect the Database;
PartsDB::DISCONNECT_FROM_DATABASE($db);
