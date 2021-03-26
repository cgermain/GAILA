#!/usr/local/bin/perl

use strict;
use File::Basename;
use Math::MatrixReal;

$SIG{INT} = sub { die "" };

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
my $inverse_string="";

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
if ($ARGV[9]=~/\w/) { $inverse_string=$ARGV[9];} else { exit 1;}

$parsed_filename=basename($read_file_path);
my $directory = dirname($write_txt_file_path);

# Windows/Unix Compatibility
my $dirsep = ($^O eq "MSWin32" or $^O eq "cygwin") ? "\\" : "/";
my $summary_path = $directory.$dirsep."intensity_summary.txt";
my $mgf_path = $directory.$dirsep."mgf_summary.txt";

my @previous_intensity = ();
my $previous_summary_exists = 0;

my $inverse_matrix = Math::MatrixReal->new_from_string($inverse_string);

my $short_filename = basename($read_file_path);

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
elsif ($type=~/^TMT11$/)
{
	@reporters=(126.127725,127.124760,127.131079,128.128114,128.134433,129.131468,129.137787,130.134882,130.141141,131.138176,131.144499);
}
elsif ($type=~/^TMT16$/)
{
	@reporters=(126.127726,127.124761,127.131081,128.128116,128.134436,129.131471,129.13779,130.134825,130.141145,131.13818,131.1445,132.141535,132.147855,133.14489,133.15121,134.148245);
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
	# Summary already exists
	$previous_summary_exists = 1;
	open (TEMP_SUMMARY, "$summary_path");
	<TEMP_SUMMARY>;
	my $intensity_line = <TEMP_SUMMARY>;
	@previous_intensity = split('\t',$intensity_line);
	close (TEMP_SUMMARY);
}
else{
	#Summary not found
}

open (TOTAL_INTENSITY_TABLE,">$summary_path" );

print OUT_TABLE qq!filename\tscan\tcharge\trt\tMS1_intensity!;

my $reporters_string = "";
foreach my $reporter (@reporters)
{
	my $reporter_=int($reporter);
	$reporters_string .= $type . "-" . $reporter_ . "\t";
}

if ($type eq "TMT10")
{
	$reporters_string = "TMT10-126\tTMT10-127N\tTMT10-127C\tTMT10-128N\tTMT10-128C\tTMT10-129N\tTMT10-129C\tTMT10-130N\tTMT10-130C\tTMT10-131\t";
}
if ($type eq "TMT11")
{
	$reporters_string = "TMT11-126\tTMT11-127N\tTMT11-127C\tTMT11-128N\tTMT11-128C\tTMT11-129N\tTMT11-129C\tTMT11-130N\tTMT11-130C\tTMT11-131N\tTMT11-131C\t";
}
if ($type eq "TMT16")
{
	$reporters_string = "TMT16-126\tTMT16-127N\tTMT16-127C\tTMT16-128N\tTMT16-128C\tTMT16-129N\tTMT16-129C\tTMT16-130N\tTMT16-130C\tTMT16-131N\tTMT16-131C\tTMT16-132N\tTMT16-132C\tTMT16-133N\tTMT16-133C\tTMT16-134N\t";
}

print TOTAL_INTENSITY_TABLE qq!\t$reporters_string!;
$reporters_string .= $type . "-sum\n";
print OUT_TABLE qq!\t$reporters_string!;

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
#initialize to all zeros based on the number of reporters
#makes summary output includes zeros and not just empty values
my @total_intensity=(0) x scalar @reporters;	
my $total_ms1=0;

my $previous_scan = "";
my $previous_title = "";

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
				$reporter_count++;
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

				#create a matrixreal from the intensities
				my $intensity_matrix_string = "[ " . join(" ",@recal_sum) . " ]\n";
				my $intensity_matrix = Math::MatrixReal->new_from_string($intensity_matrix_string);

				#crossover correct the intensities with the inverse matrix
				my $product_matrix = $intensity_matrix->multiply($inverse_matrix);

				my @product_array = $product_matrix->as_list;

				#get the sum of intensities after crossover correction
				my $product_array_sum = 0;
				for (@product_array) {
				 	$product_array_sum += $_;
				}

				#force any negative intensities to be zero
				my @zero_product_array = map{$_<0 ? 0:$_} @product_array;

				#get the sum of intensities after crossover correction and after forcing negatives to zero
				my $zero_product_array_sum = 0;
				for (@zero_product_array) {
					$zero_product_array_sum += $_;
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
					
					#normalize the intensities
					for(my $k=0;$k<$recal_reporter_count;$k++)
					{
						# It used to divide by recal_sum_max
						my $sum_ = 0;
						if ($zero_product_array_sum != 0){
							$sum_=$zero_product_array[$k]/(1.0*$zero_product_array_sum);
						}

						print OUT_TABLE qq!\t$sum_!;
						#if this is a replicate of the previous scan, don't add its intensity to the total
						if (($scans ne $previous_scan) && ($title ne $previous_title))
						{
							$total_intensity[$k]+=$zero_product_array[$k];
						}
					}
					print OUT_TABLE qq!\t$zero_product_array_sum\n!;
					#if this is a replicate of the previous scan, don't add its intensity to the total
					if (($scans ne $previous_scan) && ($title ne $previous_title))
					{
						$total_ms1+=$ms1_intensity;
					}
				}
			}

			else #max = 0
			{
				if ($min_intensity == 0 or $min_reporters == 0)
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

					#if a max wasn't found and we still want to display all the rows
					print OUT_TABLE qq!$parsed_filename\t$scans\t$charge\t$rt\t$ms1_intensity!;
					for(my $k=0;$k<$reporter_count;$k++)
					{
						#since max=0, just output 0 for everything
						my $sum_ = 0;
						print OUT_TABLE qq!\t$sum_!;
					}
					print OUT_TABLE qq!\t$sum\n!;
					#if this is a replicate of the previous scan, don't add its intensity to the total ms1
					if (($scans ne $previous_scan) && ($title ne $previous_title))
					{
						$total_ms1+=$ms1_intensity;
					}
				}

			}
			
			$previous_title = $title;
			$previous_scan = $scans;

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

my @combined_intensity = ();
for (my $i=0; $i < scalar @total_intensity; $i++){
	@combined_intensity[$i] = @total_intensity[$i] + @previous_intensity[$i];
}

my @rounded_combined_intensity = map{int($_ + 0.5)} @combined_intensity;
my @rounded_total_intensity = map{int($_ + 0.5)} @total_intensity;

print TOTAL_INTENSITY_TABLE "\n",  join("\t", @rounded_combined_intensity);
open (MGF_TABLE, ">>$mgf_path");
print MGF_TABLE $parsed_filename, "\t", int($total_ms1 + 0.5), "\t", join("\t", @rounded_total_intensity), "\n";

close(OUT);
close(TOTAL_INTENSITY_TABLE);
close(MGF_TABLE);
exit 0;