import sys

def info_deal(info):
    ac_num,an_num = info.split(';')
    vari_num = sum([int(i) for i in ac_num.strip('AC=').split(',')])
    total_num = int(an_num.strip('AN='))-1
    return vari_num,total_num,ac_num.strip('AC=')

def write_info(w,info,judg):
    w.write('\t'.join(info[:5]) + '\t%.2f%%\t%s\t%s\t%s\n'%(info[5]*100,info[6],info[7],judg))

check = 0
if len(sys.argv) == 5:
    check = 1

list_info = []
#           ORF（SA-XIN-F3) (SA-XIN-07F1) N(tdy-N-F1)  (SA-N-XIN-F1)
#               国内版         国际版         国际版         国内版
primer_probe = [[9093,9238],[12643,12736],[28626,28708],[28881,28979]] #扩增引物区间
#                                               ORF                                                                                 N
#                               china                           globe                                               globe                               china
probe_threhold = [[9093,9116],[9119,9143],[9217,9238], [12643,12666],[12691,12715],[12720,12736],  [28626,28645],[28654,28676],[28683,28708], [28881,28902],[28934,28953],[28958,28979]]

def prob_validation(site,gene):
    if gene == 'ORF':
        for list_site in probe_threhold[:3]:
            if list_site[0]<=site<=list_site[1]:
                return True
        return False
    elif gene == 'N':
        for list_site in probe_threhold[-3:]:
            if list_site[0]<=site<=list_site[1]:
                return True
        return False


if check:
    with open(sys.argv[1],'r') as f_fatovcf,open(sys.argv[4],'r') as f_coutry,open(sys.argv[2],'w') as w:
        dict_country = {}
        for line in f_coutry:
            line = [i.strip('"') for i in line.strip().split(',')]
            dict_country[line[0]] = ':'.join(line[2:4]) if '-' not in line[2:4] else '-'

        for line in f_fatovcf:
            if line.startswith('#'):continue
            line = line.strip().split('\t')
            vari_num, total_num,ac_num = info_deal(line[7])
            ratio = float(vari_num)/float(total_num)
            #有效数据：pos ID  mutation REF  ALT tario 
            mutation_info = dict_country[line[1]] if line[1] in dict_country else '-'
            effective_info = [line[1],line[2],mutation_info,line[3],line[4],ratio, ac_num,total_num]
            list_info.append(effective_info)

        w.write('位置\t突变(Genome)\t突变(Amino Acid)\tREF\tALT\t总突变比例\t突变计数\t序列总数\n')
        for info in list_info:
            #设置阈值
            if info[5] > float(sys.argv[3]):
                # if primer_probe[0][0]<= int(info[0]) <=primer_probe[0][1]:
                #     write_info(w,info,'ORF')
                # elif primer_probe[3][0]<= int(info[0]) <=primer_probe[3][1]:
                #     write_info(w,info,'N')
                # else:
                #     write_info(w,info,'')
                if prob_validation(int(info[0]),'ORF'):
                    write_info(w,info,'ORF')
                elif prob_validation(int(info[0]),'N'):
                    write_info(w,info,'N')
                else:
                    write_info(w,info,'')

            else:
                # if primer_probe[0][0]<= int(info[0]) <=primer_probe[0][1]  and info[5] > float(sys.argv[3])/10:
                if prob_validation(int(info[0]),'ORF')  and info[5] > float(sys.argv[3])/10:
                    write_info(w,info,'ORF')
                # elif primer_probe[3][0]<= int(info[0]) <=primer_probe[3][1] and info[5] > float(sys.argv[3])/10:
                elif prob_validation(int(info[0]),'N') and info[5] > float(sys.argv[3])/10:
                    write_info(w,info,'N')
else:
    with open(sys.argv[1],'r') as f,open(sys.argv[2],'w') as w:
        for line in f:
            if line.startswith('#'):continue
            line = line.strip().split('\t')
            #处理INFO
            vari_num, total_num,ac_num = info_deal(line[7])
            ratio = float(vari_num)/float(total_num)
            #有效数据：pos ID  REF  ALT tario 
            effective_info = [line[1],line[2],line[3],line[4],ratio, ac_num,total_num]
            list_info.append(effective_info)

        w.write('位置\t突变(Genome)\tREF\tALT\t总突变比例\t突变计数\t序列总数\n')
        for info in list_info:
            #设置阈值
            if info[4] > float(sys.argv[3]):
                # if primer_probe[0][0]<= int(info[0]) <=primer_probe[0][1]:
                if prob_validation(int(info[0]),'ORF'):
                    w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\tORF\n'%(info[4]*100,info[5],info[6]))
                # elif primer_probe[3][0]<= int(info[0]) <=primer_probe[3][1]:
                elif prob_validation(int(info[0]),'N'):
                    w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\tN\n'%(info[4]*100,info[5],info[6]))
                else:
                    w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\n'%(info[4]*100,info[5],info[6]))
            else:
                # if primer_probe[0][0]<= int(info[0]) <=primer_probe[0][1]  and info[4] > float(sys.argv[3])/10:
                if prob_validation(int(info[0]),'ORF')  and info[4] > float(sys.argv[3])/10:
                    w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\tORF\n'%(info[4]*100,info[5],info[6]))
                # elif primer_probe[3][0]<= int(info[0]) <=primer_probe[3][1] and info[4] > float(sys.argv[3])/10:
                elif prob_validation(int(info[0]),'N') and info[4] > float(sys.argv[3])/10:
                    w.write('\t'.join(info[:4]) + '\t%.2f%%\t%s\t%s\tN\n'%(info[4]*100,info[5],info[6]))
