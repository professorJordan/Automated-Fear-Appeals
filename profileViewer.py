# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 11:38:58 2019

@author: jordan
"""

#*************************************************************************
# The purpose of this script is to present the complete, assembled profile
# for a given user.
#*************************************************************************


import psycopg2, sys

#from botocore.exceptions import ClientError

#*************************************************************************
# This class supports communication with the db
#*************************************************************************

class buildProfile:
    def __init__(self,uid):
        self.uid = uid
        self.email = None
        self.race = None
        self.age = None
        self.gender = None
        self.fname = None
        self.lname = None
        self.photoid = None
        self.linkedinphoto = None
        self.linkedinaccount = None
        self.fbphoto = None
        self.fbaccount = None
        self.devprofile = None
        self.fearappeal = None




    def getUsersData(self):
        try:
            #first, get db connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()

            #do users query
            cursor.execute("""select email from users where uid = %s;""",(self.uid,))
            res = cursor.fetchone()
            if res != None:
                self.email = res[0]

            #do demographics query
            cursor.execute("""select race, age, gender from demographics where\
                           uid = %s;""",(self.uid,))
            res = cursor.fetchone()
            if res != None:
                self.race = res[0]
                self.age = res[1]
                self.gender = res[2]

            #do identification query
            cursor.execute("""select fname, lname, photoid from identification where\
                           uid = %s;""",(self.uid,))
            res = cursor.fetchone()
            if res != None:
                 self.fname = res[0]
                 self.lname = res[1]
                 self.photoid = res[2]

            #do socials query
            cursor.execute("""select linkedinphoto, linkedinaccount, fbphoto, fbaccount\
                           from socials where uid = %s;""",(self.uid,))
            res = cursor.fetchone()
            if res != None:
                self.linkedinphoto = res[0]
                self.linkedinaccount = res[1]
                self.fbphoto = res[2]
                self.fbaccount = res[3]

            #do security query
            cursor.execute("""select devprofile from security where uid = %s order by datetime desc;""",(self.uid,))
            res = cursor.fetchone()
            if res != None:
                self.devprofile = res[0]

            #do fear appeals query
            cursor.execute("""select message from fearappeal where uid = %s order by datetime desc;""",(self.uid,))
            res = cursor.fetchone()
            if res != None:
                self.fearappeal = res[0]

            conn.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error

    def makeReport(self):
        print("\n\n********************************************************************************")
        print("report for user %s\nemail: %s" % (self.uid,self.email))
        print("age: %s\nethnicity: %s\ngender: %s" % (self.age,self.race,self.gender))
        print("first name: %s\nlast name: %s\nphotoid: %s" % (self.fname,self.lname,self.photoid))
        print("linkedIn Photo: %s\nLinkedin Account: %s\nFB photo: %s\nFB account: %s" % (self.linkedinphoto,self.linkedinaccount,self.fbphoto, self.fbaccount))
        print("Most recent device profile report: %s" % (self.devprofile))
        print("Most recent fear appeal: %s" % (self.fearappeal))
        print("********************************************************************************\n\n")

#*************************************************************************
# This stuff is for testing the preparation routines only.
#*************************************************************************

uid = sys.argv[1]
client = buildProfile(uid)
client.getUsersData()
client.makeReport()
