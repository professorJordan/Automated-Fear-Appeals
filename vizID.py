# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 12:35:34 2019

@author: jordan
"""

import boto3, os, sys, glob, time, string, random
from botocore.exceptions import ClientError
from os import environ
import psycopg2

#*************************************************************************
# This class defines the basic mechanics for interacting with  rekognition
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
        faceList = []
        numMatches = 0

        client=boto3.client('rekognition')


        response=client.search_faces(CollectionId=collectionName,
                                FaceId=FaceID,
                                FaceMatchThreshold=threshold,
                                MaxFaces=maxFaces)


        faceMatches=response['FaceMatches']

        for match in faceMatches:
            face = match['Face']['FaceId']
            faceList.append(face)
            numMatches +=1
        return[numMatches]




#*************************************************************************
# This class defines the procedures for setting up for comparison.
# You need to supply collectionName (no @ symbol), userID,
# and input_directory.
#*************************************************************************

class Preparation:

    def GetImgList(userID):
        input_directory = "/var/profileData/"
        directory = input_directory + "/" + userID + "/selfies/"
        imgList = glob.glob(directory+"*")
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
# This class allows for communication with the database
#*************************************************************************

class CheckDB:
    def determineNeed(uid):
        try:
            #first, get db connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            #do query
            cursor.execute("""select * from identification where uid = %s;""",(uid,))
            res = cursor.fetchone()
            conn.close()
            return res
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error

    def saveResults(uid, img):
        try:
            # get db connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            #write to demographics table
            cursor.execute("""INSERT INTO identification (photoid, uid) VALUES (%s, %s);""",\
                           (img,uid))
            conn.commit()
            conn.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)


#*************************************************************************
# This class provides the routines for comparing images in the collection
# in order to determine which face is seen the most. The inputs include
# collectionName and the faceList. The output is the img name of the most
# frequent face in the collection.
#*************************************************************************

class Comparison:

    def compareFaces(collectionName, faceList):
        faces = []
        for face in faceList:
            faceID = face[0]
            image = face[1]
            numMatches = Rekognition.searchFaces(collectionName,faceID)
            #print("\nnumber of matches for",faceID,image,":",numMatches)
            faces.append((faceID,image,numMatches))
            time.sleep(.500)
        return[faces]


    def sortResults(faceList):
        sorted_faceList = faceList[0]
        from operator import itemgetter
        res=sorted(sorted_faceList, key=itemgetter(2), reverse=True)
        firstEntry = next(iter(res))
        mostCommon = firstEntry[1]
        return mostCommon


#*************************************************************************
# The orchestrator manages the visual identification process.
#*************************************************************************

def identify(uid):

    #check to see if photo ID has already been made
    res = CheckDB.determineNeed(uid)
    if res == None:
        #get random collection name
        collectionName = Rekognition.randomCollectionName()
        #create Collection
        Rekognition.createCollection(collectionName)
        #get Image List
        imgList = Preparation.GetImgList(uid)
        if not imgList:
            print("/nno self photos available for analysis")
            return "no self photos available for analysis"
        #upload image list
        faceList = Preparation.ImgListUpload(collectionName, imgList)
        if not faceList:
           print("\nNo faces in any selfie pictures")
           return "No faces in any selfie pictures"
        #compare faces & find most common face
        scoredFaceList = Comparison.compareFaces(collectionName, faceList)
        mostCommon = Comparison.sortResults(scoredFaceList)
        #save result to database
        CheckDB.saveResults(uid,mostCommon)
        #delete unncecessary face collection
        Rekognition.deleteCollection(collectionName)
        print(mostCommon)
        return mostCommon
    else:
        print("an identity has already been made")

#*************************************************************************
# This stuff is for testing the preparation routines only.
#*************************************************************************

#userID = "123456788"

#identify(userID)
