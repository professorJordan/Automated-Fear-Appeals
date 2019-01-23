# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 13:43:35 2019

@author: jordan
"""
import requests

url = 'http://...:5000/deviceprofile'

data = {'uid':'X7TWVZHT','file':open('test.txt','rb'),'submit':'Upload'}

files = [('file', open('test.txt', 'rb'))]

r = requests.post(url, data=data, files = files)

print(r.content)
