#!/usr/bin/env python
# -*- coding: utf8 -*-
   
import pysvn
import time
import locale
import os
import shutil
import json
from env import *


def get_login(realm, username, may_save):
    return True, Config.username, Config.password, True

def get_local_version(project):
    entry = client.info(project.get_local_code_path());
    return entry.commit_revision.number;

def get_remote_need_build_version(project,current_version):
    #只获取提交日志中包含 “#build#” 关键字的版本号，该关键字表示该版本需要进行build
    keyword = '#build#'; 
    revision = pysvn.Revision(pysvn.opt_revision_kind.number,current_version);
    log_list = client.log(project.get_svn_path(),revision_end = revision);
    validRevision = current_version;
    
    for log in log_list:
        log_revision = log.revision.number;
        if keyword in log.message and log_revision > validRevision:
            print_log('check buildable version:' + str(log_revision) + ',log:' + log.message);
            validRevision = log_revision;
    return validRevision;

def svn_update(project,target_version):
    try:
        code_path = project.get_local_code_path();
        client.cleanup(code_path);
        client.revert(code_path,True);
        revision = pysvn.Revision(pysvn.opt_revision_kind.number,target_version);
        client.update(code_path,revision = revision);
        print_log('update ' + project.get_name() + ' successfully');
    except Exception,err:
        print_log('update ' + project.get_name() + ' error:' + str(err));

def print_log(msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S");
    print now,msg;

def check_need_update(project):
    current_version = get_local_version(project);
    latest_version = get_remote_need_build_version(project,current_version);#仅查询svn上需要build的最新版本号,防止无效获取并build
    return latest_version > current_version,latest_version;

def check_out(project):
    ret = client.checkout(project.get_svn_path(), project.get_local_code_path());

def ensure_checkout():
    for project in Config.projects:
        project_name = project.get_name();
        local_code_dir = project.get_local_code_path();
        exist = os.path.exists(local_code_dir);#判断是否存在该目录，因为如果存在目录则说明已经成功检出过
        if not exist:
            try:
                print_log('check out ' + project_name + ' start');
                check_out(project);
                print_log('check out ' + project_name + ' successfully');
            except Exception,err:
                print_log('check out ' + project_name + ' failed:' + str(err));
                shutil.rmtree(local_code_dir);#检出失败时，递归删除该目录，方便下次再次检出
                raise Exception,err;#重新抛出该异常，中断后续操作，保证只有在检出成功的情况下才继续进行        

def auto_update():
    while True:
        for project in Config.projects:
            project_name = project.get_name();
	    try:
                result = check_need_update(project);
                need_update = result[0];
                version = result[1];
                if(need_update):
                    print_log(project_name +' new version detected:' + str(version));
                    svn_update(project,version);
                    build(project);
                else:
                    print_log(project_name + ' no avaliable version!');
            except Exception,err:
                print_log(project_name + ' auto update error:' + str(err));
        time.sleep(Config.check_interval_seconds);

def build(project):
    project_name = project.get_name();
    try:
        print_log('build project ' + project.get_name() + ' start');
        print_log(os.popen('npm run build --prefix ' + project.get_local_code_path()).readlines());
        print_log('build project ' + project.get_name() + ' end');
    except Exception,err:
        print_log('build project ' + project_name + ' error: ' + str(err));


def setlocale():
    language_code, encoding = locale.getdefaultlocale()
    if language_code is None:
        language_code = 'en_US'
    if encoding is None:
        encoding = 'UTF-8'
    if encoding.lower() == 'utf':
        encoding = 'UTF-8'

    locale.setlocale( locale.LC_ALL, '%s.%s' % (language_code, encoding))

if "__main__" == __name__:
    setlocale();
    client = pysvn.Client();
    client.callback_get_login = get_login;
    ensure_checkout();
    # check_out();
    auto_update();
    # print_log(os.popen('ls').readlines());

