from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash, session, send_from_directory
from werkzeug import secure_filename
from concurrent.futures import ThreadPoolExecutor
# from web_script.Cov_mutation_deal import Cov
from glob import glob
import os,datetime,re
from copy import deepcopy
UPLOAD_FOLDER = '/project/user/chenqi/test/test_nothing/file_save'
# 创建线程池执行器
executor = ThreadPoolExecutor(2)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FILE'] = '/project/user/chenqi/test/test_nothing/workflow'
#限制上传文件大小为16M，当超出16M大小会抛出RequestEntityTooLarge异常
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'some_secret'
#设置新冠探针采用的是那一版  圣湘新冠：SA-XIN-F/R/P3 + SA-N-XIN-F/R/P1  圣湘新冠甲乙流：SA-XIN-F/R/P3 + tdy-N-F/R/P1 Sansure：SA-XIN-07F/R/P1 + tdy-N-F/R/P1 默认"圣湘新冠"
app.config['prob_chose'] = 'value1'

#判断上传文件拓展名是否在允许拓展列表内
ALLOWED_EXTENSIONS = set(['fasta','csv'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # session['username'] = request.form['username']
        # return redirect(url_for('index'))
        if request.form['username'] != 'admin' or \
           request.form['password'] != 'secret':
            error = 'Invalid credentials'
        else:
            flash(u'Invalid password provided', 'error')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

app.config['upload_type'] = {}
@app.route('/upload_file',methods=['GET', 'POST'])
def upload_file():
    kinds = ''
    dict_filenames = {}

    if request.method == 'POST':
        # file = request.files['file']
        for file in request.files.getlist('file'):
            if file and allowed_file(file.filename):
                #secure_filename不支持中文传输
                filename = secure_filename(file.filename)
                kinds = info_get(kinds,filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER'] + '/%s'%kinds):
                    os.mkdir(app.config['UPLOAD_FOLDER'] + '/%s'%kinds)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/%s'%kinds, filename))
                
                if kinds:
                    if kinds not in dict_filenames:dict_filenames[kinds] = []
                    dict_filenames[kinds].append(filename)
                    kinds = ''
        app.config['upload_type'] = deepcopy(dict_filenames)
    elif request.method == 'GET':
        dict_filenames = deepcopy(app.config['upload_type'])
        if request.values.get('select'):
            app.config['prob_chose'] = request.values.get('select')
        else:
            app.config['prob_chose'] = 'value1'
    return render_template('upload.html',upload_files=dict_filenames)

def info_get(kinds,sequnce_file):
    if sequnce_file.endswith('fasta'):
        kinds = sequnce_file.rsplit('.fasta')[0]
    elif sequnce_file.endswith('csv'):
        kinds = sequnce_file.rsplit('.csv')[0]
    return kinds

def long_task(fasta_num,fasta_file,csv_file,prob_chose):
    workflow_dir = '/project/user/chenqi/test/test_nothing/workflow'
    script_dir = '/project/user/chenqi/test/test_nothing/novel_coron_script'
    if fasta_num > 100:
        os.system('cd %s && sh %s/cov_19_mutation_samtools_call.sh %s 10 %s %s'%(workflow_dir, script_dir, fasta_file,csv_file, prob_chose))
    else:
        os.system('cd %s && sh %s/cov_19_mutation_fatovcf_new_model.sh %s %s %s'%(workflow_dir, script_dir, fasta_file,csv_file, prob_chose))

def check_file_exists(filename):
    # total_info = []
    fasta_file,csv_file = '%s/%s/%s.fasta'%(app.config['UPLOAD_FOLDER'],filename,filename), '%s/%s/%s.csv'%(app.config['UPLOAD_FOLDER'],filename,filename)
    if os.path.exists(fasta_file) and os.path.exists(csv_file):
        fasta_num = int(os.popen('grep "^>" %s|wc -l'%fasta_file).readlines()[0].strip())
        file_line = '\t'.join(os.popen('sh /project/user/chenqi/test/test_nothing/test.sh %s'%fasta_file).readlines())
        if app.config['prob_chose'] == 'value1':
            executor.submit(long_task, fasta_num,fasta_file,csv_file,'C')
        elif app.config['prob_chose'] == 'value2':
            executor.submit(long_task, fasta_num,fasta_file,csv_file,'G')
        elif app.config['prob_chose'] == 'value3':
            executor.submit(long_task, fasta_num,fasta_file,csv_file,'S')
    else:
        total_info = 'please check %s fasta or csv file'%filename
    # return total_info

def file_name_check(list_result_file=None):
    filename = []
    for docx in glob(app.config['RESULT_FILE'] + '/*/*.docx'):
        list_docx = docx.split('/')
        if list_result_file !=None:
            list_result_file.append(['/'.join(list_docx[-2:]),[list_docx[-2],list_docx[-1]]])
        if list_docx[-2] not in filename:
            filename.append(list_docx[-2])
    if list_result_file:
        return filename,list_result_file
    else:
        return filename

def check_final_file_new(type_name):
    result_dir = os.path.join(app.config['RESULT_FILE'],type_name)
    result_files = []
    for i in glob(result_dir + '/*.docx'):
        result_files.append(['/'.join(i.strip().split('/')[-2:]),[type_name,i.strip().split('/')[-1]]])
        break
    if result_files:
        return result_files[0]
    else:
        return False


@app.route('/info_show/',methods=['GET', 'POST'])
@app.route('/info_show/<filename>',methods=['GET', 'POST'])
def info_show(filename=None):
    try:
        filename = eval(filename)
    except:
        pass
    list_result_file = []
    if filename:
        if type(filename) == dict:
            for each_name in filename.keys():
                type_old_docx = glob(app.config['RESULT_FILE'] + '/%s/*docx'%each_name)
                if type_old_docx:
                    for i in type_old_docx:
                        os.remove(i.strip())
                check_file_exists(each_name)
            filename = list(filename.keys())
        elif type(filename) == list and filename[1] == 'download':
            filename = [filename[0]]
        else:
            type_old_docx = glob(app.config['RESULT_FILE'] + '/%s/*docx'%filename)
            if type_old_docx:
                for i in type_old_docx:
                    os.remove(i.strip())
            check_file_exists(filename)
            filename = [filename]
        for i in filename:
            check_rec = check_final_file_new(i)
            if check_rec:
                list_result_file.append(check_rec)
            else:
                list_result_file.append([i,[]])

        return render_template('info_show.html',type_name=filename,result_files=list_result_file,check_return=0)
    else:
        filename,list_result_file = file_name_check(list_result_file)

    #list_result_file: [result_file,[type_name,file_name]],['/project/user/chenqi/test/test_nothing/workflow/A.28/附件2 评价报告表_A.28_2021-7-16.docx',['A.28','附件2 评价报告表_A.28_2021-7-16.docx']]
    #需要提前检查传输的文件是否包括同一珠系的fasta和csv文件
    if request.method == 'POST':
        type_list = re.split(r',|、|\n',request.form['type_cov'].strip())
        list_result_file = []
        # print(request.form['type_cov'])
        for type_name in type_list:
            check_rec = check_final_file_new(type_name)
            if check_rec:
                list_result_file.append(check_rec)
            else:
                list_result_file.append([type_name,[]])
    return render_template('info_show.html',type_name=filename,result_files=list_result_file,check_return=1)

@app.route('/download_file/<path:file>',methods=['GET','POST'])
def download_file(file):
    # return send_from_directory(app.config['RESULT_FILE'],file,as_attachment=True)
    return send_from_directory(app.config['RESULT_FILE'],file)

def read_mut(file):
    list_info = []
    with open(file,'r',encoding='utf-8') as f:
        for line in f:
            if line.startswith('位置'):continue
            list_info.append(line.strip().split('\t'))
    return list_info

def conclusion_get(list_info,total_num):
    conclusion_list = [[],[]]
    for info in list_info:
        if len(info) >8:
            word, mut_num = '', 0
            for i in range(len(info[1].split(','))):
                word += '%s共%s条,'%(info[1].split(',')[i],info[6].split(',')[i])
                mut_num += int(info[6].split(',')[i])

            word += '其中%s条没有发生突变,还有%s条未覆盖;'%(int(info[7])-mut_num,total_num-int(info[7]))
            if info[-1] == 'ORF':
                conclusion_list[0].append(word)
            elif info[-1] == 'N':
                conclusion_list[1].append(word)
    conclusion_word = 'ORF1ab基因设计的引物探针区域发生%s个突变（%s）。'%(len(conclusion_list[0]),''.join(conclusion_list[0])) if len(conclusion_list[0]) != 0 else 'ORF1ab基因设计的引物探针区域未发生突变。'
    conclusion_word += 'N基因设计的引物探针区域发生%s个突变（%s）。'%(len(conclusion_list[1]),''.join(conclusion_list[1])) if len(conclusion_list[1]) !=0 else 'N基因设计的引物探针区域未发生突变。'
    return conclusion_word

def update_time(type_name):
    for i in glob(app.config['RESULT_FILE']+'/%s/*.docx'%type_name):
        # current_update = i.strip().rstrip('.docx').split('_')[-1].replace('-','.')
        current_update = i.strip().split('/')[-1].rstrip('.docx').split('_')[2].replace('-','.')
        current_file = '/'.join(i.strip().split('/')[-2:])
        break
    return current_update,current_file

@app.route('/result/',methods=['GET','POST'])
@app.route('/result/<type_name>',methods=['GET','POST'])
def result(type_name=None):
    list_info, fasta_num, conclusion_word, current_update, current_file, pic = [], '','', '', '', ''
    filenames = file_name_check()

    type_name = request.form['type_cov'] if request.method == 'POST' else type_name
    if request.method == 'POST' or type_name:
        mutation_file = app.config['RESULT_FILE'] + '/%s/%s.txt'%(type_name,type_name)
        list_info = read_mut(mutation_file)
        fasta_num = int(os.popen('grep "^>" %s/%s/%s.fasta|wc -l'%(app.config['UPLOAD_FOLDER'],type_name,type_name)).readlines()[0].strip())
        conclusion_word = conclusion_get(list_info,fasta_num)
        current_update,current_file = update_time(type_name)
    return render_template('result.html',mutation_list=list_info,type_names=filenames,type=type_name,type_fasta_num=fasta_num,conclusion=conclusion_word,time=current_update,docx_file=current_file)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
