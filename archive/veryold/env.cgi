#!/usr/bin/perl

# Check that this is allowed.

print "Content-type: text/plain\n\n";

foreach $key (sort {$a cmp $b} keys %ENV) {
	print "$key - $ENV{$key}\n";
}

if ($ENV{'REQUEST_METHOD'} eq "POST") {
	read(STDIN, $GN_QUERY, $ENV{'CONTENT_LENGTH'});
	print "\nPost Data\n";
	$GN_QUERY =~ s/\&/\n/g;
	print $GN_QUERY;
}

