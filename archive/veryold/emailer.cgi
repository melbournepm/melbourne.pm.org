#! /usr/bin/perl -w

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
use Mail::Sendmail;

my $output = new CGI;

my $length = "";
my $i = "";
my $j = "";
my @values = ();

my %redirect = ();
my %mail = ();

my $mailNum = 0;

my $tableState = "off";
my @tableFields = ();
my @tableFieldSizes = ();
my $tableFSref = \@tableFieldSizes;
my @tableFieldAlign = ();
my @tableHeadAlign = ();
my $tableColCount = 0;

my $ccToList = "";

my @params_IN = $output -> param;
my $value = "";
my $longest = 0;

if ( $ENV{HTTP_REFERER} !~ /$ENV{SERVER_NAME}/ ) { exit 0; }

for $i (0 .. $#params_IN) {
	if (length($params_IN[$i]) > $longest) { $longest = length $params_IN[$i]; }
}

my $wrapLength = 100 - $longest;
my $splitStr = "";
my $splitCount = 0;
my $printStr = "";
my $lastLine = "";
my $nextLine = "";

my $seperator = "     ";
for $j (1 .. $longest) { $seperator .= " "; }

for $i (0 .. $#params_IN) {
	$value = param("$params_IN[$i]") or $value = "";

	if ($mail{'ccToList'}[$mailNum]) {
		if ($mail{'ccToList'}[$mailNum] =~ /$params_IN[$i]/) {
			if ($value ne "") {
				if (!defined $mail{'cc'}[$mailNum]) { $mail{'cc'}[$mailNum] = "$value"; }
				else { $mail{'cc'}[$mailNum] .= ", $value"; }
			}
		}
	}

	if ($params_IN[$i] =~ /drop_/) { $params_IN[$i] = ""; }
	elsif ($params_IN[$i] =~ /mailNumber/) { $mailNum = $value or $mailNum = 0 }
	elsif ($params_IN[$i] =~ /spacer_/) { $mail{'message'}[$mailNum] .= "\n"; }
	elsif ($params_IN[$i] =~ /label_/) { $mail{'message'}[$mailNum] .= "$value\n"; }
	elsif ($params_IN[$i] =~ /mailCcToList/) { $mail{'ccToList'}[$mailNum]  = "[$value]"; }
	elsif ($params_IN[$i] eq "redirectGood") { $redirect{'good'} = $value; }
	elsif ($params_IN[$i] eq "redirectBad") { $redirect{'bad'} = $value; }
	elsif ($params_IN[$i] eq "mailToAddress") { $mail{'to_address'} = $value; }
	elsif ($params_IN[$i] eq "mailToName") { $mail{'to_name'} = $value; }
	elsif ($params_IN[$i] eq "mailFromAddress") { $mail{'from_address'} = $value; }
	elsif ($params_IN[$i] eq "mailFromName") { $mail{'from_name'} = $value; }
	elsif ($params_IN[$i] =~ /mailMessageHead/) { $mail{'message_head'}[$mailNum] = $value; }
	elsif ($params_IN[$i] =~ /mailMessageTail/) { $mail{'message_tail'}[$mailNum] = $value; }
	elsif ($params_IN[$i] =~ /mailSubject/) { $mail{'subject'}[$mailNum] = $value; }
	elsif ($params_IN[$i] =~ /mailEncrypt/) { $mail{'encrypt'}[$mailNum] = $value; }
	elsif ($params_IN[$i] =~ /table_on/) { $tableState = "on"; }
	elsif ($params_IN[$i] =~ /table_field_size/) {
		@tableFieldSizes = split /---/, $value;
	}
	elsif ($params_IN[$i] =~ /table_head_align/) {
		@tableHeadAlign = split /---/, $value;
	}
	elsif ($params_IN[$i] =~ /table_field_align/) {
		@tableFieldAlign = split /---/, $value;
	}
	elsif ($params_IN[$i] =~ /table_separator/) {
		$mail{'message'}[$mailNum] .= tableDivider($tableFSref);
	}
	elsif ($params_IN[$i] =~ /table_fields_/) {
		@tableFields = split /---/, $value;
		
		for my $i (0 .. $#tableFieldSizes) {
			$mail{'message'}[$mailNum] .= tableCell($tableFields[$i], $tableFieldSizes[$i], $tableHeadAlign[$i]);
		}
		$mail{'message'}[$mailNum] .= "|\n";
	}
	elsif ($params_IN[$i] =~ /table_off/)    {
		$tableState = "off";
		@tableFields = ();
		@tableFieldSizes = ();
		$tableColCount = 0;
	}
	elsif ($tableState eq "on") {
		$mail{'message'}[$mailNum] .= tableCell($value, $tableFieldSizes[$tableColCount], $tableFieldAlign[$tableColCount]);

		$tableColCount ++;
		if ($tableColCount > $#tableFieldSizes) {
			$tableColCount = 0;
			$mail{'message'}[$mailNum] .= "|\n";
		}
	}
	else {
		$length = length $params_IN[$i];
		if ($length == $longest) { $params_IN[$i] = " $params_IN[$i]"; }
		else {
			for $j ($length .. $longest) { $params_IN[$i] = " $params_IN[$i]"; }
		}
		$params_IN[$i] = " $params_IN[$i]";

		if (length $value > $wrapLength or $value =~ /\n/) {

			$printStr = "";
			$splitCount = 0;
			
			while ($value) {
				($splitStr, $value) = split / /, $value, 2;

				if ($splitCount == 0) {
					$printStr = "$params_IN[$i] :- ";
					$splitCount ++;
				}

				if ($splitStr =~ /\n/) {
					($lastLine, $nextLine) = split /\n/, $splitStr, 2;

					$mail{'message'}[$mailNum] .= $printStr.qq[$lastLine];

					while ($nextLine =~ s/\n//) {
						$mail{'message'}[$mailNum] .= qq[\n];
					}

					if ($nextLine ne "") {
						$printStr = "\n$seperator $nextLine ";
					}
					else {
						$printStr = "";
					}
				}	
				elsif (length($splitStr) + length($printStr) >= $wrapLength) {
					$mail{'message'}[$mailNum] .= qq[$printStr\n];
					$printStr = "$seperator $splitStr ";
				}
				else {
					$printStr .= "$splitStr ";
				}
			}

			$mail{'message'}[$mailNum] .= qq[$printStr\n];

		}
		else {
			$mail{'message'}[$mailNum] .= qq[$params_IN[$i] :- $value\n];
		}
	}
}

my $mailTo = "$mail{'to_name'} <$mail{'to_address'}>";
my $mailFrom = "$mail{'from_name'} <$mail{'from_address'}>";

for my $i (0 .. $#{$mail{'message'}}) {
###	warn "$i: $mail{'message'}[$i]";

	$mail{'message'}[$i] = $mail{'message_head'}[$i]."\n\n".$mail{'message'}[$i]."\n\n".$mail{'message_tail'}[$i];

	$mail{'message'}[$i] =~ s/\\n/\n/g;
	$mail{'message'}[$i] =~ s/\\t/\t/g;

	my %sendmail = ();

	if ($mail{'encrypt'}[$i] eq "yes") {
		my $processID = "$$-$i";

		open (MAILBODY, ">tmp/$processID") or die "Unable to open 'tmp/$processID' for writing";
			print MAILBODY $mail{'message'}[$i];
		close MAILBODY;

		chmod 0600, "tmp/$processID";

		system("gpg --homedir /home/rodd/.gnupg/ -ea -r $mail{'to_address'} -o tmp/$processID.pgp --always-trust --yes < tmp/$processID") == 0 or die "system failed: $?";
	
		$mail{'message'}[$i] = "";
	
		open (MAILBODY, "tmp/$processID.pgp") or die "Unable to open 'tmp/$processID.pgp' for reading";
			while (<MAILBODY>) { $mail{'message'}[$i] .= $_; }
		close MAILBODY;

		chmod 0600, "tmp/$processID.pgp";

		unlink "tmp/$processID";
		unlink "tmp/$processID.pgp";

		$sendmail{'Content-Type'} = 'multipart/encrypted; boundary=foo; protocol="application/pgp-encrypted"';
		$mail{'message'}[$i] = qq[--foo
Content-Type: application/pgp-encrypted

Version: 1

--foo
Content-Type: application/octet-stream

$mail{'message'}[$i]
--foo--];
		
	}

	$sendmail{'To'} = $mailTo;
	$sendmail{'From'} = $mailFrom;
	if ($mail{'cc'}[$i]) { $sendmail{'Cc'} = $mail{'cc'}[$i]; }
	$sendmail{'Subject'} = $mail{'subject'}[$i];
	$sendmail{'Message'} = $mail{'message'}[$i];
	$sendmail{'smtp'} = 'localhost';

	if (!sendmail(%sendmail)) { print $output -> redirect( -uri=>"$redirect{'bad'}", -nph=>0 ); }
}

print $output -> redirect( -uri=>"$redirect{'good'}", -nph=>0 );

##############################################################################################

sub tableDivider {
	my ($tableFSref) = @_;
	my $returnBody = "";

	foreach my $i (@{$tableFSref}) {
		$returnBody .= "+-";
		for (1 .. $i) { $returnBody .= "-"; }
		$returnBody .= "-";
	}

	$returnBody .= "+\n";
	
	return $returnBody;
}

sub tableCell {
	my ($fieldValue, $fieldSize, $align) = @_;
	my $returnBody = "";
	my $spaceLeft = "";
	my $spaceRight = "";
	my $count = 0;

	$length = length $fieldValue;
	for ($length + 1 .. $fieldSize) {
		if ($align eq "c") {
			if ($count%2 == 0) { $spaceLeft .= " "; }
			else { $spaceRight .= " "; }
		}
		elsif ($align eq "r") { $spaceLeft .= " "; }
		else { $spaceRight .= " "; }
		
		$count ++;
	}
	$returnBody .= "| ".$spaceLeft.$fieldValue.$spaceRight." ";

	return $returnBody;
}
