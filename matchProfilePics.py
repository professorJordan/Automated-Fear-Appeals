# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 12:37:53 2019

@author: jordan
"""

#*************************************************************************
# The purpose of this script is to determine if there are any matches
# between the image which is thought to be that of the user and the
# linkedIn profile pictures stored on the phone. We invoke classes and
# methods used to interface with Rekognition and make comparisons.
#*************************************************************************

import boto3, os, sys, glob, time, string, random
from botocore.exceptions import ClientError
from os import environ
import psycopg2

#*************************************************************************
# This class defines the basic mechanics for interacting with rekognition
#*************************************************************************


class Rekognition:

    def randomCollectionName():
        collectionName = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return(collectionName)

    def createCollection(collectionName):
        client=boto3.client('rekognition')
        client.create_collection(CollectionId=collectionName)
        return


    def deleteCollection(collectionName):
        client=boto3.client('rekognition')

        try:
            client.delete_collection(CollectionId=collectionName)

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print ('The collection ' + collectionName + ' was not found ')
            else:
                print ('Error other than Not Found occurred: ' + e.response['Error']['Message'])

        return



    def describeCollection(collectionName):
        client=boto3.client('rekognition')
        try:
            response=client.describe_collection(CollectionId=collectionName)
            faceCount = response['FaceCount']
            return[faceCount]
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print ('The collection ' + collectionName + ' was not found ')
            else:
                print ('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        return



    def addFace(collectionName, imagefile):

        photo = 'photo'
        client = boto3.client('rekognition')
        faceList = []

        with open(imagefile, 'rb') as image:
            response = client.index_faces(CollectionId=collectionName,
                Image={'Bytes': image.read()},
                ExternalImageId=photo,
                MaxFaces=100,
                QualityFilter="AUTO",
                DetectionAttributes=['ALL'])

        for faceRecord in response['FaceRecords']:
            res = faceRecord['Face']['FaceId']
            faceList.append((res, imagefile, 0))
        return[faceList]




    def listFaces(collectionName):
        maxResults=2
        tokens=True

        client=boto3.client('rekognition')
        response=client.list_faces(CollectionId=collectionName, MaxResults=maxResults)
        faceList = []

        while tokens:

            faces=response['Faces']


            for face in faces:
                faceID = face['FaceId']

                faceList.append(faceID)
            if 'NextToken' in response:
                nextToken=response['NextToken']
                response=client.list_faces(CollectionId=collectionName,
                                           NextToken=nextToken,MaxResults=maxResults)
            else:
                tokens=False
        return[faceList]



    def searchFaces(collectionName, FaceID):
        threshold = 50
        maxFaces=4096

        client=boto3.client('rekognition')


        response=client.search_faces(CollectionId=collectionName,
                                FaceId=FaceID,
                                FaceMatchThreshold=threshold,
                                MaxFaces=maxFaces)


        faceMatches=response['FaceMatches']
        return[faceMatches]




#*************************************************************************
# This class defines the procedures for setting up for comparison.
# You need to supply collectionName (no @ symbol), userID,
# and input_directory.
#*************************************************************************

class Preparation:

    def GetImgList(uid, selfiePic, socialMediaPlatform):

        #Determine path to profile pics
        baseDir = "/var/profileData/" + uid
        if socialMediaPlatform == 'linkedin':
            directory = baseDir + "/linkedin/profilePics/"
        if socialMediaPlatform == 'fb':
            directory = baseDir + "/fb/profilePics/"

        #sanity check for expected directory path
        if not os.path.exists(directory):
            print("Error: The following directory does not exist:", directory)
            return

        #load images into imgList
        List = glob.glob(directory+"*")

        #If there are no files located in imgList then halt.
        if List == '':
            print("no social media profile pictures located")
            return

        #create & load the img list
        imgList = []
        imgList.append(selfiePic)
        imgList.extend(List)
        #print("imgList:",imgList)
        return(imgList)


    def ImgListUpload(collectionName, imgList):
        faceList= []
        #upload each img in imgList to a collection named userID
        for img in imgList:
            res = Rekognition.addFace(collectionName, img)
            if res != [[]]:
                faceList.append(res[0][0])
        return(faceList)


#*************************************************************************
# This class provides the routines for comparing images in the collection
# in order to determine which face is the best match. The inputs include
# faceMatches and faceList. The output is the img name of the closest
# matching profile pic in the collection.
#*************************************************************************

class Comparison:


    def sortResults(faceMatches):
        flist = faceMatches
        from operator import itemgetter
        res=sorted(flist, key=itemgetter('Similarity'), reverse=True)
        #print("\nsorted faceMatches:",res)
        firstEntry = next(iter(res))
        #print("\nbest Match:",firstEntry)
        face = firstEntry["Face"]
        #print("\nface: ",face)
        faceID = face['FaceId']
        #print("\nfaceId:",faceID)
        return(faceID)

    def findPic(faceList, faceID):
        image = 0
        for face in faceList:
            #print("Does",face[0],"==",faceID,"?")
            if face[0] == faceID:
                image = face[1]
        return(image)

#*************************************************************************
# This class allows for communication with the database
#*************************************************************************

class CheckDB:

    #do we have a profile photo ID?
    def check4PhotoID(uid):
        try:
            #first, get db connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            #do query
            cursor.execute("""select photoid from identification where uid = %s;""",(uid,))
            res = cursor.fetchone()
            conn.close()
            return res
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error


    #Have we already made an ID?
    def check4socialPhoto(uid, socialMediaPlatform):
        try:
            #first, get db connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            #do query
            if socialMediaPlatform == 'linkedin':
                cursor.execute("""select linkedinphoto from socials where uid = %s;""",(uid,))
                res = cursor.fetchone()
            if socialMediaPlatform == 'fb':
                cursor.execute("""select fbphoto from socials where uid = %s;""",(uid,))
                res = cursor.fetchone()
            conn.close()
            if res is None:
                return "None"
            else:
                return res[0]

        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error

    def saveResults(uid, img, socialMediaPlatform):
        try:
            # get db connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()

            #write to demographics table

            #check to see if this should be an update or insert operation...
            cursor.execute("""select * from socials where uid = %s;""",(uid,))
            res = cursor.fetchone()

            #If there is no record there for this user
            if res == None:
                if socialMediaPlatform == 'linkedin':
                    cursor.execute("""INSERT INTO socials (linkedinphoto, uid) VALUES (%s, %s);""",\
                                   (img,uid))
                if socialMediaPlatform == 'fb':
                    cursor.execute("""INSERT INTO socials (fbphoto, uid) VALUES (%s, %s);""",\
                                   (img,uid))
            # if there is already a record for this user:
            if res != None:
                if socialMediaPlatform == 'linkedin':
                    cursor.execute("""UPDATE socials SET linkedinphoto = %s WHERE uid = %s;""",\
                                   (img,uid))
                if socialMediaPlatform == 'fb':
                    cursor.execute("""UPDATE socials SET fbphoto = %s WHERE uid = %s;;""",\
                                   (img,uid))
            conn.commit()
            conn.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)

#*************************************************************************
# The orchestrator manages the visual identification process.
#*************************************************************************

def checkForMatches(uid, socialMediaPlatform):

    # This is a sanity checks for UID
    if uid == '':
        print("Error: no userID provided.")
        return

    # checking to see if selfiePic has been assigned
    Pic = CheckDB.check4PhotoID(uid)
    if Pic == None:
        print("Error: no profile picture provided")
        return
    else:
        selfiePic = Pic[0]

    res2 = CheckDB.check4socialPhoto(uid, socialMediaPlatform)

    if (res2 == "None") or (res2 == None):


        #get random collection name
        collectionName = Rekognition.randomCollectionName()

        #create Collection
        Rekognition.createCollection(collectionName)
        #get Image List
        imgList = Preparation.GetImgList(uid, selfiePic, socialMediaPlatform)
        #print("image list:", imgList )
        #upload image list
        faceList = Preparation.ImgListUpload(collectionName, imgList)
        if not faceList:
            print("\nNo faces detected in any profile pictures")
            return
        #else:
        #print("\nFaceList:",faceList)

        #compare the selfie face against all the other faces in the collection.
        Matches = Rekognition.searchFaces(collectionName, faceList[0][0])
        faceMatches = Matches[0]
        #print("\nfaceMatches:",faceMatches)
        bestMatch = Comparison.sortResults(faceMatches)
        #print("\nbestMatch:",bestMatch)
        profilePic = Comparison.findPic(faceList, bestMatch)
        print("\nWe suspect this is the device owner's %s profile picture: %s"% (socialMediaPlatform, profilePic))
        #save result to database
        CheckDB.saveResults(uid, profilePic, socialMediaPlatform)
        #delete unncecessary face collection
        Rekognition.deleteCollection(collectionName)

        return profilePic
    else:
        print("%s photo identification already made: %s" % (socialMediaPlatform, res2))
        return

#*************************************************************************
# This stuff is for testing the preparation routines only.
#*************************************************************************

#userID = "1234567899"
#checkForMatches(userID)
