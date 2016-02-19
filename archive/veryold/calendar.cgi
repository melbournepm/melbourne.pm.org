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
use AdminPerm;
use PartsContent;
use MainPage;

use PartsCommon;
use PartsDate;

### Connect the Database
my $db = CONNECT_TO_DATABASE();
my $output = new CGI;

my $month_IN = ""; if (!defined $output->param('month')) { $month_IN = ""; } else { $month_IN = $output->param('month')};
my $year_IN = ""; if (!defined $output->param('year')) { $year_IN = ""; } else { $year_IN = $output->param('year')};

if (!$month_IN and !$year_IN) {
	if (!defined $output->cookie('GCAL_MONTH')) { $month_IN = (localtime())[4]; }
	else { $month_IN = $output->cookie('GCAL_MONTH')};
	if (!defined $output->cookie('GCAL_YEAR')) { $year_IN = (localtime())[5]; }
	else { $year_IN = $output->cookie('GCAL_YEAR')};
}

my $treeLevel = 0;
my $treeDots = PartsCommon::GET_TREE_DOTS($treeLevel);

my %document = (
	treeLevel => $treeLevel,
	content => [0, "$Defs::SITE_NAME_SHORT - Calendar"],
	title => "$Defs::SITE_NAME_SHORT - Calendar",
	pageInfo => ['calendar'],
	showFull => 1
);
my $documentRef = \%document;

if ($output->cookie('TEXTONLY')) { $documentRef->{'showFull'} = 0; }

my $i = 0;
my $j = 0;
my $k = 0;

my $firstDay = (localtime(timelocal(1,1,1,1,$month_IN,$year_IN)))[6];

my $dateFromPre = (1900 + $year_IN)."-".(sprintf "%02d", $month_IN)."-";
my $dateToPre = (1900 + $year_IN)."-".(sprintf "%02d", $month_IN)."-";

my $dateFrom = "";
my $dateTo = "";
my $dateOffset = "";

my $daysInMonth = 0;
my $daysInLastMonth = 0;
my $daysInNextMonth = 0;
my $nextMonth = $month_IN + 1;
my $nextYear = $year_IN;
my $lastMonth = $month_IN - 1;
my $lastYear = $year_IN;

if ($month_IN == 11) {
	$daysInMonth = 31;
	$daysInNextMonth = 31;
	$daysInLastMonth = 30;
	$nextMonth = 0;
	$nextYear = $year_IN + 1;
}
else {
	$daysInMonth = (localtime(timelocal(1,1,1,1,$month_IN + 1,$year_IN)))[7] - (localtime(timelocal(1,1,1,1,$month_IN,$year_IN)))[7];
	if ($month_IN != 0) {
		$daysInLastMonth = (localtime(timelocal(1,1,1,1,$month_IN,$year_IN)))[7] - (localtime(timelocal(1,1,1,1,$month_IN - 1,$year_IN)))[7];
	}

	if ($month_IN != 10) {
		$daysInNextMonth = (localtime(timelocal(1,1,1,1,$month_IN + 2,$year_IN)))[7] - (localtime(timelocal(1,1,1,1,$month_IN + 1,$year_IN)))[7];
	}
	else { $daysInNextMonth = 31; }
}

if ($month_IN == 0) {
	$lastMonth = 11;
	$lastYear = $year_IN - 1;
	$daysInMonth = 31;
	$daysInLastMonth = 31;
}

my $dateToMatch = ($year_IN + 1900)."-".(sprintf "%02d", $month_IN + 1)."-";

my $extraWhere = "";
my $cookie = "";	if ($output->cookie('SITE_ALLOWS')) { $cookie = '\\\\|('.$output->cookie('SITE_ALLOWS').')\\\\|'; }

if ($cookie) {
	if ($cookie !~ /SU/) {
		$extraWhere = qq[
		AND ('$cookie' REGEXP tblContents.strGroups OR tblContents.strGroups = '')];
	}
}
else {
	$extraWhere = qq[
		AND tblContents.strGroups = ''];
}

use POSIX qw(strftime);
my $currentDate = strftime "%G-%m-%d %H:%M:%S", localtime;

my $statement = "
	SELECT tblContents.intContentID, tblContents.strTitle, tblModules.strValue
	FROM tblContents
		LEFT JOIN tblModules ON tblContents.intContentID = tblModules.intContentID
	WHERE tblModules.strModule = 'event'
		AND dtActivate <= 'date()'
		AND (dtDeactivate <= 'date()')
		$extraWhere
";

my $query = PartsDB::RUN_QUERY($db, $statement);

my @dayEvents = ();
my @spanEvents = ();
my %eventYears = ();

my $count = 0;

while ( my ($id, $title, $value1, $value2) = $query -> fetchrow_array()) {

	$value1 =~ s/^(.{0,4}?-.{0,2}?-.{0,2}?)-.*$/$1/;
	$value2 =~ s/^(.{0,4}?-.{0,2}?-.{0,2}?)-.*$/$1/;

	my $eventYear = $value1;
	if ($eventYear =~ m/^([0-9]{4}).*$/) { $eventYears{$1} = 1; }

	$eventYear = $value2;
	if ($eventYear =~ m/^([0-9]{4}).*$/) { $eventYears{$1} = 1; }

	my $fileName = PartsCommon::GENERATE_LINK($id, "content");

	if ($value2 =~ /^--/) {
		if ($value1 =~ m/^$dateToMatch/) {
			push @dayEvents, [$fileName, $title, $value1];
		}
	}
	else {
		if ($value1 le $dateToMatch."31" and $value2 ge $dateToMatch) {
			push @spanEvents, [$fileName, $title, $value1, $value2, $Defs::CAL_COLORS[$count % 6]];
			$count ++;
		}
	}
}

my $dayWidth = 100;
my $tableWidth = $dayWidth * 7 + 8;

my $borderColor = "#00401b";

my $tableSpacer = qq[<td class="calSpacer"><img src="$treeDots].qq[images/shim.gif" width="1" height="1"></td>];

$documentRef->{'body'}{'main'} .= qq[<script language="JavaScript">
<!--
	function setCookie(name, value, expires, path, domain, secure) {
		var curCookie = name + "=" + escape(value) +
			((expires) ? "; expires=" + expires.toGMTString() : "") +
			((path) ? "; path=" + path : "") +
			((domain) ? "; domain=" + domain : "") +
			((secure) ? "; secure" : "");
		document.cookie = curCookie;
	}
//-->
</script>

<center>

<table cellpadding="0" cellspacing="0" border="0" width="$tableWidth">
<tr>
	<td colspan="15"><img src="$treeDots].qq[images/shim.gif" width="1" height="3"></td>
</tr>
<tr>
	<td colspan="15" class="calSpacer"><img src="$treeDots].qq[images/shim.gif" width="1" height="1"></td>
</tr>
<tr>
	<td class="calSpacer"><img src="$treeDots].qq[images/shim.gif" width="1" height="30"></td>
	<td colspan="13" class="calHeader">
		<table cellpadding="0" cellspacing="0" border="0" width="100%">
		<tr valign="middle" background="$treeDots].qq[images/shim.gif">
			<td><img src="$treeDots].qq[images/shim.gif" width="10" height="35" alt=""></td>
			<td class="calArrows" align="left"><a href="$treeDots].qq[calendar.cgi?month=$lastMonth&year=$lastYear" onClick="setCookie('GCAL_MONTH', '$lastMonth', '', '', '', ''); setCookie('GCAL_YEAR', '$lastYear', '', '', '', '');" class="calArrows">&lt;&lt;</a></td>
			<td align="center">
				<table cellpadding="0" cellspacing="0" border="0">
				<tr>
					<td class="calTitle">].lc ("$Defs::SITE_NAME_SHORT Calendar").qq[ - ].lc($Defs::MONTHS[$month_IN]).qq[ ].($year_IN + 1900).qq[</td>
				</tr>
				</table>
			</td>
			<td class="calArrows" align="right"><a href="$treeDots].qq[calendar.cgi?month=$nextMonth&year=$nextYear" onClick="setCookie('GCAL_MONTH', '$nextMonth', '', '', '', ''); setCookie('GCAL_YEAR', '$nextYear', '', '', '', '');" class="calArrows">&gt;&gt;</a></td>
			<td><img src="$treeDots].qq[images/shim.gif" width="10" height="35" alt=""></td>
		</tr>
		</table>
	</td>
	<td class="calSpacer"><img src="$treeDots].qq[images/shim.gif" width="1" height="1"></td>
</tr>
<tr>
	<td colspan="15" class="calSpacer"><img src="$treeDots].qq[images/shim.gif" width="1" height="1"></td>
</tr>
<tr align="center">
	$tableSpacer
	<td class="calWeekday">Sunday<br><img src="$treeDots].qq[images/shim.gif" width="$dayWidth" height="1"></td>
	$tableSpacer
	<td class="calWeekday">Monday<br><img src="$treeDots].qq[images/shim.gif" width="$dayWidth" height="1"></td>
	$tableSpacer
	<td class="calWeekday">Tuesday<br><img src="$treeDots].qq[images/shim.gif" width="$dayWidth" height="1"></td>
	$tableSpacer
	<td class="calWeekday">Wednesday<br><img src="$treeDots].qq[images/shim.gif" width="$dayWidth" height="1"></td>
	$tableSpacer
	<td class="calWeekday">Thursday<br><img src="$treeDots].qq[images/shim.gif" width="$dayWidth" height="1"></td>
	$tableSpacer
	<td class="calWeekday">Friday<br><img src="$treeDots].qq[images/shim.gif" width="$dayWidth" height="1"></td>
	$tableSpacer
	<td class="calWeekday">Saturday<br><img src="$treeDots].qq[images/shim.gif" width="$dayWidth" height="1"></td>
	$tableSpacer
</tr>\n];

my $matchToday = "no";
my $dayOffset = "";
my $spanCount = "0";
my $alreadySpanned = "0";
my $weekHeight = 0;

for $i (0 .. 41) {
	
	if (!($i%7)) {
		if ($i - ($firstDay - 1) > $daysInMonth) { last; }
		$documentRef->{'body'}{'main'} .= qq[<tr>
	<td colspan="15" class="calSpacer"><img src="$treeDots].qq[images/shim.gif" width="1" height="1"></td>
</tr>
<tr align="middle">
	$tableSpacer\n];

		$dayOffset = $firstDay - 1;

		$dateFrom = $i - $dayOffset;
		$dateTo = $dateFrom + 6;

		for $j ($i .. $i + 6) {
			if ($j - ($firstDay - 1) < 1 or $j - ($firstDay - 1) > $daysInMonth ) {
				if ($i < 15) {
					$documentRef->{'body'}{'main'} .= qq[	<td class="calDayEmpty">].($j - ($firstDay - 1) + $daysInLastMonth).qq[</td>\n	$tableSpacer\n];
				}
				else {
					$documentRef->{'body'}{'main'} .= qq[	<td class="calDayEmpty">].($j - ($firstDay - 1) - $daysInMonth).qq[</td>\n	$tableSpacer\n];
				}
			}
			else {
				$documentRef->{'body'}{'main'} .= qq[	<td class="calDay">].($j - ($firstDay - 1)).qq[</td>\n	$tableSpacer\n];
			}
		}

		$documentRef->{'body'}{'main'} .= qq[<tr>
	<td colspan="15" class="calSpacer"><img src="$treeDots].qq[images/shim.gif" width="1" height="1"></td>
</tr>
</tr>\n];

		$weekHeight = "80";

		for $j (0 .. $#spanEvents) {
		
			$spanCount = 0;
			$alreadySpanned = 0;
		
			for $k ($i .. $i + 6) {
				if ($spanEvents[$j][2] le "$dateToMatch".(sprintf "%02d", $k - $dayOffset) and $spanEvents[$j][3] ge "$dateToMatch".(sprintf "%02d", $k - $dayOffset)) {

					if ($spanCount == 0) {
						$documentRef->{'body'}{'main'} .= qq[<tr>
	$tableSpacer\n];

						if ($k - $i != 0) {
							for (1 .. $k - $i) {
								$documentRef->{'body'}{'main'} .= qq[	<td class="calEmpty">&nbsp;</td>
	$tableSpacer\n];
							}
							
							$alreadySpanned = $k - $i;
						}
					}

					
					$spanCount ++;				
				}
				
			}

			if ($spanCount > 0) {
				$documentRef->{'body'}{'main'} .= qq[	<td colspan="].(($spanCount * 2) - 1).qq[" height="15" bgcolor="$spanEvents[$j][4]" align="center"><a href="$treeDots].qq[$spanEvents[$j][0]" target="$Defs::site_name" class="calText">$spanEvents[$j][1]</a></td>
	$tableSpacer\n];

				$weekHeight = $weekHeight - 15;

				if ($spanCount + $alreadySpanned < 7) {
					for (1 .. 7 - ($spanCount + $alreadySpanned)) { 
						$documentRef->{'body'}{'main'} .= qq[ 	<td class="calEmpty">&nbsp;</td>
	$tableSpacer\n];
					}
				}

				$documentRef->{'body'}{'main'} .= qq[</tr>\n];
			}
		}

		$documentRef->{'body'}{'main'} .= qq[<tr valign="top">
	$tableSpacer\n];

		for $j ($i .. $i + 6) {
		
			if ($weekHeight < 15) { $weekHeight = 15; }

			$documentRef->{'body'}{'main'} .= qq[	<td height="$weekHeight" align="center" class="calEmpty">];

			$matchToday = "no";
		
			for $k (0 .. $#dayEvents) {
				if ("$dateToMatch".(sprintf "%02d", $j - $dayOffset) eq $dayEvents[$k][2]) {
					if ($matchToday eq "yes") { $documentRef->{'body'}{'main'} .= "<br>"; }
					$documentRef->{'body'}{'main'} .= qq[<a href="$treeDots].qq[$dayEvents[$k][0]" target="$Defs::site_name" class="calText">$dayEvents[$k][1]</a>];
					$matchToday = "yes";
				}
			}
			
			if ($matchToday eq "no") { $documentRef->{'body'}{'main'} .= " &nbsp;"; }
			
			$documentRef->{'body'}{'main'} .= qq[</td>
	$tableSpacer\n];
		}
		
		$documentRef->{'body'}{'main'} .= qq[</tr>\n];
	}

}

$documentRef->{'body'}{'main'} .= qq[<tr>
	<td colspan="15" class="calSpacer"><img src="$treeDots].qq[images/shim.gif" width="1" height="1"></td>
</tr>
</table>\n];

$documentRef->{'body'}{'main'} .= qq[<table cellpadding="3" cellspacing="0" border="0" width="$tableWidth">
<tr>
	<td class="calBold"> | ];

for (0 .. $#Defs::MONTHS) {
	$documentRef->{'body'}{'main'} .= qq[<a href="$treeDots].qq[calendar.cgi?month=$_&year=$year_IN" onClick="setCookie('GCAL_MONTH', '$_', '', '', '', '');" class="calBold">$Defs::MONTHS[$_]</a> | ];
}

$documentRef->{'body'}{'main'} .= qq[</td>
	<td class="calBold" align="right"> | ];

foreach $i (sort keys %eventYears) {
	$documentRef->{'body'}{'main'} .= qq[<a href="$treeDots].qq[calendar.cgi?year=].($i - 1900).qq[&month=$month_IN" onClick="setCookie('GCAL_YEAR', '].($i - 1900).qq[', '', '', '', '');" class="calBold">$i</a> | ];
}

$documentRef->{'body'}{'main'} .= qq[</td>
</tr>
</table>

</center>];

my $bodyTitle = qq[<img src="$treeDots].qq[images/arrows_body_title.gif" width="27" height="9"><span class="bodyTitle">CALENDAR</span>];

PRINT_MAIN_WRAPPER($db, $output, $documentRef);

### Disconnect the Database;
DISCONNECT_FROM_DATABASE($db);
