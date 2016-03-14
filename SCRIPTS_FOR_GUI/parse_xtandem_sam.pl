#!c:/perl/bin/perl.exe
#

# SOMETHING TO NOTE: NOW I'M USING THE FULL PATHS.

use strict;

my $error=0;
my $xmlfile=0;
my $xmldir=0;
my $threshold=0;
my $proton_mass=1.007276;
my $label_mass_int=0;
my $genefile=0;

my $unacceptable_mass_array_string="";
my $unacceptable_mod_array_string="";
my $unacceptable_label_mod_string="";

my @unacceptable_mass_array=();
my @unacceptable_mod_array=();
my @unacceptable_label_mod_array=();

if (defined $ARGV[0]) { $xmlfile=$ARGV[0];} else { exit 1; }
if (defined $ARGV[1]) { $xmldir=$ARGV[1];} else { exit 2; }
if (defined $ARGV[2]) { $threshold=$ARGV[2];} else { exit 3; }
if (defined $ARGV[3]) { $label_mass_int=$ARGV[3];} else { exit 4; }
if (defined $ARGV[4]) { $genefile=$ARGV[4];} else { exit 5; }
if (defined $ARGV[5]) { $unacceptable_mass_array_string=$ARGV[5];} else { exit 6; }
if (defined $ARGV[6]) { $unacceptable_mod_array_string=$ARGV[6];} else { exit 7; }
if (defined $ARGV[7]) { $unacceptable_label_mod_string=$ARGV[7];} else { exit 8; }


@unacceptable_mass_array=split /,/,$unacceptable_mass_array_string;
@unacceptable_mod_array=split /,/,$unacceptable_mod_array_string;
@unacceptable_label_mod_array=split /,/,$unacceptable_mod_array_string;

my $length_of_unacceptable_mass=scalar @unacceptable_mass_array;
my $length_of_unacceptable_mod=scalar @unacceptable_mod_array;

unless ($length_of_unacceptable_mass == $length_of_unacceptable_mod)
{
  print "The two unacceptable mass and unacceptable mod arrays should have equal value, instead they have value $length_of_unacceptable_mass and $length_of_unacceptable_mod , respectively";
  exit 9;
}

# $threshold=$threshold*1.0;

if ($error==0)
{
  #$xmlfile=~s/\\/\//g;
  my $line="";
  my %genes=();
  my %gene_ids=();
  my %protein_descriptions=();
  if (open (IN,qq!$genefile!))
  {
    my $no_newline="";
    while($line=<IN>)
    {
      chomp($line);
      # if ($line=~/^([^\t]+)\t([^\t]*)\t([^\t]*)\t([^\t]*)$/)
      if ($line=~/^([^\t]+)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)$/)
      {
        $genes{$1}=$4;
        $gene_ids{$1}=$3;
        # Just trying this out, because there are newline problems.
        $no_newline=$5;
        $no_newline=~s/(\n|\r)//; #because chomp doesn't delete it on mac.
        $protein_descriptions{$1}=$no_newline;
        #print qq!$1-$4\n!;
      }
    }
    close(IN);
  }
  else
  {
    exit 10;
  }
  #print qq!###$genes{"ENSRNOP00000019021"}###\n!;
  open (IN,qq!$xmlfile!) || die "Could not open $xmlfile\n";
  open (OUT,qq!>$xmlfile.txt!) || die "Could not open $xmlfile\n";
  print OUT qq!filename\tscan\tcharge\tpre\tpeptide\tpost\tmodifications\tstart\tpeptide expectation\tlabeling\ttryptic\tmissed\tunacceptable modifications\tprotein log(e)\tprotein\tdescription\tgene\tgene_id\tother proteins\tother descriptions\tother genes\tother gene ids\tdifferent genes\n!;
  my $xmlfile_=$xmldir;
  # $xmlfile_=~s/\.xml$//;
  # mkdir($xmlfile_);
  # system(qq!del $xmlfile_/*!);
  my %filenames=();
  my $mh="";
  my $mz="";
  my $charge="";
  my $filename="";
  my $f_name_sans_mgf="";
  my @f_name_array_to_hold_stuff=();
  my $scan="";
  my $proteins="";
  my $start="";
  my $end="";
  my $expect="";
  my $pre="";
  my $post="";
  my $peptide="";
  my $title="";
  my $modifications="";
  my $tryptic="";
  my $missed="";
  my $unacceptable="N";
  my %protein_expect=();
  while ($line=<IN>)
  {
    # if ($line=~/^\<protein\s+.*expect="([^\"]+)"\s+.*label="([^\"]+)"/)
    if ($line=~/^\<protein\s+.*expect="([^\"]+)"\s+.*label="([^\".\s]+).*"/)
    {
      my $protein_expect=$1;
      my $protein_name=$2;
      $protein_expect{$protein_name}=$protein_expect;
      if($protein_name!~/\:reversed$/) { $proteins.="#$protein_name#"; }
      $start="";
      $end="";
      $expect=1;
      $pre="";
      $post="";
      $peptide="";
      $title="";
      $modifications="";
      $tryptic="";
      $missed="";
      $unacceptable="N";
    }
    if ($line=~/\<domain\s+id="([0-9\.edED\+\-]+)".*start="([0-9]+)".*end="([0-9]+)".*expect="([0-9\.edED\+\-]+)".*mh="([0-9\.edED\+\-]+)".*delta="([0-9\.edED\+\-]+)".*pre="(.*)".*post="(.*)".*seq="([A-Z]+)".*missed_cleavages="([0-9]+)"/)
    {
      my $start_=$2;
      my $end_=$3;
      my $expect_=$4;
      my $pre_=$7;
      my $post_=$8;
      my $peptide_=$9;
      if ($expect_<$expect)
      {
        $start=$start_;
        $end=$end_;
        $expect=$expect_;
        $pre=$pre_;
        $post=$post_;
        $peptide=$peptide_;
        $modifications="";
        $missed=0;
        my $temp=$peptide;
        while ($temp=~s/^[^KR]*[KR](.)/$1/)
        {
          my $aa=$1;
          if ($aa!~/P/) { $missed++; }
        }
        $tryptic="Y";
        if ($pre!~/[KR]$/)
        {
          if ($pre!~/\[M$/ and $pre!~/\[$/)
          {
            $tryptic="N";
          }
        }
        else
        {
          if ($peptide=~/^P/)
          {
            $tryptic="N";
          }
        }
        if ($peptide!~/[KR]$/)
        {
          if ($post!~/^\]/)
          {
            $tryptic="N";
          }
        }
        else
        {
          if ($post=~/^P/)
          {
            $tryptic="N";
          } 
        }
        $unacceptable="N";
        #$peptide=~tr/L/I/;
        if ($line!~/\<domain[^\>]+\/\>/)
        { 
          my $labeled_Y_Nterm=0;
          while ($line!~/\<\/domain\>/)
          {
            $line=<IN>;
            while($line=~s/^\s*\<aa\s+type=\"([A-Z])\"\s+at=\"([0-9]+)\"\s+modified=\"([0-9\.\-\+edED]+)\"\s*//)
            {
              my $mod_aa=$1;
              my $mod_pos=$2;
              my $mod_mass=$3;
              my $mod_pm="";
              my $mod_id="";
              if ($line=~s/^\s*pm=\"([A-Z])\"\s*id="([^\"]+)"\s*//)
              {
                $mod_pm=$1;
                $mod_id=$2;
              }
              $line=~s/^\s*\/\>\s*//;
              my $mod_pos_=$mod_pos-$start+1;
              #my $test_aa = substr $peptide,$mod_pos_-1,1;
              #if ($test_aa=~/^$mod_aa$/)
              #{
                $modifications.="$mod_mass\@$mod_aa$mod_pos_->$mod_pm,";

                my $current_unacc_mass="";
                my $current_unacc_mod="";
                for(my $mods=0;$mods<$length_of_unacceptable_mod;$mods++)
                {
                  $current_unacc_mass=$unacceptable_mass_array[$mods];
                  $current_unacc_mod=$unacceptable_mod_array[$mods];
                  if ($mod_aa eq $current_unacc_mod and int((1*$current_unacc_mass) + 0.5)==int((1*$mod_mass) + 0.5))
                  {
                    $unacceptable="Y";
                    last;
                  }
                }
                unless ($unacceptable eq "Y")
                {
                  my $bad_label="";
                  foreach $bad_label (@unacceptable_label_mod_array) {
                    if ($mod_aa eq $bad_label and $mod_pos_!=1 and int($mod_mass+0.5)==$label_mass_int)
                    {
                      $unacceptable="Y";
                      last;
                    }
                    if ($mod_aa eq $bad_label and $mod_pos_==1)
                    {
                      if(int($mod_mass + 0.5)==$label_mass_int){$labeled_Y_Nterm+=1;}
                      if(int($mod_mass + 0.5)==2*$label_mass_int){$labeled_Y_Nterm+=2;}
                    }
                  }
                }
                # if ($mod_aa=~/^M$/ and int($mod_mass+0.5)==32)
                # {
                #   $unacceptable="Y";
                # }
                # if ($mod_aa=~/^W$/ and int($mod_mass+0.5)==32)
                # {
                #   $unacceptable="Y";
                # }
                # if ($mod_aa=~/^W$/ and int($mod_mass+0.5)==16)
                # {
                #   $unacceptable="Y";
                # }
                # if ($mod_aa=~/^Q$/ and int($mod_mass+0.5)==1)
                # {
                #   $unacceptable="Y";
                # }
                # if ($mod_aa=~/^N$/ and int($mod_mass+0.5)==1)
                # {
                #   $unacceptable="Y";
                # }
                # if ($mod_aa=~/^Y$/ and $mod_pos_!=1 and int($mod_mass+0.5)==$label_mass_int)
                # {
                #   $unacceptable="Y";
                # }
                # if ($mod_aa=~/^Y$/ and $mod_pos_==1)
                # {
                #   if (int($mod_mass+0.5)==$label_mass_int) { $labeled_Y_Nterm+=1; }
                #   if (int($mod_mass+0.5)==2*$label_mass_int) { $labeled_Y_Nterm+=2; }
                # }



              #}
            }
          }
          if ($labeled_Y_Nterm>1) { $unacceptable="Y"; } 
        }
      }
    }
    if($line=~/<note label=\"Description\">(.+?)<\/note>/)  
    {
      $title=$1;
      if($title=~/scans: (\S+)/)
      {
        $scan=$1;
        $scan=~s/,.*$//;
      }
      if($title=~/source=(.*\.mgf)/)
      {
        # 
        $filename=$1;
        $filename=~s/^.*[\/\\]([^\/\\]+)$/$1/;
        @f_name_array_to_hold_stuff=split(".mgf",$filename);
        $f_name_sans_mgf=$f_name_array_to_hold_stuff[0];
      }
    }
    if($line=~/<GAML\:attribute type=\"M\+H\">(.*)<\/GAML\:attribute>/)
    {
      $mh=$1;   
    }
    if($line=~/<GAML:attribute type="charge">([0-9]+)<\/GAML:attribute>/)
    {
      $charge=$1;
      $mz=($mh+(($charge-1)*$proton_mass))/$charge; 
      if($expect<$threshold)
      {
        my $protein_="";
        my $protein_expect="";
        my $temp=$proteins;
        while($temp=~s/^#([^#]+)#//)
        {
          my $temp_=$1;
          if ($protein_expect{$temp_}<$protein_expect)
          {
            $protein_=$temp_;
            $protein_expect=$protein_expect{$temp_};
          }
        }
        my $protein_other="";
        my $other_genes="";
        my $other_gene_ids="";
        my $other_protein_descriptions="";
        my $different_genes="N";
        my $different_gene_fam="N";
        my $temp=$proteins;
        while($temp=~s/^#([^#]+)#//)
        {
          my $temp_=$1;
          if ($temp_!~/^$protein_$/)
          {
            $protein_other.="#$temp_#";
            if ($genes{$temp_}=~/\w/ and $other_genes!~/#$genes{$temp_}#/i)
            {
              $other_genes.="#\U$genes{$temp_}#";
            }
            else
            {
              if ($genes{$temp_}!~/\w/ and $other_genes!~/#NotFound#/i)
              {
                $other_genes.="#NotFound#";
              }
            }
            if ($gene_ids{$temp_}=~/\w/ and $other_gene_ids!~/#$gene_ids{$temp_}#/)
            {
              $other_gene_ids.="#$gene_ids{$temp_}#";
            }
            else
            {
              if ($gene_ids{$temp_}!~/\w/ and $other_gene_ids!~/#NotFound#/)
              {
                $other_gene_ids.="#NotFound#";
              }
            }
            if ($protein_descriptions{$temp_}=~/\w/ and (index($other_protein_descriptions,"#$protein_descriptions{$temp_}#")==-1))
            # if ($protein_descriptions{$temp_}=~/\w/ and $other_protein_descriptions!~/#$protein_descriptions{$temp_}#/)
            {
              $other_protein_descriptions.="#$protein_descriptions{$temp_}#";
            }
            else
            {
              if ($protein_descriptions{$temp_}!~/\w/ and $other_protein_descriptions!~/#NotFound#/)
              {
                $other_protein_descriptions.="#NotFound#";
              }
            }
            my $temp__=$genes{$temp_};
            $temp__=~s/([0-9\.]).*$//;
            #print qq!#$genes{$protein_}#$temp__#\n!;
            if ($genes{$protein_}!~/^$temp__([0-9\.]?).*$/i)
            {
              $different_gene_fam="Y";
            }
            if ($genes{$protein_}!~/^$genes{$temp_}$/i)
            {
              $different_genes="Y";
            }
          }
        }
        $protein_other=~s/##/,/g;
        $protein_other=~s/#//g;
        $other_genes=~s/##/,/g;
        $other_genes=~s/#//g;
        $other_gene_ids=~s/##/,/g;
        $other_gene_ids=~s/#//g;
        $other_protein_descriptions=~s/##/,/g;
        $other_protein_descriptions=~s/#//g;
        my %itraq_labels=();
        my $temp=$modifications;
        $modifications="";
        my $complete_labeling=0;
        while($temp=~s/^([^\@]+)\@([A-Z])([0-9]+)\-?\>?([A-Z]?),//)
        {
          my $mod_mass=$1;
          my $mod_aa=$2;
          my $mod_res=$3;
          my $mod_pm=$4;
          #my $test_aa = substr $peptide,$mod_res-1,1;
          #if ($test_aa=~/^$mod_aa$/)
          #{
            $modifications.="$mod_mass\@$mod_aa$mod_res";
            if ($mod_pm=~/\w/){ $modifications.="->$mod_pm"; }
            $modifications.=",";
            if ($mod_pm=~/^K$/)
            {
              $complete_labeling++;
            }
            if ($mod_res==1 or $mod_aa=~/^K$/)
            {
              if (int($mod_mass)==$label_mass_int)
              {
                $itraq_labels{$mod_res}++;
              }
              if (int($mod_mass)==-$label_mass_int)
              {
                $itraq_labels{$mod_res}--;
              }
              if (int($mod_mass)==2*$label_mass_int)
              {
                $itraq_labels{$mod_res}+=2;
              }
            }
          #}
        }
        my $labeling=0;
        my $reactive_residue_count=0;
        my $temp=$peptide;
        while($temp=~s/^([A-Z])//)
        {
          my $aa=$1;
          $reactive_residue_count++;
          if ($itraq_labels{$reactive_residue_count}>0)
          {
            $labeling+=$itraq_labels{$reactive_residue_count};
          }
          if ($reactive_residue_count==1)
          {
            $complete_labeling++;
          }
          if ($aa=~/^K$/)
          {
            $complete_labeling++;
          }
        }
        $labeling/=1.0*$complete_labeling;
        if ($modifications!~/\w/) { $modifications="N"; }
        if ($protein_other!~/\w/) { $protein_other="N"; }
        my $gene=$genes{$protein_};
        if ($gene!~/\w/) { $gene="None"; }
        if ($other_genes!~/\w/) { $other_genes="None"; }
        my $gene_id=$gene_ids{$protein_};
        if ($gene_id!~/\w/) { $gene_id="None"; }
        if ($other_gene_ids!~/\w/) { $other_gene_ids="None"; }
        my $protein_description=$protein_descriptions{$protein_};
        if ($protein_description!~/\w/) { $protein_description="None"; }
        if ($other_protein_descriptions!~/\w/) { $other_protein_descriptions="None"; }
        
        print OUT qq!$filename\t$scan\t$charge\t$pre\t$peptide\t$post\t$modifications\t$start\t$expect\t$labeling\t$tryptic\t$missed\t$unacceptable\t$protein_expect\t$protein_\t$protein_description\t$gene\t$gene_id\t$protein_other\t$other_protein_descriptions\t$other_genes\t$other_gene_ids\t$different_genes\n!;
        open (OUT_,qq!>>$xmlfile_/$f_name_sans_mgf.reporter!) || die "Could not open $xmlfile_/$filename.reporter\n";
        if ($filenames{$filename}!~/\w/)
        {
          $filenames{$filename}=1;
          print OUT_ qq!filename\tscan\tcharge\tpre\tpeptide\tpost\tmodifications\tstart\tpeptide expectation\tlabeling\ttryptic\tmissed\tunacceptable modifications\tprotein log(e)\tprotein\tdescription\tgene\tgene_id\tother proteins\tother descriptions\tother genes\tother gene ids\tdifferent genes\n!;
        }
        print OUT_ qq!$filename\t$scan\t$charge\t$pre\t$peptide\t$post\t$modifications\t$start\t$expect\t$labeling\t$tryptic\t$missed\t$unacceptable\t$protein_expect\t$protein_\t$protein_description\t$gene\t$gene_id\t$protein_other\t$other_protein_descriptions\t$other_genes\t$other_gene_ids\t$different_genes\n!;
        close(OUT_);
      }
      $mh="";
      $mz="";
      $filename="";
      $f_name_sans_mgf="";
      $charge="";
      $scan="";
      $proteins="";
      $start="";
      $end="";
      $expect="";
      $pre="";
      $post="";
      $peptide="";
      $title="";
      $modifications="";
      $tryptic="";
      $missed="";
      $unacceptable="N";
    }
  } 
  close(IN);
  close(OUT); 
}