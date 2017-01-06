#!/usr/local/bin/perl

use strict;
use File::Basename;

# THE FIRST PARAMETER IS PATH TO FILE
# THE SECOND IS PATH TO WHERE I SHOULD WRITE
# THE THIRD IS mz_error
# THE FOURTH IS type
# THE FIFTH IS min_intensity
# THE SIXTH is min_reporters

my $read_file_path="";
my $write_file_path="";
my $write_txt_file_path="";
my $mz_error="";	
my $type="";
my $parsed_filename="";
my $min_intensity="";
my $min_reporters="";
my $should_select="0";
my $recal_mz_error="";

my $reporter_largest="0";
my $scaled_reporter_largest="0";


if ($ARGV[0]=~/\w/) { $read_file_path=$ARGV[0];} else { exit 1;}
if ($ARGV[1]=~/\w/) { $write_file_path=$ARGV[1];} else { exit 1;}
if ($ARGV[2]=~/\w/) { $write_txt_file_path=$ARGV[2];} else { exit 1;}
if ($ARGV[3]=~/\w/) { $mz_error=$ARGV[3];} else { exit 1;}
if ($ARGV[4]=~/\w/) { $type=$ARGV[4];} else { exit 1;}
if ($ARGV[5]=~/\w/) { $min_intensity=$ARGV[5];} else { exit 1;}
if ($ARGV[6]=~/\w/) { $min_reporters=$ARGV[6];} else { exit 1;}
if ($ARGV[7]=~/\w/) { $should_select=$ARGV[7];} else { exit 1;}
if ($ARGV[8]=~/\w/) { $recal_mz_error=$ARGV[8];} else { exit 1;}

$parsed_filename=basename($read_file_path);
my $directory = dirname($write_txt_file_path);
my $summary_path = $directory."\\intensity_summary.txt";
my @previous_intensity = ();

print "READ FILE PATH: $read_file_path\n";
print "WRITE FILE PATH: $write_file_path\n";
print "SUMMARY PATH: $summary_path\n";

my @reporters=();
if ($type=~/^iTRAQ8$/)
{
	@reporters=(113.1078,114.1112,115.1082,116.1116,117.1150,118.1120,119.1153,121.1220);
}
elsif ($type=~/^iTRAQ4$/)
{
	@reporters=(114.1112,115.1083,116.1116,117.1150);
}
elsif ($type=~/^TMT2$/)
{
	@reporters=(126.127725,127.131079);
}
elsif ($type=~/^TMT10$/)
{
	@reporters=(126.127725,127.124760,127.131079,128.128114,128.134433,129.131468,129.137787,130.134882,130.141141,131.138176);
}
elsif ($type=~/^TMT6$/)
{
	@reporters=(126.127725,127.131079,128.134433,129.137787,130.141141,131.138176);
}
elsif ($type=~/^TMT6OLD$/)
{
	@reporters=(126.127725,127.124760,128.134433,129.131468,130.141141,131.138176);
}
elsif ($type=~/^TMT0$/)
{
	@reporters=(126.127725);
}
else
{
	print "Error: Have not specified reporter ion properly\n";
	exit 1;
}

$reporter_largest = $reporters[-1];

unless ($read_file_path=~/\.mgf$/i)
{
	print "This doesn't look like it's an MGF file.\n";
	exit 1;
}
unless (open (IN, "$read_file_path"))
{
	print "Cannot open MGF file.\n";
	exit 1;
}

if ($should_select)
{
	unless (open (OUT, ">$write_file_path"))
	{
		print "Cannot write to selected .mgf file\n";
		exit 1;
	}
}

unless (open (OUT_TABLE,">$write_txt_file_path"))
{
	print "Cannot write to .reporter file\n";
	exit 1;
}

if (-e "$summary_path")
{
	print "Summary already exists.";
	open (TEMP_SUMMARY, "$summary_path");
	<TEMP_SUMMARY>;
	my $intensity_line = <TEMP_SUMMARY>;
	print $intensity_line;
	@previous_intensity = split('\t',$intensity_line);
	print join(", ",@previous_intensity);
	print "Summary ingested";
	close (TEMP_SUMMARY);
}
else{
	print "Summary not found";
}

open (TOTAL_INTENSITY_TABLE,">$summary_path" );
print OUT_TABLE qq!filename\tscan\tcharge\trt\tMS1_intensity!;

foreach my $reporter (@reporters)
{
	my $reporter_=int($reporter);
	##########################################################
	# Could be problematic with TMT10, because of replicants #
	##########################################################
	print OUT_TABLE qq!\t$type-$reporter_!;
	print TOTAL_INTENSITY_TABLE qq!\t$type-$reporter_!;
}
print OUT_TABLE qq!\t$type-sum\n!;

my $pepmass=0;
my $ms1_intensity="";
my $title="";
my $scans="";
my $charge="NA";
my $rt="";
my @mz=();
my @intensity=();
my $header="";
my $footer="";
my $started_reading_fragments=0;
my $done_reading_fragments=0;
my $points=0;
my $line="";

my @total_intensity=@previous_intensity;

while($line=<IN>)
{
	if ($line=~/^TITLE=(.*)$/)
	{
		$title=$1;
		if ($title=~/scans:\s*(.*)$/)
		{
			$scans=$1;
		}
		else
		{
			if ($title=~/^Scan ([0-9\.]+), Time=([0-9\.\-\+edED]+)/)
			{
				$scans=$1;
				$rt=$2;
			}
		}
	}
	if ($line=~/^PEPMASS=([0-9\.\-\+edED]+)\s?([0-9\.\-\+edED]*)\s*$/)
	{
		$pepmass=$1;
		$ms1_intensity=$2;
	}
	if ($line=~/^CHARGE=([0-9]+)[\.\-\+]+\s*$/)
	{
		$charge=$1;
	}
	if ($line=~/^RTINSECONDS=([0-9\.\-\+]+)\s*$/)
	{
		$rt=$1;
	}
	if ($line=~/^SCANS=([0-9\.\-\+]+)\s*$/)
	{
		$scans=$1;
	}
	if ($line=~/^([0-9\.\+\-edED]+)\s([0-9\.\+\-edED]+)/)
	{
		$started_reading_fragments=1;
		$mz[$points]=$1;
		$intensity[$points]=$2;
		$points++;
	}
	else
	{
		if ($started_reading_fragments==1)
		{
			$done_reading_fragments=1;
		}
	}
	if ($started_reading_fragments==0)
	{
		$header.=$line;
	}
	else
	{
		if ($done_reading_fragments==1)
		{
			$footer.=$line;
			#----------------------------------------------------------#
			my $max=0;
			my $sum=0;
			my @sum=();
			my @reporters_found=();
			my %reporter_dm=();
			my %reporter_intensity=();
			my $reporter_max=$reporters[0];
			my $mz_max=0;
			my $reporter_count=0;
			my $scaling_at_max=0;
			my $biggest_value_we_care_about=0;
			foreach my $reporter (@reporters)
			{
				$biggest_value_we_care_about = $reporter + ((3*$mz_error*$reporter)/1e+6);
				for(my $i=0;$i<$points;$i++)
				{
					# if it's inside the original threshold:
					# if ($mz[$i] > $reporter_largest+2){last;}
					if (abs($reporter-$mz[$i])<$mz_error*$reporter/1e+6)
					{
						if ($max<$intensity[$i])
						{
							$max=$intensity[$i];
							$mz_max=$mz[$i]; #That makes it so we know at what mz the highest count is 
							$reporter_max=$reporter;
							# In here, if we find a new global max, we say that's the new global max,
							# and that the mz_at that max is something, and the reporter is the reporter.
							# This is iterating points, when we've done all the points for all the
							# reporters, we move on.
						}
					}
					if ($mz[$i] > $biggest_value_we_care_about){last;}
				}
				# points come in sorted order, that means we can stop reading when
				# we get past the biggest we care about
			}
			if (0<$max)
			{
				# We've seen something. This is important, because otherwise we'll get division errors or worse.
				$scaling_at_max=$mz_max/$reporter_max; #This is what we use to make the new reporter ion mass array.
				my @scaled_reporters=();
				my $scaled_single_reporter=0;
				foreach my $reporter (@reporters)
				{
					$scaled_single_reporter = $reporter * $scaling_at_max;
					push (@scaled_reporters, $scaled_single_reporter);
					# Now, we've got a scaled reporter list.
					# print @scaled_reporters;
				}
				# Now that we have a scaled reporter list, we need to re-select.
				$scaled_reporter_largest=$scaled_reporters[-1];
				
				my $recal_reporter_count=0;
				my @recal_sum=();
				my $recal_sum=0;
				my $recal_sum_max=0;
				my $recal_reporters_found=0;
				my $biggest_scaled_value_we_care_about=0;
				foreach my $scaled_reporter (@scaled_reporters)
				{
					$recal_sum[$recal_reporter_count]=0;
					$biggest_scaled_value_we_care_about = $scaled_reporter + ((3*$recal_mz_error*$scaled_reporter)/1e+6);
					for(my $i=0;$i<$points;$i++)
					{
						if (abs($scaled_reporter-$mz[$i])<$recal_mz_error*$scaled_reporter/1e+6)
						{
							$recal_sum+=$intensity[$i];
							$recal_sum[$recal_reporter_count]+=$intensity[$i];
						}
						if ($mz[$i] > $biggest_scaled_value_we_care_about){last;}
					}
					if($recal_sum_max<$recal_sum[$recal_reporter_count])
					{
						$recal_sum_max=$recal_sum[$recal_reporter_count];
					}
					if ($recal_sum[$recal_reporter_count] >= $min_intensity){
						$recal_reporters_found++;
					}
					$recal_reporter_count++;
				}
				if ($recal_reporters_found >= $min_reporters)
				{
					if ($should_select)
					{
						print OUT $header;
						for(my $i=0;$i<$points;$i++)
						{
							#Space vs. tab?
							print OUT "$mz[$i] $intensity[$i]\n"; 
						}
						print OUT $footer;	
					}
					print OUT_TABLE qq!$parsed_filename\t$scans\t$charge\t$rt\t$ms1_intensity!;
					for(my $k=0;$k<$recal_reporter_count;$k++)
					{
						# It used to divide by recal_sum_max
						my $sum_=$recal_sum[$k]/(1.0*$recal_sum);
						print OUT_TABLE qq!\t$sum_!;
						$total_intensity[$k]+=$recal_sum[$k];
					}
					print OUT_TABLE qq!\t$recal_sum\n!;
				}
			}
			$pepmass="";
			$title="";
			$charge="";
			@mz=();
			@intensity=();
			$header="";
			$footer="";
			$started_reading_fragments=0;
			$done_reading_fragments=0;
			$points=0;
		}
	}
}

if ($should_select)
{
	close(OUT);
}
print TOTAL_INTENSITY_TABLE "\n",  join( "\t", @total_intensity ), "\n";

close(OUT);
close(TOTAL_INTENSITY_TABLE);

exit 0;