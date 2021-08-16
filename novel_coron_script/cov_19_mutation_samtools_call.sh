#!/bin/bash
# **********************************************************
# * Author        : chenqi
# * Email         : chenqi@gooalgene.com
# * Create time   : 2021-04-29 17:20
# * Last modified : 2021-05-06 
# * Filename      : test.sh
# * Description   : 
# **********************************************************
if [ ! -n "$1" ] || [ $1 == "-h" ] || [ $1 == "--help" ]; then
    echo "Usage"
    echo "  sh $0 <fasta> <thread> <csv> <prob:C|G|S>"
else
echo start at time `date +%F'  '%H:%M:%S`
ref_seq="/project/user/chenqi/test/test_novel_coronavirus/NC_045512.2.fasta"
minimap2="/home/chenqi/bin/soft/minimap2"
samtools="/usr/local/bin/samtools"
bcftools="/usr/local/bin/bcftools"
vcf_deal="/project/user/chenqi/test/test_nothing/novel_coron_script/new_vcf.py"
dos_deal="/project/user/chenqi/test/test_nothing/novel_coron_script/dos_deal_new_model.py"
deep=`grep "^>" $1 |wc -l`
prefix=`python3 -c "import sys;print(sys.argv[1].split('/')[-1].rsplit('.fasta')[0])" $1`
if [ ! -d "/$prefix" ]; then
    mkdir $prefix
fi
cd $prefix
/usr/bin/perl /project/Analysis/Test/alignment/hCOV_19/splitfa_210429.3.pl -refseq $ref_seq -fafile $1
$minimap2 -t $2 -ax map-ont $ref_seq $1 |$samtools view -bS -@ $2 -|$samtools sort -@ $2 - >$prefix.bam
$samtools index $prefix.bam
$samtools mpileup -d $deep -A -f $ref_seq $prefix.bam >$prefix.mpileup
java -Xmx8g -jar /biostack/tools/variation/VarScan-2.4.1/VarScan.jar mpileup2cns $prefix.mpileup --output-vcf 1 --min-coverage 100 --min-var-freq 0.0004 > $prefix.VarScan2.vcf
awk -F '\t' '{if($1~"#" || ($5!="" && $5!=".")) print}' $prefix.VarScan2.vcf >>$prefix.VarScan2.pass.vcf
# perl /project/Analysis/Test/alignment/hCOV_19/extract_position_genotype210706.pl $prefix.VarScan2.pass.vcf $3
perl /project/Analysis/Test/alignment/hCOV_19/extract_position_genotype210729.pl $prefix.VarScan2.pass.vcf $3 $4
if [ $deep -lt 10000 ];then
    grep "^>" $1|awk -F '|' '{print $2}'| python3 -c "import sys;a = [i.strip() for i in sys.stdin];print('、'.join(a))" >$prefix.acc.txt
fi
python3 $dos_deal samtools $prefix.txt $deep $4
rm $prefix.mpileup
rm $prefix.VarScan2.pass.vcf
echo finish at time `date +%F'  '%H:%M:%S`
fi

