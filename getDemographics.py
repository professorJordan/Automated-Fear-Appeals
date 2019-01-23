# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 12:36:59 2019

@author: jordan
"""

import requests
import os
import shutil
import psycopg2

#*****************************************************************
# The purpose of this class is to support copying the selected
# image to web root and determining the updated path.
#*****************************************************************

class Preparation:


    def getImageName(img):
        #gets just the file name
        imgName = os.path.basename(img)
        return(imgName)


    def getinternalURL(imgName):
        webRoot="/var/www/html/"
        #creates local file path to webroot
        internalURL = webRoot+imgName
        return(internalURL)


    def copyToWebRoot(internalURL, img):
        webRoot="/var/www/html/"
        #if not exists, copy img to the web root
        if os.path.isfile(internalURL):
            #print("file already exists in ",webRoot)
            return
        else:
            shutil.copy2(img, webRoot)
            #print("file copied to",webRoot)
            return


    def getExternalURL(imgName):
        ServerAddress="http://.../"
        #create externally-accessable img URL
        externalURL = ServerAddress+imgName
        return(externalURL)

    #This function performs the task of ensuring an external link
    def getSharableImage(img):

        imgName = Preparation.getImageName(img)

        internalURL = Preparation.getinternalURL(imgName)


        #This relies on ubuntu addressing. need to test & use
        #in python machine
        Preparation.copyToWebRoot(internalURL, img)
        externalURL = Preparation.getExternalURL(imgName)

        return externalURL

    def removeCopy(img):
        imgName = Preparation.getImageName(img)
        webRoot="/var/www/html/"
        sharedFile = webRoot+imgName
        os.remove(sharedFile)
        return

#*****************************************************************
# The purpose of thisclass is to support querying to the db
#*****************************************************************

class CheckDB:
    def saveResults(uid, actualDemographics):
        try:
            #first, unpack actualDemographics into separate variables
            gender = actualDemographics[0]
            ethnicity = actualDemographics[1]
            age = actualDemographics[2]
            #now, get db connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            #write to demographics table
            cursor.execute("""INSERT INTO demographics (gender,age,race, uid) VALUES (%s, %s, %s, %s);""",\
                           (gender, age, ethnicity,uid))
            conn.commit()
            conn.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error

    def determineNeed(uid):
        try:
            #first, get db connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            #write to demographics table
            cursor.execute("""select * from demographics where uid = %s;""",(uid,))
            res = cursor.fetchone()
            conn.close()
            return res
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error

    def isThereAPic(uid):
        try:
            #first, get db connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            #write to demographics table
            cursor.execute("""select photoid from identification where uid = %s;""",(uid,))
            res = cursor.fetchone()
            conn.close()
            return res

        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error


#*****************************************************************
#For this function you need to pass in the URL to a portrait and
#you receive a json text file in response.
#*****************************************************************

class Demographics:
    def processImage(image_url):
        http_url = 'https://api-us.faceplusplus.com/facepp/v3/detect'
        key = ""
        secret = ""
        attributes="gender,age,ethnicity"
        url = image_url

        json_resp = requests.post(http_url,
              data = {
                  'api_key': key,
                  'api_secret': secret,
                  'image_url': url,
                  'return_attributes': attributes
              }
        )
        demographicData = json_resp.json()
        return(demographicData)

    def parseResults(demographicData):
        gender = (demographicData["faces"][0]["attributes"]["gender"]["value"])
        ethnicity = (demographicData["faces"][0]["attributes"]["ethnicity"]["value"])
        age = (demographicData["faces"][0]["attributes"]["age"]["value"])
        return [gender, ethnicity, age]


    #This is the process orchestration function
    def getDemographics(uid):
        #If there is no record already
        res = CheckDB.determineNeed(uid)
        if (res == None):
            #And if there is an identification picture available then proceed
            img2 = CheckDB.isThereAPic(uid)
            if (img2 != None):
                img = img2[0]
                if (os.path.basename(img)):
                    externalURL = Preparation.getSharableImage(img)
                    demographicData = Demographics.processImage(externalURL)
                    actualDemographics = Demographics.parseResults(demographicData)
                    CheckDB.saveResults(uid, actualDemographics)
                    Preparation.removeCopy(img)
                    print (actualDemographics)
                else:
                    print("no profile picture available at specified location: ",img)
            else:
                print("no profile picture available at specified location",img2)
        else:
            print("demographics already collected")


#*****************************************************************
#The code below is an example of how to use the function
#*****************************************************************

#uid = "123456789"
#Demographics.getDemographics(uid)
