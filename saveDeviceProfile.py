# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 13:11:16 2019

@author: jordan
"""

import psycopg2
from datetime import datetime

#*************************************************************************
# This app updates the database with the most recent security profile
# for a given user. 
#*************************************************************************

class profile:
    def __init__(self, uid, filename):
        self.uid = uid
        self.filename = filename
        self.file = "/var/profileData/" + self.uid + "/security/devprofiles" + self.filename
    
    
    #check to see if the uid is valid
    def hasAccount(self):
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if the uid already exists in the db
            cursor.execute("""SELECT uid FROM users WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()      
            conn.commit()
            if res is None:
                #if it does not exist, give the warning.
                return False
            else:
                return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error
    
    
    def doupdate(self):
        try: 
            #first, get connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            dt = datetime.now()
            cursor.execute("""INSERT INTO security (devprofile, datetime, uid) values (%s, %s, %s);""",(self.file,dt,self.uid))          
            conn.commit()
            return ("%s successfully saved" % (self.filename))                

        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error
        
    def updateDB(self):        
        res = profile.hasAccount(self)
        if res:
            res2 = profile.doupdate(self)
            return res2


                
            
        
        
