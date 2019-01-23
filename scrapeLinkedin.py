#*************************************************************************
# The purpose of this script is to extract the important information from
# a downloaded linkedin html script.
#*************************************************************************

import re, psycopg2, os.path

#*************************************************************************
# Class extraction is the only class in the script. It should be called
# and decorated with a uid. A client should be assigned the value of the
# decorated class instance. The orchestrator calls the methods for 
# extracting and saving data.
#*************************************************************************

class extraction:

    def __init__(self, uid):
        self.uid = uid
        self.file = None
        self.fname = None
        self.lname = None
        self.occupation = None
        self.industry = None
        self.location = None
        self.workHistory = []
        self.positionHistory = []
        self.employmentHistory = []

#*************************************************************************
# The whole script depends on whether we can access a file. This routine
# gets the name of the downloaded linkedin file associated with the script
# if there is one. If there is a file, it confirms that the file is 
# where we expect it to be and it is openable. 
#*************************************************************************
    
    def getFile(self):
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if record already exists in the db
            cursor.execute("""SELECT linkedinfile FROM socials WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()
            conn.close()
            if res is None:                
                return  "no record of a local linkedin file"
            else:
                filename = res[0]
                baseDir = "/var/profileData/" + self.uid                
                file = baseDir + "/linkedin/" + filename
                
                #Check to see if file exists 
                if os.path.isfile(file):
                    self.file = file
                else:
                    return "The db has a record of a file called %s for user %s. But the file either doesn't exist or is not openable" % (file, self.uid)
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error


#*************************************************************************
# Because name is so important, we have two methods for ensuring we have
# the right values for the user. 
#*************************************************************************
    def getName(self):
        preamble = "/voyager/api/identity/profiles/"
        conclusion = "-"
        with open(self.file, encoding="utf8") as f:
                contents = f.read()

                my_regex = r'(?<=' + re.escape(preamble) + ')\w+'
                res = re.search(my_regex, contents)
                a = res.group(0)
                b = a.replace('&&',"")
                fname1 = b
                #print(fname1)

                searchName = fname1 + conclusion
                my_regex = r'(?<=' + re.escape(searchName) + ')\w+'
                res = re.search(my_regex, contents)
                lname1 = res.group(0)
               # print(lname1)

                m = re.findall('VolunteerExperienceView(.+?)deletedFields', contents)
                for n in m:

                    a = n #for first name
                    b = n #for last name

                    c = re.search('firstName(.+?)lastName',a)
                    if c:
                        d = c.group(0)
                        e = d.replace('&amp;',"")
                        f = e.replace('quot;',"")
                        g = f.replace('firstName',"")
                        h = g.replace('lastName',"")
                        i = h.replace(':',"")
                        x = i.replace(',',"")
                        fname2 = x.replace('&&',"")
                        #print("fname2:",fname2)
                        self.fname = fname2

                    j = re.search('lastName(.+?)$',b)
                    if j:
                        k = j.group(0)
                        l = k.replace('&amp;',"")
                        m = l.replace('quot;',"")
                        n = m.replace('lname',"")
                        o = n.replace('lastName',"")
                        p = o.replace(':',"")
                        q = p.replace(',',"")
                        y = q.replace('$',"")
                        lname2 = y.replace('&&',"")
                        #print("lname2:",lname2)
                        self.lname = lname2

                    if not fname2:
                        self.fname = fname1

                    if not lname2:
                        self.lname = lname1

                    print("name is: ", self.fname, self.lname)

    def getCurrentPosition(self):
        with open(self.file, encoding="utf8") as f:
                contents = f.read()
                #print(contents)
                m = re.search('headline(.+?)deletedFields', contents)
                if m:
                    r = m.group(0)
                    a = r.replace('headline&amp;quot;:&amp;quot;', "")
                    b = a.replace('&amp;quot;},{&amp;quot;$deletedFields',"")
                    c = b.replace('amp;',"")
                    d = c.replace('&quot;',"")
                    e = d.replace(':',"")
                    f = e.replace('headline',"")
                    g = f.replace('},{$deletedFields',"")
                    self.occupation = g
                    print(self.occupation)

    def getWorkHistory(self):
        with open(self.file, encoding="utf8") as f:
                contents = f.read()
                m = re.findall('companyName(.+?)timePeriod', contents)
                for n in m:
                    k = n
                    f = k.replace('quot;', "")
                    b = f.replace('amp', "")
                    c = b.replace(';,;',"")
                    d = c.replace(';:;',"")
                    e = d.replace(';:;',"")
                    f = e.replace('&;:&;',"")
                    g = f.replace('&;,&;',"")
                    h = g.replace(';;',"")
                    i = h.replace('&:&',"")
                    j = i.replace('&,&',"")
                    self.workHistory.append(j)


    def getPositionHistory(self):
        with open(self.file, encoding="utf8") as f:
                contents = f.read()
                m = re.findall('companyName(.+?)urn:li:fs_position',contents)
                for n in m:
                    #print("\n raw n:",n,"\n")
                    a = re.search('title(.+?),',n)
                    if a:
                        b = a.group(0)
                        c = b.replace('&amp;',"")
                        d = c.replace('quot;',"")
                        e = d.replace('title',"")
                        f = e.replace(',',"")
                        g = f.replace('&',"")
                        h = g.replace(':',"")
                        self.positionHistory.append(h)



    def mergeWork(self):
        if self.positionHistory:
            if self.workHistory:
                if len(self.positionHistory) == len(self.workHistory):
                    i = 0
                    for p in self.positionHistory:
                        entry = p + ":" + self.workHistory[i]
                        self.employmentHistory.append(entry)
                        i+=1
                        print(entry)

    def getIndustry(self):
        with open(self.file, encoding="utf8") as f:
                contents = f.read()
                m = re.search('industryName(.+?)lastName', contents)
                if m:
                    a = m.group(0)
                    b = a.replace('industryName', "")
                    c = b.replace('&quot;',"")
                    d = c.replace(':',"")
                    e = d.replace('lastName',"")
                    f = e.replace('&amp;',"")
                    g = f.replace('quot;',"")
                    h = g.replace(',',"")
                    self.industry = h
                    print("Industry:",self.industry)

    def getLocation(self):
        with open(self.file, encoding="utf8") as f:
                contents = f.read()
                m = re.search('industryName(.+?)Area', contents)
                if m:
                    a = m.group(0)
                    b = re.search('locationName(.+?)Area',a)
                    if b:
                        c = b.group(0)
                        d = c.replace('quot;',"")
                        e = d.replace('&amp;',"")
                        f = e.replace('locationName',"")
                        g = f.replace(':',"")
                        self.location = g
                        print("Location:",self.location)
                else:
                    m = re.search('industryName(.+?)miniProfile', contents)
                    if m:
                        a = m.group(0)
                        b = re.search('locationName(.+?)miniProfile',a)
                        if b:
                            c = b.group(0)
                            d = c.replace('quot;',"")
                            e = d.replace('&amp;',"")
                            f = e.replace('locationName',"")
                            g = f.replace('*miniProfile',"")
                            h = g.replace('student',"")
                            i = h.replace(',:false,',"")
                            j = i.replace('false',"")
                            k = j.replace(':',"")
                            l = k.replace('&',"")
                            m = l.replace(',,',"")
                            n = m.replace('&&',"")
                            self.location = m
                            print("Location:",self.location)
 
#*************************************************************************
# There is a separate method for saving each data element in case.
# This is in case a piece of data is missing, which would otherwise break
# the insertion statement.
#*************************************************************************
                            
    def saveName(self):
        
        if (self.uid is None) or (self.fname is None) or (self.lname is None):
            return ("missing uid, first name, or last name")
        
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if the record already exists in the db
            cursor.execute("""SELECT uid FROM identification WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()         
            if res is None:
                cursor.execute("""INSERT INTO identification (uid, fname, lname) VALUES(%s,%s,%s);""",\
                               (self.uid, self.fname, self.lname))                
            else:
                cursor.execute("""UPDATE identification SET fname = %s, lname = %s WHERE uid = %s;""",\
                               (self.fname, self.lname, self.uid)) 
            
            conn.commit()
            conn.close()
            
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error

    def saveLoc(self):
        
        if (self.uid is None) or (self.location is None) :
            return ("missing uid or location")
        
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if record already exists in the db
            cursor.execute("""SELECT uid FROM identification WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()         
            if res is None:
                cursor.execute("""INSERT INTO identification (uid, location) VALUES(%s,%s);""",\
                               (self.uid, self.location))                
            else:
                cursor.execute("""UPDATE identification SET location = %s WHERE uid = %s;""",\
                               (self.location, self.uid)) 
            
            conn.commit()
            conn.close()
            
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error
        

    def saveIndustry(self):
        
        if (self.uid is None) or (self.industry is None) :
            return ("missing uid or industry")
        
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if record already exists in the db
            cursor.execute("""SELECT uid FROM employment WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()         
            if res is None:
                cursor.execute("""INSERT INTO employment (uid, industry) VALUES(%s,%s);""",\
                               (self.uid, self.industry))                
            else:
                cursor.execute("""UPDATE employment SET industry = %s WHERE uid = %s;""",\
                               (self.industry, self.uid)) 
            
            conn.commit()
            conn.close()
            
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error


    def saveCurrent(self):
        
        if (self.uid is None) or (self.occupation is None) :
            return ("missing uid or occupation")
        
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if record already exists in the db
            cursor.execute("""SELECT uid FROM employment WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()         
            if res is None:
                cursor.execute("""INSERT INTO employment (uid, currentpos) VALUES(%s,%s);""",\
                               (self.uid, self.occupation))                
            else:
                cursor.execute("""UPDATE employment SET currentpos = %s WHERE uid = %s;""",\
                               (self.occupation, self.uid)) 
            
            conn.commit()
            conn.close()
            
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error


    def saveHistory(self):
        
        if (self.uid is None) or (self.employmentHistory is None) :
            return ("missing uid or employment history")
        
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if record already exists in the db
            cursor.execute("""SELECT uid FROM employment WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()         
            if res is None:
                cursor.execute("""INSERT INTO employment (uid, workhistory) VALUES(%s,%s);""",\
                               (self.uid, self.employmentHistory))                
            else:
                cursor.execute("""UPDATE employment SET workhistory = %s WHERE uid = %s;""",\
                               (self.employmentHistory, self.uid)) 
            
            conn.commit()
            conn.close()
            
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error


#*************************************************************************
# SaveResults is responsible for ensuring that the uid is valid and 
# appears on the users table. Assuming a good uid, it saves each piece
# of data separately.
#*************************************************************************    
    def saveResults(self):                
        try:
            #first, get connection.
            connect_str = "dbname='testpython' user='jordan' host='localhost' " + "password='labrat'"
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
         
            #check to see if the email address already exists in the db
            cursor.execute("""SELECT uid FROM users WHERE uid = %s;""",(self.uid,))
            res = cursor.fetchone()         
            if res is None:
                return "Bad or missing uid. Cannot save Data."
            else:
                extraction.saveName(self)
                extraction.saveLoc(self)
                extraction.saveIndustry(self)
                extraction.saveCurrent(self)
                extraction.saveHistory(self)
                                
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return error


#*************************************************************************
# The orchestrator coordinates all activities regarding linkedin profile
# scraping. It is the only method that needs to be called. 
#*************************************************************************
    
    def orchestrator(self):
        res = extraction.getFile(self)
        if self.file is None:
            print(res)
            return res
        else:
            extraction.getName(self)
            extraction.getCurrentPosition(self)
            extraction.getWorkHistory(self)
            extraction.getPositionHistory(self)
            extraction.mergeWork(self)
            extraction.getIndustry(self)
            extraction.getLocation(self)
            extraction.saveResults(self)

#*************************************************************************
# The purpose of this section is for unit testing. Comment off for
# production.
#*************************************************************************

uid = '1234567899'
#html = "view-source_https___www.linkedin.com_in_alec-yasinsac-3b5188_.html"
#html = "view-source_https___www.linkedin.com_in_jordan-shropshire-52709513_.html"
#html = "view-source_https___www.linkedin.com_in_mayor-karin-wilson-4212a09a_.html"
#html = "view-source_https___www.linkedin.com_in_eric-steward-ph-d-p-e-a3656864_.html"
html = "linkedinProfile.html"
client = extraction(uid)
client.orchestrator()

