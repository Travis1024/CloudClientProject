#encoding:utf-8

import os
import configparser

#获取config配置文件
def getConfig(section, key):
    config = configparser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + '/SecretKey/para.conf'
    config.read(path)
    return config.get(section, key)
