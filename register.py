#*************************************************************************
# The purpose of this script is to connect to the postgres db and create
# a new client record with a primary key of email and a randomly generated
# key for uid. uid is then returned to the client. If record already
# exists than a message is returned to the client that the record already
# exists.
#
# This script takes in the posted data from the app route called "register"
# and it returns the uid.
#*************************************************************************

import psycopg2
import random
import string

#*************************************************************************
# This class constructs an object with email address and usid attributes
# it uses the object to inform the db query and record insertion.
#*************************************************************************

class register:

    def __init__(self, email):
        self.email = email

    def id_generator(self, size=8, chars=string.ascii_uppercase + string.digits):
        uid = ''.join(random.choice(chars) for _ in range(size))
        self.uid = uid

    def doRegister(self):
        
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='' host='localhost' " + "password=''"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if the email address already exists in the db
            cursor.execute("""SELECT * FROM users WHERE email = %s;""",(self.email,))
            res = cursor.fetchone()         
            if res is None:
                #if it does not exist, add the email & a new uid.
                register.id_generator(self)
                cursor.execute("""INSERT INTO users (email, uid) VALUES (%s, %s);""",(self.email, self.uid))
                conn.commit()
                cursor.execute("""SELECT * FROM users;""")

                return self.uid
            else:
                return "record already exists."
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error

#*************************************************************************
#  The purpose of this section is for testing. It should be commented out
# for production.
#*************************************************************************

#email = "jordan@yaho0o.com"
#client = register(email)
#res = client.doRegister()
#print(res)
