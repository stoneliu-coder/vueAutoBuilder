#!/usr/bin/env python
# -*- coding: utf8 -*-

class Project:
    __svn_pre_path = u'http://svn.92hidc.com:8080/svn/Hishop.OmniChannel/trunk/src/HiShop.OmniChannel/src/Himall.Web';
    __work_dir = u'/home/debian/www/ocMallVueProjects/projects/';
    
 
    def __init__(self,svn_path):
        self.__svn_path = svn_path;
    
    def get_name(self):
        parts = self.__svn_path.split('/');
        return parts[len(parts)-1];

    def get_local_code_path(self):
        name = self.get_name();
        return self.__work_dir + name;

    def get_svn_path(self):
        return self.__svn_pre_path + self.__svn_path;

class Config:
    username ='liulei';
    password = 'rcTqGC7T';
    check_interval_seconds = 30;
    projects = [Project('/Areas/SellerAdmin/Cashier/src'),Project('/Areas/mpTempSet'),Project('/Areas/Mobile/wxshop')];
