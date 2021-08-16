import sys

def info_deal(info):
    #DP4:high-quality reference forward bases, ref reverse, alternate for and alt rev bases
    info = info.split('DP4=')
    alt_num = int(info[1].split(';')[0].split(',')[-2])
    ref_num = int(info[0].split(';')[0].strip('DP='))
    return ref_num,alt_num

list_info = []
#           ORF（SA-XIN-F3) (SA-XIN-07F1) N(tdy-N-F1)  (SA-N-XIN-F1)
#               国内版         国际版         国际版         国内版
primer_probe = [[9093,9238],[12643,12736],[28626,28708],[28881,28979]]
with open(sys.argv[1],'r') as f,open(sys.argv[2],'w') as w:
    for line in f:
        if line.startswith('#'):continue
        #处理内容
        line = line.strip().split('\t')
        ref_num,alt_num = info_deal(line[7])
        list_info.append([line[1],line[3] + line[1] + line[4],line[3],line[4],float(alt_num)/float(ref_num),alt_num,ref_num])

    w.write('位置\t突变(Genome)\tREF\tALT\t总突变比例\t突变计数\t序列总数\n')
    for info in list_info:
        #设置阈值
        if info[4] > float(sys.argv[3]):
            # if primer_probe[0][0]<= int(info[0]) <=primer_probe[0][1] or primer_probe[1][0]<= int(info[0]) <=primer_probe[1][1]:
            if primer_probe[0][0]<= int(info[0]) <=primer_probe[0][1]:
                w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\tORF\n'%(info[4]*100,info[5],info[6]))
            # elif primer_probe[2][0]<= int(info[0]) <=primer_probe[2][1] or primer_probe[3][0]<= int(info[0]) <=primer_probe[3][1]:
            elif primer_probe[3][0]<= int(info[0]) <=primer_probe[3][1]:
                w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\tN\n'%(info[4]*100,info[5],info[6]))
            else:
                w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\n'%(info[4]*100,info[5],info[6]))
        else:
            if primer_probe[0][0]<= int(info[0]) <=primer_probe[0][1]  and info[4] > float(sys.argv[3])/10:
                w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\tORF\n'%(info[4]*100,info[5],info[6]))
            elif primer_probe[3][0]<= int(info[0]) <=primer_probe[3][1] and info[4] > float(sys.argv[3])/10:
                w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\tN\n'%(info[4]*100,info[5],info[6]))

f.close()
w.close()
