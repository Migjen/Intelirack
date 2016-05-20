#!/usr/bin/perl

# the size of the short term memory:

my $MEMORY_LENGTH = 10;

# The memory buffer:

my @MEMORY = ();

# Max

my $MAX;

# Average:

my $AVG;

# Sum:

my $SUM;

# The index for the buffer-rotation:

my $index = -1;

# The currently read data item

my $data;

# The result of the CHI squared computation:

my $chi = 0;

# counter

my $counter = 0;

########################
# Application specific variables. Not part of the algorithm

use strict "vars";
use Getopt::Std;

my $opt_string = 'vm:c:qaDl:e:';
getopts( "$opt_string", \my %opt ) or usage() and exit;


my $QUIET;
my $QUIET_CHECK;
my $DRAMATIC = 0;
$DRAMATIC = 1 if $opt{D};

$QUIET = 1 if $opt{q};

my $VERBOSE;
$VERBOSE = 1 if $opt{v};

my $CHI_LIMIT;
$CHI_LIMIT = $opt{c} if $opt{c};

my $ALL_EVENTS;
$ALL_EVENTS = 1 if $opt{a};

$MEMORY_LENGTH = $opt{m} if $opt{m};

my $EXP_START = $opt{e};

my $EXP_LENGTH = $opt{l};

#######################


while( $data = <STDIN> ) {

    # removing newline:
    chomp $data;
    $data = ( $data * -1) if $data < 0;
    $index++;
    $counter++;
    
#    $MAX = $data if $data > $MAX;

    verbose("\n--- read data: $data\n");

    if ( $#MEMORY + 1 < $MEMORY_LENGTH ){
	# we have not filled up the entire memory yet:
	$SUM += $data;
	$AVG += $data/( $MEMORY_LENGTH + 1 );
	verbose("inserting $data at position " . ($#MEMORY + 1) ." (sum: $SUM) [avg: $AVG]\n");
	$MEMORY[$index] = $data;

    } else {
	# we have filled up the memory, and can now start the detection

	# lets find the adaptive treshold
	$MAX = find_max();

	my $MAXAVG = $AVG + $MAX/( $MEMORY_LENGTH + 1 );

	# we compute the chi squared:
	my $Tchi = 
	    sqrt(
		($SUM - $MEMORY_LENGTH * $MAX)**2 
		/ 
		($MEMORY_LENGTH * ($MEMORY_LENGTH + 1) * $MAXAVG )
	    );
	
	verbose("Adjusting new chi treshold to $Tchi with max: $MAX\n");
	$CHI_LIMIT = $Tchi;


	
	$AVG += $data/( $MEMORY_LENGTH + 1 );

	# we compute the chi squared:
	$chi = 
	    sqrt(
		($SUM - $MEMORY_LENGTH * $data)**2 
		/ 
		($MEMORY_LENGTH * ($MEMORY_LENGTH + 1) * $AVG )
	    );

	

	$index = $index % $MEMORY_LENGTH;


	$SUM = $SUM - $MEMORY[$index] + $data;
	$AVG = $AVG - ($MEMORY[$index] / ($MEMORY_LENGTH + 1 ));
	$MEMORY[$index] = $data;



    }
    print_summary();


}

sub print_summary {

    if ( $QUIET  ){
	if ( $CHI_LIMIT and $chi > $CHI_LIMIT and not $QUIET_CHECK){
	    print "1\n";
	    $QUIET_CHECK = 1;
	    return;
	}
	return;
    }

    if ( $ALL_EVENTS ){
	print "$counter , $chi Vs $CHI_LIMIT, ";
	if ( $CHI_LIMIT and $chi > $CHI_LIMIT){
	    if ( $DRAMATIC ){
		if ( $EXP_START and $EXP_LENGTH and ( $counter > $EXP_START and $counter < ($EXP_START + $EXP_LENGTH))){
		    print "1 TRUE LEAP DETECTED\n";
		} elsif ( $EXP_START and $EXP_LENGTH and ( $counter < $EXP_START or $counter > $EXP_START + $EXP_LENGTH )){
		    print "1 FALSE LEAP DETECTED\n";
		}
	    } else {
		print "1\n";
	    }
	} else {
	    print "0\n";
	}
	return; 
    }

    if ($VERBOSE) {
	print_memory();
	verbose("chi($MEMORY_LENGTH) = $chi [".($chi**2)."] \n");
	verbose("new index: $index (sum: $SUM) [avg: $AVG]\n");
    } else {
	print "$chi";
	if ($CHI_LIMIT and $chi > $CHI_LIMIT ){
	    print " *";
	}
	print "\n";
    }
}


sub verbose {
    if ($VERBOSE) {
	print $_[0];
    }
}

sub print_memory {
    if ($VERBOSE) {
	my $line1;
	my $line2;
	my $i;
	for ($i = 0; $i < $MEMORY_LENGTH; $i++){
	
	    $line1 .= "$i  ";
	    $line2 .= "$MEMORY[$i]  ";
	    
	}
	print "$line1\n$line2\n";
    }
}

sub find_max {
    
    my $max = 0;
    foreach my $tall (@MEMORY){
	$max = $tall if $tall > $max;
    }
    return $max; 
}
