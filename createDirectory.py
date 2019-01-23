# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 12:33:08 2019

@author: jordan
"""

#*************************************************************************
# The purpose of this script is to create the directory system for each
# new, authenticated user. It creates all the necessary directories at
# once.
#*************************************************************************

import psycopg2
import os

#*************************************************************************
# This class performs the creation steps
#*************************************************************************

class create:

    def __init__(self, uid):
        self.uid = uid
        self.baseDir = "/var/profileData/" + self.uid
        self.selfieDir = self.baseDir + "/selfies"
        self.linkedinDir = self.baseDir + "/linkedin/profilePics"
        self.fbDir = self.baseDir + "/fb/profilePics"
        self.securityDir = self.baseDir + "/security/devprofiles"
        self.fearappealDir = self.baseDir + "/fearppeal/messages"


    def makedir(self):

        #before we make the folders we want to be sure the uid is valid.
        try:
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()

            cursor.execute("""SELECT uid FROM users WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()
            if res == None:
                return"invalid or missing uid"
            else:
                if not os.path.exists(self.baseDir):
                    os.makedirs(self.selfieDir)
                    os.makedirs(self.linkedinDir)
                    os.makedirs(self.fbDir)
                    os.makedirs(self.securityDir)
                    os.makedirs(self.fearappealDir)

        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error
        return


#*************************************************************************
# This is for testing purposes only. It should be commented out for
# production
#*************************************************************************

#uid = '1234567899'
#client = create(uid)
#client.makedir()
