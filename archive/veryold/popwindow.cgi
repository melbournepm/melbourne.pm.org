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
use CGI ":standard";

use lib "/home/groupleaders/melbourn/yacmas",".","/home/groupleaders/melbourn/yacmas/parts","/home/groupleaders/melbourn/perl/lib","/home/groupleaders/melbourn/perl/arch";
use PartsCommon;

my $fileType = "";
my $fileName = "";
my $width = "";
my $height = "";
my $directory = "";

my $output = new CGI;


$fileType = $output->param('fileType') or $fileType = "";
$fileName = $output->param('fileName') or $fileName = "";
$width = $output->param('width') or $width = "";
$height = $output->param('height') or $height = "";
$directory = $output->param('directory') or $directory = "";

print header('text/html');

print qq[
<html>

<head>
	<link rel="stylesheet" type="text/css" href="style.cgi">
</head>

<body
	bgcolor="#ffffff"
        leftmargin="0" topmargin="0" marginwidth="0" marginheight="0"
        onLoad="window.focus();"
>\n];

if ($fileType eq "image") {
	my $imageNo = -1;

	($imageNo, $fileName) = split /---/, $fileName;
	my @images = split /,/, $fileName;

	my $title = $output->param('title');
	my $desc = $output->param('desc');

	my @title = split /-------/, $title;
	my @desc = split /-------/, $desc;

	$title = CGI::escape($title);
	$desc = CGI::escape($desc);

	print qq[
<table cellpadding="0" cellspacing="0" border="0" width="100%">
<tr>
	<td height="].($height+130).qq[" valign="top">
		<table cellpadding="0" cellspacing="0" border="0" width="100%">\n];

	print qq[		<tr valign="middle" align="center">
			<td height="].($height+10).qq["><img src="uploads/$images[$imageNo]"></td>
		</tr>\n];

	if ($title[$imageNo]) {
		print qq[		<tr valign="middle" align="center">
			<td height="20" class="popTitle">$title[$imageNo]</td>
		</tr>\n];
	}

	if ($desc[$imageNo]) {
		print qq[		<tr valign="middle" align="center">
			<form name="desc">
			<td height="100"><!NO-INDENT-START><textarea name="desc" cols="45" rows="4" wrap="soft" onFocus="blur();" class="popDesc">$desc[$imageNo]</textarea><!NO-INDENT-END></td>
			</form>
		</tr>\n];
	}

	print qq[		</table>
	</td>
<tr>
<tr valign="middle" align="center">
	<td height="30">
		<table cellpadding="0" cellspacing="0" border="0" width="95%"
		<tr>
			<td width="20%" height="30" align="left" class="text"><img src="images/shim.gif" width="1" height="1" alt=""></td>
			<td width="60%" align="center" class="text">
				<table cellpadding="3" cellspacing="0" border="0">
				<tr>
					<td>];

	if ($imageNo > 0) {
		print qq[<a href="popwindow.cgi?fileType=image&fileName=].($imageNo-1).qq[---$fileName&width=$width&height=$height&directory=$directory&title=$title&desc=$desc"><img src="images/icons/triangle_left.gif" width="11" height="12" border="0" alt="last"></a>];
	}
	else {
		print qq[<img src="images/shim.gif" width="11" height="12" alt=""></a>];
	}
		
	
	print qq[</td>
					<td align="center" class="text">];
	
	for (1 .. $#images + 1) {
		if ($_ == $imageNo + 1) { 
			print qq[<span class="popCurrent">&nbsp;$_&nbsp;</span>];
		}
		else {
			print qq[<a href="popwindow.cgi?fileType=image&fileName=].($_-1).qq[---$fileName&width=$width&height=$height&directory=$directory&title=$title&desc=$desc" class="popIndex">&nbsp;$_&nbsp;</a>];
		}
	}

	print qq[</td>
					<td>];

	if ($imageNo < $#images) {
		print qq[<a href="popwindow.cgi?fileType=image&fileName=].($imageNo+1).qq[---$fileName&width=$width&height=$height&directory=$directory&title=$title&desc=$desc"><img src="images/icons/triangle_right.gif" width="11" height="12" border="0" alt="next"></a>];
	}
	else {
		print qq[<img src="images/shim.gif" width="11" height="12" alt=""></a>];
	}
	
	print qq[</td>
				</tr>
				</table>
			</td>
			<td width="20%" align="right" class="popText">[ <a href="javascript://" onClick="window.close();" class="popText"><b>CLOSE</b></a> ]</td>
		</tr>
		</table>
</td>
</tr>
</table>
	];
}

if ($fileType eq "media") {

	if ($fileName =~ m/^.*?\.swf$/) {
		print PartsCommon::WRAP_FLASH_MEDIA("$directory/$fileName", $width, $height);
	}
	if ($fileName =~ m/^.*?\.mov$/) {
		print PartsCommon::WRAP_QUICKTIME_MEDIA("$directory/$fileName", $width, $height);
	}
}

print qq[\n</body></html>];
