
# my $a="sam";
# if($a!=~/sam/)
# {
# 	print "YUP\n";
# }
# else
# {
# 	print "NUP\n";
# }
use strict;


# my $a=1.e6;
# my $b=2*$a;
# print "$b\n"

# my $a=$ARGV[0];
# my $b=$ARGV[1];

# my @b=split /,/,$a;
# print "$b\n";

# my @a=('1','2','3');
# my $b=scalar @a;
# print "@a\n";
# print "$b\n";

# my @c=();
# my$d=scalar @c;
# print "@c\n";
# print "$d\n";

# my @e=split /,/,"";
# my $f=scalar @e;
# print "@e\n";
# print "$f\n";

for(my $i=0; $i< scalar @ARGV;$i++)
{
	print "ARG $i: '$ARGV[$i]'\n";
}
my $q="";
my $r=undef;
my $s=0;
# print "$q==$r";


my @a=(1,2);
if (defined $a[0])
{
	print "a0 is defined\n";
}
if (defined $a[1])
{
	print "a1 is defined\n";
}
if (defined $a[2])
{
	print "a2 is defined\n";
}
if (defined $a[20])
{
	print "a20 is defined\n";
}

if ("sammy" eq "sammy")
{
	print "sammy is sammy\n";
}