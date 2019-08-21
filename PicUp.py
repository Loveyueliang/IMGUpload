#!/usr/bin/python
# -*- coding: utf-8 -*-
# upload images to https://sm.ms
# v1.2

import imghdr
import os
import os.path
import shutil
import sqlite3
import sys
from pprint import pprint

import requests

upload_url = "https://sm.ms/api/upload"
allow_suffix = ['jpeg', 'png', 'gif']
FILE_PATH = 'image'


class UploadIMG(object):
    def __init__(self, parent=None):
        self.sql = sqlite3.connect('sm.ms.db')
        self.sql_cur = self.sql.cursor()
        self.sql_cur.execute(
            "create table if not exists img_his(id integer primary key AUTOINCREMENT,filename varchar(128),width int(11),"
            "height int(11),storename varchar(128),size int(11),url varchar(128),delete_url varchar(128),page varchar(128),"
            "CreatedTime TIMESTAMP not null default (datetime('now', 'localtime')))")
        self.sql.commit()
        self.results = []

    def upload(self, args):
        files = []
        for arg in args:
            file = open(arg, 'rb')
            imgType = imghdr.what(file)
            if imgType in allow_suffix:
                filename = os.path.basename(arg)  # arg.split('/')[-1].split('\\')[-1]
                files.append({'smfile': (arg, file, 'image/jpeg')})
        data = {
            'ssl': True
        }

        for file in files:
            response = requests.post(upload_url, data=data, files=file)
            json = response.json()
            if json['success'] == True:
                json_data = json['data']
                pprint(json)
                self.sql_cur.execute("INSERT INTO img_his(filename,width,height,storename,size,url,delete_url,page)"
                                     "VALUES ('%s',%d,%d,'%s',%d,'%s','%s','%s')" % (
                                         json_data["filename"], json_data["width"], json_data["height"],
                                         json_data["storename"], json_data["size"], json_data["url"],
                                         json_data['delete'],
                                         json_data['page']))

                if not os.path.exists(FILE_PATH):
                    os.makedirs(FILE_PATH)
                print(file['smfile'][0])
                shutil.copy(file['smfile'][0], os.path.abspath(FILE_PATH))
                self.results.append(json_data['url'])

            elif json['message'] == 'Image upload repeated limit.':
                res = requests.get('https://sm.ms/api/list').json()
                print('上传失败：该文件已存在，下面为一小时内请求历史：')
                pprint(res)
            else:
                pprint(json)

    def updateResultEdit(self):
        self.sql.commit()
        self.sql.close()


if __name__ == '__main__':
    args = sys.argv
    os.chdir(os.path.dirname(os.path.abspath(args[0])))
    if len(args) == 1:
        print("Usage: Usage:uPic.py imagePath")
    elif args[1] == "-h":
        res = requests.get('https://sm.ms/api/list').json()
        pprint(res)
    else:
        upload_img = UploadIMG()
        upload_img.upload(args)
        upload_img.updateResultEdit()

