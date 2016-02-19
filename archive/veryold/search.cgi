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
use POSIX qw(strftime);

use Defs;
use PartsDB;

use MainPage;
use MainCheck;
use MainImage;

use PartsPerms;
use PartsCommon;
use PartsContent;
use PartsSearch;
use PartsDate;
use PartsWrapper;

### Connect the Database
my $db = CONNECT_TO_DATABASE();
my $output = new CGI;

my $advSearch_IN = "";  $advSearch_IN = $output->param('advSearch') or $advSearch_IN = "no";
my $advText_IN = "";  $advText_IN = $output->param('text') or $advText_IN = "";
my $advTitle_IN = "";  $advTitle_IN = $output->param('title') or $advTitle_IN = "";
my $advContent_IN = "";  $advContent_IN = $output->param('content') or $advContent_IN = "";
my $advPostedBy_IN = "";  $advPostedBy_IN = $output->param('postedby') or $advPostedBy_IN = "";
my $advAftDay_IN = "";  $advAftDay_IN = $output->param('afterDay') or $advAftDay_IN = "";
my $advAftMonth_IN = "";  $advAftMonth_IN = $output->param('afterMonth') or $advAftMonth_IN = "";
my $advAftYear_IN = "";  $advAftYear_IN = $output->param('afterYear') or $advAftYear_IN = "";
my $advBefDay_IN = "";  $advBefDay_IN = $output->param('beforeDay') or $advBefDay_IN = "";
my $advBefMonth_IN = "";  $advBefMonth_IN = $output->param('beforeMonth') or $advBefMonth_IN = "";
my $advBefYear_IN = "";  $advBefYear_IN = $output->param('beforeYear') or $advBefYear_IN = "";

my $si_IN = "";  $si_IN = $output->param('si') or $si_IN = "";
my $te_IN = "";  $te_IN = $output->param('te') or $te_IN = "";
my $contentID_IN = 0;  $contentID_IN = $output->param('contentID') or $contentID_IN = 0;

my %document = (
	treeLevel => 0,
	title => "$Defs::SITE_NAME_SHORT - Search Results",
	content => [0, "Search"],
	pageInfo => ['search'],
	display => "full",
	showFull => 1
);
my $documentRef = \%document;

if ($output->cookie('TEXTONLY')) { $documentRef->{'showFull'} = 0; }

my $treeDots = PartsCommon::GET_TREE_DOTS($documentRef->{'treeLevel'});

$documentRef->{'body'}{'main'} = qq[<img src="$treeDots].qq[images/shim.gif" width="1" height="10" alt=""><br>];

my $dateAft = "";
my $dateBef = "";

my $conductSearch = 1;

if ($si_IN eq "" and $advSearch_IN eq "") { $conductSearch = 0; }
#if ($advSearch_IN ne "" and $advText_IN eq "" and $advTitle_IN eq "" and $advContent_IN eq "" and $advPostedBy_IN eq "" and $advAftDay_IN eq "" and $advAftMonth_IN eq "" and $advAftYear_IN eq "" and $advBefDay_IN eq "" and $advBefMonth_IN eq "" and $advBefYear_IN eq "") { $conductSearch = 0; }

if ($advSearch_IN eq "form") { $conductSearch = 0; }
elsif ($advSearch_IN eq "yes") {
	my %errors = ();	my $errorsRef = \%errors;
	
	VALIDATE_FIELD($errorsRef, "title", "$advText_IN", "Title");
	VALIDATE_FIELD($errorsRef, "title", "$advTitle_IN", "Text");
	VALIDATE_FIELD($errorsRef, "number", "$advAftDay_IN", "Posted After Day");
	VALIDATE_FIELD($errorsRef, "number", "$advAftMonth_IN", "Posted After Month");
	VALIDATE_FIELD($errorsRef, "number", "$advAftYear_IN", "Posted After Year");
	VALIDATE_FIELD($errorsRef, "number", "$advBefDay_IN", "Posted Before Day");
	VALIDATE_FIELD($errorsRef, "number", "$advBefMonth_IN", "Posted Before Month");
	VALIDATE_FIELD($errorsRef, "number", "$advBefYear_IN", "Posted Before Year");

	if (length $advAftYear_IN == 1 or length $advAftYear_IN == 3) { 
		$errorsRef->{'other'} .= "<li><p>The <b>Posted After Year</b> needs to be a four digit year (eg 2001)</p></li>";
	}
	if (length $advBefYear_IN == 1 or length $advBefYear_IN == 3) {
		$errorsRef->{'other'} .= "<li><p>The <b>Posted Before Year</b> needs to be a four digit year (eg 2001)</p></li>";
	}

	if ($errorsRef->{'invalid'} or $errorsRef->{'other'}) {
		$documentRef->{'body'}{'main'} = MainCheck::PRINT_ERROR_CONTENT("inputError", $errorsRef);
		$documentRef->{'title'} = "We've got a problem!";
		PRINT_MAIN_WRAPPER($db, $output, $documentRef);
		DISCONNECT_FROM_DATABASE($db);
		exit 0;
	}
	
	my $currentYear = substr ((localtime)[5], -2, 2);
	
	if (length $advAftYear_IN == 2) {
		if ($advAftYear_IN > $currentYear) { $advAftYear_IN = "19".$advAftYear_IN; }
		else                               { $advAftYear_IN = "20".$advAftYear_IN; }
	}
	if (length $advAftMonth_IN == 1) { $advAftMonth_IN = "0".$advAftMonth_IN; }
	if (length $advAftDay_IN == 1) { $advAftDay_IN = "0".$advAftDay_IN; }
	if (length $advBefYear_IN == 2) {
		if ($advBefYear_IN > $currentYear) { $advBefYear_IN = "19".$advBefYear_IN; }
		else                               { $advBefYear_IN = "20".$advBefYear_IN; }
	}
	if (length $advBefMonth_IN == 1) { $advBefMonth_IN = "0".$advBefMonth_IN; }
	if (length $advBefDay_IN == 1) { $advBefDay_IN = "0".$advBefDay_IN; }
	
	if ($advAftYear_IN ne "") {
		$dateAft = $advAftYear_IN;
		if ($advAftMonth_IN ne "" and $advAftMonth_IN <= 12) {
			$dateAft = $dateAft."-$advAftMonth_IN";
			if ($advAftDay_IN ne "") { $dateAft = $dateAft."-$advAftDay_IN 00:00:00"; }
			else                     { $dateAft = $dateAft."-01 00:00:00"; }
		}
		else {
			$dateAft = $dateAft."-01-01 00:00:00";
		}
	}

	if ($advBefYear_IN ne "") {
		$dateBef = $advBefYear_IN;
		if ($advBefMonth_IN ne "" and $advBefMonth_IN <= 12) {
			$dateBef = $dateBef."-$advBefMonth_IN";
			if ($advBefDay_IN ne "") { $dateBef = $dateBef."-$advBefDay_IN 23:59:59"; }
			else                     { $dateBef = $dateBef."-31 23:59:59"; }
		}
		else {
			$dateBef = $dateBef."-12-31 23:59:59";
		}
	}
}

if (!defined $te_IN) { $te_IN = ""; }
if (!defined $si_IN) { $si_IN = ""; }

my $showDate = "yes";
my $colspanFull = "3";
my $colspan = "2";

if ($showDate ne "yes") {
	$colspanFull = "2";
	$colspan = "1";
}

my $extraWhere = "";
my $contentResults = "";
my $count = 0;

if ($conductSearch) {

	###
	# Content Related Searches
	###

	if ($advTitle_IN ne "") {
		$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "AND", "strTitle REGEXP '$advTitle_IN'");
	}

	if ($advContent_IN ne "") {
		$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "AND", "intContentID = '$advContent_IN'");
	}

	if ($advText_IN ne "") {
		$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "AND", "strValue REGEXP '$advText_IN'");
	}

	if ($dateAft ne "") {
		$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "dtPosted >= '$dateAft'");
	}

	if ($dateBef ne "") {
		$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "AND", "dtPosted <= '$dateBef'");
	}

	if ($te_IN =~ m/^[0-9|]+$/) {
		$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "AND", "intContentID REGEXP '^($te_IN)\$'");
	}

	if ($si_IN ne "") {
		$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "AND", "(strTitle REGEXP '$si_IN' OR strValue REGEXP '$si_IN');
	}

	my $statement = "";
	my $query = "";

	my $cookie = "";	if ($output->cookie('SITE_ALLOWS')) { $cookie = '|'.$output->cookie('SITE_ALLOWS').'|'; }

	if ($cookie) {
		if ($cookie !~ /SU/) {
			my $cookieExp = '\\\\|('.$output->cookie('SITE_ALLOWS').')\\\\|';
			$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "AND", "(strGroups REGEXP '$cookieExp' OR strGroups = '')");
		}
	}
	else {
		$extraWhere .=  PartsDB::CREATE_WHERE_STATEMENT($extraWhere, "AND", "(strGroups = '')");
	}

	my $statusWhere = "";
	foreach my $i (2, 1) {
		foreach (keys %Defs::STATUS_OPTIONS) {
			if ($Defs::STATUS_OPTIONS{$_}{'content'}{'show'} == $i) {
				if ($statusWhere) {	$statusWhere .= qq[ OR ]; }
				else { $statusWhere .= qq[AND (]; }

				$statusWhere .= qq[chrStatus = '$_'];
			}
		}
	}
	if ($statusWhere) {	$statusWhere .= ")\n"; }

	$statement = "
		SELECT intContentID, strTitle, DATE_FORMAT(dtPosted, '%a %D %b, %Y')
		FROM tblContents
			LEFT JOIN tblModules ON tblContents.intContentID = tblModules.intContentID
		$extraWhere
		$statusWhere
		ORDER BY dtPosted DESC
	";

	$query = PartsDB::RUN_QUERY($db, $statement);

	my %usedContent = ();

	while ( my ($id, $title, $posted) = $query -> fetchrow_array()) {
		if (!defined $usedContent{$id} or $usedContent{$id} eq "") {
			$contentResults .= PartsSearch::WRITE_SEARCH_TABLE_ROW('content', $id, $title, $posted, $documentRef);
			$usedContent{$id} = "yes";
			$count ++
		}
	}

	$query -> finish;
}

$documentRef->{'body'}{'main'} .= PartsSearch::WRAP_SEARCH_LISTINGS($contentResults, $count, $colspan, $showDate, $documentRef);

my %wrapper = ();  my $wrapRef = \%wrapper;

$wrapRef->{'content'}[0] = 0;
$wrapRef->{'body'} = $documentRef->{'body'}{'main'};
$wrapRef->{'icon'}[0] = "";

if (!$conductSearch) {
	$wrapRef->{'content'}[1] = "Search Results";
	$documentRef->{'title'} = qq[$Defs::SITE_NAME_SHORT - Search Results];
}
elsif ($advSearch_IN ne "no") {
	$wrapRef->{'content'}[1] = "Advanced Search Results";
	$documentRef->{'title'} = qq[$Defs::SITE_NAME_SHORT - Advanced Search Results];
}
elsif ($te_IN ne "") {
	$wrapRef->{'content'}[1] = "Search for '$si_IN'";
	$documentRef->{'title'} = qq[$Defs::SITE_NAME_SHORT - Search for "$si_IN"];
}
elsif ($si_IN ne "") {
	$wrapRef->{'content'}[1] = "Search Results for '$si_IN'";
	$documentRef->{'title'} = qq[$Defs::SITE_NAME_SHORT - Search for "$si_IN"];
}
else {
	$wrapRef->{'content'}[1] = "Search Results";
	$documentRef->{'title'} = qq[$Defs::SITE_NAME_SHORT - Search Results];
}

$documentRef->{'body'}{'main'} = PartsWrapper::PREPARE_CONTENT($documentRef, $wrapRef);

my $searchAgain = "Search Again?";

if (!$conductSearch) {
	$searchAgain = "Advanced Search";

	$documentRef->{'body'}{'main'} = "";
	$documentRef->{'body'}{'sub'} = qq[<img src="$treeDots].qq[images/shim.gif" width="1" height="10" alt=""><br>];
	$documentRef->{'title'} = qq[$Defs::SITE_NAME_SHORT - $searchAgain];
}

if ($advSearch_IN) {
	my %wrapper = ();  my $wrapRef = \%wrapper;

	$wrapRef->{'content'}[0] = 0;
	$wrapRef->{'content'}[1] = $searchAgain;
	$wrapRef->{'body'} = PartsSearch::PRINT_SEARCH_FORM($db, $documentRef);
	$wrapRef->{'icon'}[0] = "";

	$documentRef->{'body'}{'main'} .= PartsWrapper::PREPARE_CONTENT($documentRef, $wrapRef);
}

PRINT_MAIN_WRAPPER($db, $output, $documentRef);

### Disconnect the Database;
DISCONNECT_FROM_DATABASE($db);


###
# SUB ROUTINES
###

sub whereOrAnd {
	my ($current, $type, $new) = @_;

	if ($current) {
		if ($type eq "AND") { return qq[		AND $new\n]; }
		else { return qq[		OR $new\n]; }
	}
	else { return qq[WHERE $new\n]; }
}



