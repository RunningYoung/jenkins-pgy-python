# coding=utf-8

import time
import urllib2
import time
import json
import mimetypes
import os
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import subprocess
# from gittle import Gittle ## 需要手动安装 pip install Gittle

import json

#蒲公英应用上传地址
url = 'http://www.pgyer.com/apiv1/app/upload'
#蒲公英提供的 用户Key
uKey = 'xxxxxxxx' 
#蒲公英提供的 API Key
_api_key = 'xxxxxx'





# 运行时环境变量字典
environsDict = os.environ
print environsDict
#此次 jenkins 构建版本号
jenkins_build_number = environsDict['BUILD_ID']
print jenkins_build_number

jenkins_build_workspace = environsDict['JENKINS_HOME']

# /usr/bin/python /${WORKSPACE}/../pgy_jenkins.py

#git 本地地址 和 git 服务器地址配置
repo_path = '项目 本地地址'

repo_url = '项目远程git服务器地址'

#获取 ipa 文件路径
def get_ipa_file_path():
    #工作目录下面的 ipa 文件
    ipa_file_workspace_path = 'ipa包地址'
    # ipa_file_workspace_path = os.getcwd() + 'zuche' + '.ipa'
    
    if os.path.exists(ipa_file_workspace_path):
        return ipa_file_workspace_path

#ipa 文件路径
ipa_file_path = get_ipa_file_path()
print ipa_file_path

#获取 最后一次 提交git的信息
def getCommitInfo():
    #方法一 使用 python 库 前提是 当前分支 在服务器上存在
    # repo = Gittle(repo_path, origin_uri=repo_url)
    # commitInfo = repo.commit_info(start=0, end=1)
    # lastCommitInfo = commitInfo[0]
    #方法二 直接 cd 到 目录下 git log -1 打印commit 信息
    os.chdir(repo_path);
    lastCommitInfo = run_cmd('git log -1') 
    return lastCommitInfo

#处理 蒲公英 上传结果
def handle_resule(result):
    json_result = json.loads(result)
    if json_result['code'] is 0:
        print '*******文件上传成功****'
        print  json_result
        send_Email(json_result)

#发送邮件
def send_Email(json_result):
    print '*******开始发送邮件****'
    appName = json_result['data']['appName']
    appKey = json_result['data']['appKey']
    appVersion = json_result['data']['appVersion']
    appBuildVersion = json_result['data']['appBuildVersion']
    appShortcutUrl = json_result['data']['appShortcutUrl']
    #邮件接受者
    mail_receiver = ['xxxxx']
                        
    #根据不同邮箱配置 host，user，和pwd
    mail_host = 'smtp.qq.com'
    mail_port = 465
    mail_user = 'xxxxx@qq.com'
    mail_pwd = '密码key'
    mail_to = ','.join(mail_receiver)
    
    msg = MIMEMultipart()
    
    environsString = '<p><h3>本次打包相关信息</h3><p>'
    # environsString += '<p>ipa 包下载地址 : ' + 'wudizhi' + '<p>'
    environsString += '<p>蒲公英安装地址 : ' + 'http://www.pgyer.com/' + str(appShortcutUrl) + '<p><p><p><p>'
    # environsString += '<li><a href="itms-services://?action=download-manifest&url=https://ssl.pgyer.com/app/plist/' + str(appKey) + '"></a>点击直接安装</li>'
    environsString += '<p><h3>本次git提交相关信息</h3><p>'
    #获取git最后一次提交信息
    lastCommitInfo = getCommitInfo()
    # #提交人
    # committer = lastCommitInfo['committer']['raw']
    # #提交信息
    # description = lastCommitInfo['description']

    environsString += '<p>' + '<font color="red">' + lastCommitInfo + '</font>' + '<p>'
    # environsString += '<p>Description：' + '<font color="red">' + description + '</font>' + '<p>'

    message = environsString
    body = MIMEText(message, _subtype='html', _charset='utf-8')
    msg.attach(body)
    msg['To'] = mail_to
    msg['from'] = 'xxxx@qq.com'
    msg['subject'] = 'iOS APP 最新打包文件' 
    
    try:
        s = smtplib.SMTP()
        # 设置为调试模式，就是在会话过程中会有输出信息
        s.set_debuglevel(1)
        s.connect(mail_host)
        s.starttls()  # 创建 SSL 安全加密 链接

        s.login(mail_user, mail_pwd)
        
        s.sendmail(mail_user, mail_receiver, msg.as_string())
        s.close()
        
        print '*******邮件发送成功****'
    except Exception, e:
        print e

#############################################################

#蒲公英上传
#python 执行shell 命令
def run_cmd(cmd):  
    try:  
        import subprocess  
    except ImportError:  
        _, result_f, error_f = os.popen3(cmd)  
    else:  
        process = subprocess.Popen(cmd, shell = True,  
        stdout = subprocess.PIPE, stderr = subprocess.PIPE)  
        result_f, error_f = process.stdout, process.stderr  
  
    errors = error_f.read()  
    if errors:  pass  
    result_str = result_f.read().strip()  
    if result_f :   result_f.close()  
    if error_f  :    error_f.close()  
  
    return result_str 
    
print '*******开始文件上传****'
result = run_cmd('curl -F "file=@[ipa包路径]" -F "uKey=xxxx" -F "_api_key=xxxx" https://www.pgyer.com/apiv1/app/upload')
if result:
    print result
    handle_resule(result)