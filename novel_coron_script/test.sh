path_script="/project/user/chenqi/test/test_nothing/novel_coron_script/"
vcf_deal="$path_script/vcf_deal_new_model.py"
echo $vcf_deal
arr=`python3 -c "import sys;print(sys.argv[1].split('/')[-1].rsplit('.fasta')[0])" $1`
echo $arr
