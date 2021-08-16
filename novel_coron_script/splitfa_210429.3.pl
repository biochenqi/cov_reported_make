#!/usr/bin/perl

use strict;
use Getopt::Long;
use threads;
use Cwd 'abs_path';
use List::Util qw/max min sum/;
use Encode;
use Term::ANSIColor;

my $abs_path = abs_path(__FILE__);
my @tmp = split(/\//, $abs_path);
pop(@tmp);
$abs_path = join("/", @tmp);

my $usage = "Software name: Software  #多序列拆分比对分析软件
	
	Model:San-Multi-alingment

	Version:	 1.0.1.210429

	Function: analysis Pipeline

	Auther:    mingchen, mingc\@sanwaygene.com, SanSure

Example:
    perl ###
    nohup perl  ### >run.log 2>&1
Config
    
\n";

my $refseqf;
my $h;
my $samplefile;
my $Nthread=50;
my $thd=1;
my $space = " ";
my $sep = "======================================================================================";
my $version = "Version 1.0.1.0925";


GetOptions(  
                    "refseq=s"=>\$refseqf,
                    "fafile=s"=> \$samplefile,
                    "Nthread=i"=> \$Nthread,
                    "thread=i"=>\$thd,
			         "h" => \$h);
die "$usage" if($h);


open RS,"<$refseqf" or die "Can not Load the refseq file, Please check it!";
open FA,"<$samplefile" or die "Can not Load the fasta file, Please check it!";
open (OUT,">$samplefile\.1.fa") or die;
open (OUTid,">$samplefile\.1.id.txt") or die;

$/=">";my $test=<RS>;$/="\n";

my $refseqid=<RS>;
my $refseq=<RS>;
print OUT ">$refseqid$refseq";
my $LenRef=length($refseq);
my $cutLen=$LenRef*0.8;

$/=">";<FA>;$/="\n";
my $n=1;
my $fcount=1;
while(<FA>){
    chomp;
	my $seqid=$_;
	$/=">";
	my $seq=<FA>;
		chomp $seq;
		$seq=~s/\s//g;
#		$seq=~s/N//ig; ## stand for gap or low quality
		my $len=length($seq);
		$/="\n";
		my $tempid=(split/\/|\|/,$seqid)[4];
		if($len>=$cutLen){
			print OUT ">$seqid\n$seq\n";
	    print OUTid "$tempid,";
	    		$n++;
			}
		if($n>=$Nthread){
		 close OUT;
		 last;
	}	
}
close OUT;close OUTid;

`mafft $samplefile\.1.fa >$samplefile\.1.fa.aln`;

