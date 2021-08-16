#!/bin/bash
# **********************************************************
# * Author        : chenqi
# * Email         : chenqi@gooalgene.com
# * Create time   : 2021-05-10 14:11
# * Last modified : 2021-05-10 14:11
# * Filename      : cov_19_mutation_fatovcf.sh
# * Description   : 
# **********************************************************
if [ ! -n "$1" ] || [ $1 == "-h" ] || [ $1 == "--help" ]; then
    echo "Usage"
    echo "  sh $0 <fasta> <csv file> <prob:C|G|S>"
else
echo start at time `date +%F'  '%H:%M:%S`
path_script="/project/user/chenqi/test/test_nothing/novel_coron_script/"
ref_seq="/project/user/chenqi/test/test_novel_coronavirus/NC_045512.2.fasta"
vcf_deal="$path_script/vcf_deal_new_model.py"
dos_deal="$path_script/dos_deal_new_model.py"
if [ ! -n "$3" ]; then
    country=''
else
    country=$3
fi
deep=`grep "^>" $1 |wc -l`
prefix=`python3 -c "import sys;print(sys.argv[1].split('/')[-1].rsplit('.fasta')[0])" $1`
if [ ! -d "/$prefix" ]; then
    mkdir $prefix
fi
cd $prefix
cat $ref_seq >tmp.fas && cat $1 >> tmp.fas
time /usr/bin/mafft --thread 50 tmp.fas >$prefix.aln
time /biostack/mirror/hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/faToVcf $prefix.aln $prefix.aln.vcf.xls
python3 $vcf_deal $prefix.aln.vcf.xls $prefix.txt 0.5 $2
grep "^>" $1|awk -F '|' '{print $2}'| python3 -c "import sys;a = [i.strip() for i in sys.stdin];print('、'.join(a))" >$prefix.acc.txt
python3 $dos_deal fatovcf $prefix.txt $deep $3
echo finish at time `date +%F'  '%H:%M:%S`
fi