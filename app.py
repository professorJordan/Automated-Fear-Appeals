# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 12:32:17 2019

@author: jordan
"""

#*************************************************************************
# This is the API for the profiler system. It has three major taskes:
#
# (1) registration. It allows new apps to register themselves. The app
#     sends the collected user email and receives a user ID (uid) in
#     response. This ID must be used in subsequent communications.
#
# (2) data ingestion. It accepts selfies for the visual Identification
#     and demographics stages. It accepts locally-stored social media
#     profile pictures. It accepts phone sensor data. It accepts device
#     security profile data.
#
# (3) It provides confirmation messages to devices. These messages are
#     sent in direct response to user uploads. Fear Appeal messages use
#     a different conduit.
#*************************************************************************

import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename




app = Flask(__name__)

# These definitions and data are applicable to all flask apps.
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#*************************************************************************
# This app provides a point of initial registration for the apps. The
# app user submits email address and the app receives a uid in response.
#*************************************************************************

@app.route('/register', methods=['GET', 'POST'])
def upload_email():
    if request.method == 'POST':

        #check if the post request has the user ID
        email = request.form.get('email')
        if email == '':
            print("Email address blank")
            return "Email address blank"
        elif 'email' not in request.form:
            print('Email object not submitted')
            return 'Email object not submitted'
        else:
            import register
            client = register.register(email)
            uid = client.doRegister()
            print(uid)
            from createDirectory import create
            client = create(uid)
            client.makedir()
            return 'email address submitted'
    return("complete")
        # This is part where we sort out the destination directory



#*************************************************************************
# This app provides an ingestion conduit for saving selfie images to the
# appropriate locations in the file structure. It begins the pipeline for
# for the VizID and Demographics work determination
#*************************************************************************

@app.route('/visual', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        #check if the post request has the user ID
        uid = request.form.get('uid')
        if uid == '':
            print("no UID Supplied")
            return redirect(request.url)

        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        from createDirectory import create
        client = create(uid)
        client.makedir()

        # This is part where we sort out the destination directory
        baseDir = "/var/profileData/" + uid
        selfieDir = baseDir + "/selfies"
        UPLOAD_FOLDER = selfieDir

        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        # This is the process of checking files.
        counter = 0
        for file in request.files.getlist('file'):
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)

        # This is the process of storing files to the right location
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                counter +=1

        # if no files are stored then quit.
        if counter == 0:
            print("No uploaded images to analyze")
            return

        # if files are stored then begin processing them.
        from vizID import identify
        res = identify(uid)
        if res != None:
            from getDemographics import Demographics
            Demographics.getDemographics(uid)
        return ("upload completed")

    return("complete")


#*************************************************************************
# The purpose of this flask app is to provide an ingestion point for
# social media profile photos. These photos are stored in the appropriate
# locations. It begins the pipeline for the social network analysis
#*************************************************************************

@app.route('/social', methods=['GET', 'POST'])
def upload_img():
    if request.method == 'POST':

        #check if the post request has the user ID
        uid = request.form.get('uid')
        if uid == '':
            print("no UID Supplied")
            return redirect(request.url)

        #check if the post indicates social media platform type
        socialMediaPlatform = request.form.get('platform')
        if socialMediaPlatform == '':
            print("no social media platform supplied")
            return redirect(request.url)
        elif (socialMediaPlatform != 'linkedin') and (socialMediaPlatform != 'fb'):
            print("unrecognized social media platform")
            return redirect(request.url)

        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        from createDirectory import create
        client = create(uid)
        client.makedir()

        # This is part where we sort out the destination directory
        baseDir = "/var/profileData/" + uid
        socialDir = baseDir + "/" + socialMediaPlatform
        profilePics = socialDir + "/profilePics"
        UPLOAD_FOLDER = profilePics

        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


        # This is the process of storing files to the right location
        counter = 0
        for file in request.files.getlist('file'):
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                counter +=1

        # Additional sanity check. If no files were successfully stored then quit
        if counter == 0:
            print("No uploaded images to analyze")
            return


        # This is the call to action. it will need to be amended later.
        #from profiler_prod import profile
        #profile(UID)
        print("upload Complete")
        from matchProfilePics import checkForMatches
        checkForMatches(uid, socialMediaPlatform)

    return("complete")


#*************************************************************************
# This app provides an ingestion conduit for saving security profiles 
# to the server
#*************************************************************************

@app.route('/deviceprofile', methods=['GET', 'POST'])
def upload_securityprofile():
    if request.method == 'POST':

        #check if the post request has the user ID
        uid = request.form.get('uid')
        if uid == '':
            print("no UID Supplied")
            return redirect(request.url)
      
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        from createDirectory import create
        client = create(uid)
        client.makedir()

        # This is part where we sort out the destination directory
        baseDir = "/var/profileData/" + uid
        profilesDir = baseDir + "/security/devprofiles"
        UPLOAD_FOLDER = profilesDir

        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        # This is the process of checking files.
        counter = 0
        for file in request.files.getlist('file'):
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)

        # This is the process of storing files to the right location
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                counter +=1
                
        # Additional sanity check. If no files were successfully stored then quit
        if counter == 0:
            print("No uploaded images to analyze")
            return("No uploaded images to analyze")
        else:
            print("upload complete")
            from saveDeviceProfile import profile
            client = profile(uid, filename)
            res = client.updateDB()
            print(res)
            return res
    return("complete")

# to run this code:
# export FLASK_APP=app.py
# flask run --host=0.0.0.0
