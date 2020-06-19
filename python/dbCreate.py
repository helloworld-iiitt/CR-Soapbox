import json
import sqlite3
import datetime

class teleDb:
    
    "Class for database creation of telegram bot"
    
    def __init__(self,dbfname = 'database/teleBot.sqlite'): #Create tables - days, periods
        '''
        Create tables - BRANCH_TB, YEAR_TB, GRADE_TB, TEACHER_TB, SUBJECT_TB, USER_TB, ATTEND_TB 
        Create and update tables - DAY_TB, PERIOD_TB
        '''
        
        self.conn =  sqlite3.connect(dbfname, check_same_thread=False)
        self.cur=self.conn.cursor()

        ftable = open('sqlite/tbCreateDb').read()
        self.cur.executescript(ftable)

        daylst = ['Monday','Tuesday','Wednesday','Thursday','Friday']
        periodlst = ['10.10-11.00','11.00-11.50','11.50-12.40','01.30-02.20','02.20-03.10','03.10-04.00']
        
        for i in daylst:
            self.cur.execute('''INSERT OR IGNORE INTO DAY_TB (day) VALUES ( ? )''', ( i, ) ) #daytable
        
        for i in periodlst:
            self.cur.execute('''INSERT OR IGNORE INTO PERIOD_TB (period) VALUES ( ? )''', ( i, ) ) #periodtable
        
        self.conn.commit()
        self.setup()
        self.updatett()
    
    def setup(self): 
        
        '''
        update tables - BRANCH_TB, YEAR_TB, GRADE_TB, TEACHER_TB, SUBJECT_TB
        '''

        fbhyr = open('json/branchYearlist.json').read() #access json file
        fbydata = json.loads(fbhyr)
        for i in fbydata["branch"]:
            self.cur.execute('''INSERT OR IGNORE INTO BRANCH_TB (branch) VALUES ( ? )''', ( i, ) ) #Branchtable
        
        for i in fbydata["year"]:
            self.cur.execute('''INSERT OR IGNORE INTO YEAR_TB (year) VALUES ( ? )''', ( i, ) )  #Yeartable

        for i in fbydata["branch"]:
            for j in fbydata["year"]:
                self.cur.execute('SELECT id FROM BRANCH_TB WHERE branch = (?) ', (i, ))
                branch_id = self.cur.fetchone()[0]
                self.cur.execute('SELECT id FROM YEAR_TB WHERE year = ? ', (j, ))
                year_id = self.cur.fetchone()[0]
                grade = i+str(j%100)
                self.cur.execute('''INSERT OR IGNORE INTO GRADE_TB (grade,branch_id,year_id) VALUES ( ?, ?, ?)''', (grade,branch_id,year_id ) ) #Gradetable

        for i in fbydata["teacher"]:
            emp_id= i
            tname= fbydata["teacher"] [emp_id]
            self.cur.execute('''INSERT OR IGNORE INTO TEACHER_TB (tech_name,emp_id) VALUES ( ?,? )''', ( tname,emp_id ) )
        
        self.conn.commit()
        
        fsublst = open('json/subjectlst.json').read() #access json file 
        fsubdata = json.loads(fsublst)
        for i in fsubdata:
            self.cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (i["grade"], ))
            grade_id = self.cur.fetchone()[0]
            self.cur.execute('SELECT id FROM TEACHER_TB WHERE tech_name = ? ', (i["teacher"], )) # Have to change name to employee id
            teacher_id = self.cur.fetchone()[0]
            self.cur.execute('''INSERT OR IGNORE INTO SUBJECT_TB (subject,grade_id,teacher_id) VALUES ( ?, ?, ?)''', (i["subject"],grade_id,teacher_id ) ) #Subjecttable
        self.conn.commit()

    def updatett(self): #Update timetable
        '''
        Updates table - TIMETABLE_TB
        '''
        ftt = open('json/timetable.json').read() #access json file
        fttdata = json.loads(ftt)
        gradelst = fttdata.keys()
        for i in gradelst:
            daylst = fttdata[i].keys()
            for j in daylst:
                periodlst = fttdata[i][j].keys()
                for k in periodlst:
                    subject = fttdata[i][j][k]

                    self.cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (i, ))
                    grade_id = self.cur.fetchone()[0]
                    self.cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (j.capitalize(), ))
                    day_id = self.cur.fetchone()[0]
                    self.cur.execute('SELECT id FROM PERIOD_TB WHERE period = ? ', (k, ))
                    period_id = self.cur.fetchone()[0]
                    self.cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? AND grade_id = ?', (subject, grade_id))
                    subject_id = self.cur.fetchone()[0]
                    self.cur.execute('''INSERT OR IGNORE INTO TIMETABLE_TB (day_id,period_id,subject_id) VALUES ( ?, ?, ?)''', (day_id,period_id,subject_id) ) #TimeTable
        self.conn.commit()

    def upddaytt(self,day = datetime.datetime.now().strftime("%A")): #Update timetable
        '''
        Updates table - TIMETABLE_TB
        '''
        ftt = open('json/timetable.json').read() #access json file
        fttdata = json.loads(ftt)
        gradelst = fttdata.keys()
        self.day = day
        for i in gradelst:
            daylst = fttdata[i].keys()
            j = self.day
            if j in daylst:
                periodlst = fttdata[i][j].keys()
                for k in periodlst:

                    subject = fttdata[i][j][k]

                    self.cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (i, ))
                    grade_id = self.cur.fetchone()[0]
                    self.cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (j.capitalize(), ))
                    day_id = self.cur.fetchone()[0]
                    self.cur.execute('SELECT id FROM PERIOD_TB WHERE period = ? ', (k, ))
                    period_id = self.cur.fetchone()[0]
                    self.cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? AND grade_id = ?', (subject, grade_id))
                    subject_id = self.cur.fetchone()[0]
                    self.cur.execute('''INSERT OR IGNORE INTO TIMETABLE_TB (day_id,period_id,subject_id) VALUES ( ?, ?, ?)''', (day_id,period_id,subject_id) ) #TimeTable
        self.conn.commit()

    def getStdtt(self,grade,day = datetime.datetime.now().strftime("%A")):
        '''
        Returns the students time table of the given day
            --default day is set to the present day
            returns list of tuples of (period, subject)
        '''
        self.grade = grade
        self.day = day
        self.cur.execute('''SELECT PERIOD_TB.period,SUBJECT_TB.subject 
            FROM TIMETABLE_TB JOIN DAY_TB JOIN PERIOD_TB JOIN SUBJECT_TB JOIN GRADE_TB JOIN TEACHER_TB
            ON TIMETABLE_TB.day_id = DAY_TB.id AND TIMETABLE_TB.period_id = PERIOD_TB.id
            AND TIMETABLE_TB.subject_id = SUBJECT_TB.id AND SUBJECT_TB.grade_id = GRADE_TB.id 
            AND SUBJECT_TB.teacher_id = TEACHER_TB.id
            WHERE GRADE_TB.grade = ? AND DAY_TB.day = ? ORDER BY PERIOD_TB.id''', (self.grade,self.day))
        return self.cur.fetchall()

    def getTeachtt(self,chat_id,day = datetime.datetime.now().strftime("%A")):
        '''
        Returns the teachers time table of the given day
            --default day is set to the present day
            returns list of tuples of ( period, branch, subject)
        '''
        self.chat_id = chat_id
        self.emp_id = self.chktch(self.chat_id)
        self.day = day
        self.cur.execute('''SELECT PERIOD_TB.period,GRADE_TB.grade,SUBJECT_TB.subject 
            FROM TIMETABLE_TB JOIN DAY_TB JOIN PERIOD_TB JOIN SUBJECT_TB JOIN GRADE_TB JOIN TEACHER_TB
            ON TIMETABLE_TB.day_id = DAY_TB.id AND TIMETABLE_TB.period_id = PERIOD_TB.id
            AND TIMETABLE_TB.subject_id = SUBJECT_TB.id AND SUBJECT_TB.grade_id = GRADE_TB.id 
            AND SUBJECT_TB.teacher_id = TEACHER_TB.id
            WHERE TEACHER_TB.emp_id = ? AND DAY_TB.day = ? ORDER BY PERIOD_TB.id''', (self.emp_id,self.day))
        return self.cur.fetchall()
    def delcls (self,subject,period,day = datetime.datetime.now().strftime("%A")):
        '''
        Delete the period of the given grade and day
            --default day is set to present day
        '''
        self.subject = subject
        self.period = period
        self.day = day
        try:
            self.cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? ', (self.subject, ))
            subject_id = self.cur.fetchone()[0]
            self.cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (self.day, ))
            day_id = self.cur.fetchone()[0]
            self.cur.execute('SELECT id FROM PERIOD_TB WHERE period = ? ', (self.period, ))
            period_id = self.cur.fetchone()[0]
            self.cur.execute('''DELETE FROM TIMETABLE_TB WHERE day_id = ? AND subject_id = ? AND period_id = ?''',(day_id,subject_id,period_id))
            self.conn.commit()
            return 1
        except:
            return -1

    def crecls (self,subject,period,day = datetime.datetime.now().strftime("%A")):
        '''
        Create the period on the given day for the given subject
            --default day is set to present day
            --if created returns 1 else returns -1
        '''
        self.subject = subject
        self.period = period
        self.day = day
        try:
            self.cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? ', (self.subject, ))
            subject_id = self.cur.fetchone()[0]
            self.cur.execute('SELECT grade_id FROM SUBJECT_TB WHERE subject = ? ', (self.subject, ))
            grade_id = self.cur.fetchone()[0]
            self.cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (self.day, ))
            day_id = self.cur.fetchone()[0]
            self.cur.execute('SELECT id FROM PERIOD_TB WHERE period = ? ', (self.period, ))
            period_id = self.cur.fetchone()[0] 

            self.cur.execute('''INSERT INTO TIMETABLE_TB(day_id,period_id, subject_id) VALUES ( ?, ?,  ?) ''',(day_id,period_id,subject_id))
            self.conn.commit()
            self.cur.execute('''SELECT SUBJECT_TB.subject FROM TIMETABLE_TB JOIN SUBJECT_TB ON TIMETABLE_TB.subject_id = SUBJECT_TB.id 
            WHERE SUBJECT_TB.grade_id = (?) AND TIMETABLE_TB.day_id = (?) AND TIMETABLE_TB.period_id= (?)''',(grade_id,day_id,period_id))

            return  self.cur.fetchone()[0]
        except:
            return -1

    def usrsetup(self,chat_id,roll_no,updusr = False):
        '''
        Stores the chat_id(text), roll_no(text) of the user
        update the ATTEND_TB with the user grade subjects
        '''
        self.chat_id = chat_id
        self.roll_no = roll_no
        self.updusr = updusr
        grade = self.roll_no.split('U')[0]
        try:
            self.cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (grade, ))
            grade_id = self.cur.fetchone()[0]
            if not self.updusr:
                self.cur.execute('''INSERT OR IGNORE INTO USER_TB (chat_id,roll_no,grade_id) VALUES ( ?, ?, ?)''', (self.chat_id,self.roll_no,grade_id) )
            else:
                self.cur.execute('''UPDATE USER_TB SET roll_no = ? , grade_id = ? WHERE chat_id = ?''',(self.roll_no,grade_id,self.chat_id ))
            self.cur.execute('SELECT id FROM SUBJECT_TB WHERE grade_id = ?',(grade_id,))
            sublst = self.cur.fetchall()
            self.cur.execute('SELECT id FROM USER_TB WHERE roll_no = ? AND chat_id = ?',(self.roll_no,self.chat_id))
            user_id = self.cur.fetchone()[0]
            for i in sublst:
                self.cur.execute('''INSERT OR IGNORE INTO ATTEND_TB (user_id,subject_id,attend_pcls,attend_tcls) VALUES ( ?, ?, ?, ?)''', (user_id,i[0],0,0) )
        except:
            return self.chkusr(self.chat_id)
        self.conn.commit()
        return roll_no

    def tchsetup(self,chat_id,emp_id,updusr = False):
        '''
        Stores the chat_id(text), Employee_id(text) of the user
        update the ATTEND_TB with the user grade subjects
        '''
        self.chat_id = chat_id
        self.emp_id = emp_id
        self.updusr = updusr
        try:
            self.cur.execute('SELECT id FROM TEACHER_TB WHERE emp_id = ? ', (self.emp_id,))
            self.cur.fetchone()[0]
            if not self.updusr:
                self.cur.execute('''INSERT INTO TCHUSR_TB (chat_id,emp_id) VALUES ( ?, ?)''', (self.chat_id,self.emp_id))
            else:
                self.cur.execute('''UPDATE TCHUSR_TB SET emp_id = ?  WHERE chat_id = ?''',(self.emp_id, self.chat_id))
            self.conn.commit()
            return self.emp_id
        except:
            return self.chktch(self.chat_id)
    
    def setstdatt(self,chat_id,subject,attend_pcls=1,attend_tcls=1):
        '''
        Record the attendance of the student for the given subject with 
            presented class and total classes
            -- (it will set the given values to presented class and total classes if presented class >1 and total classes >1 ,total classes==0)
            -- default is set to present in single class of the given subject

        '''
        self.chat_id = chat_id
        self.subject = subject
        self.attend_pcls = attend_pcls
        self.attend_tcls = attend_tcls
        self.cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? ', (self.subject, ))
        subject_id = self.cur.fetchone()[0]
        self.cur.execute('SELECT id FROM USER_TB WHERE chat_id = ?',(self.chat_id,))
        user_id = self.cur.fetchone()[0]
        self.cur.execute('SELECT attend_pcls,attend_tcls FROM ATTEND_TB WHERE user_id = ? AND subject_id =?',(user_id,subject_id))
        attend = self.cur.fetchall()
        if ((self.attend_pcls == 0 or self.attend_pcls == 1) and self.attend_tcls == 1 ):
            self.attend_pcls = self.attend_pcls + int(attend[0][0])
            self.attend_tcls = self.attend_tcls + int(attend[0][1])
        self.cur.execute('UPDATE ATTEND_TB SET attend_pcls = ? , attend_tcls = ? WHERE user_id = ? AND subject_id =?',(self.attend_pcls,self.attend_tcls,user_id,subject_id ))
        self.conn.commit()

    def getstdatt(self,chat_id):
        '''
        Returns the list of tuple of (subject, presented_classes, total_classes)
        '''
        self.chat_id = chat_id
        self.cur.execute('SELECT id FROM USER_TB WHERE chat_id = ?',(self.chat_id,))
        user_id = self.cur.fetchone()[0]
        self.cur.execute('''SELECT SUBJECT_TB.subject,ATTEND_TB.attend_pcls,ATTEND_TB.attend_tcls
            FROM ATTEND_TB JOIN SUBJECT_TB ON ATTEND_TB.subject_id = SUBJECT_TB.id WHERE user_id = ?''',(user_id,))
        return self.cur.fetchall()
    
    def getusrgrd(self,chat_id):
        '''
        Returns grade in str
        '''
        self.chat_id = chat_id
        self.cur.execute('SELECT GRADE_TB.grade FROM USER_TB JOIN GRADE_TB ON USER_TB.grade_id = GRADE_TB.id WHERE chat_id = ?',(self.chat_id,))
        return self.cur.fetchone()[0]
    
    def getsubgrd(self,grade):
        '''
        Returns list of tuples of subjects in the given grade
        '''
        self.grade = grade
        self.cur.execute('SELECT SUBJECT_TB.subject FROM SUBJECT_TB JOIN GRADE_TB ON SUBJECT_TB.grade_id = GRADE_TB.id WHERE GRADE_TB.grade = ?',(self.grade,))
        return self.cur.fetchall()
    def getusrlst(self):
        '''
            Returns list of tuples of user id of students
        '''
        self.cur.execute('SELECT chat_id FROM USER_TB')
        return self.cur.fetchall()

    def gettchlst(self):
        '''
            Returns list of tuples of user id of teachers
        '''
        self.cur.execute('SELECT chat_id FROM TCHUSR_TB')
        return self.cur.fetchall()

    def chkusr(self,chat_id):
        '''
            Check if user is already in the list
            Returns roll no if exists else return None
        '''
        self.chat_id = chat_id
        self.cur.execute('SELECT roll_no FROM USER_TB WHERE chat_id = ?',(self.chat_id,))
        try:
            return self.cur.fetchone()[0]
        except:
            return None
    
    def chktch(self,chat_id):
        '''
            Check if teacher is already in the list
            Returns employee no if exists else return None
        '''
        self.chat_id = chat_id
        self.cur.execute('SELECT emp_id FROM TCHUSR_TB WHERE chat_id = ?',(self.chat_id,))
        try:
            return self.cur.fetchone()[0]
        except:
            return None

    def grdstdid(self,grade):
        '''
            Returns List of tuple of chat_id of students in the grade
        '''
        self.grade = grade
        self.cur.execute('''SELECT USER_TB.chat_id FROM USER_TB JOIN GRADE_TB 
                            ON USER_TB.grade_id = GRADE_TB.id WHERE GRADE_TB.grade = ?''',(self.grade,))
        return self.cur.fetchall()

    def tchgrdsub(self,chat_id):
        '''
            Returns List of tuple of grade,subject that a teacher will attend
        '''
        self.chat_id = chat_id
        emp_id = self.chktch(self.chat_id)
        self.cur.execute('''SELECT GRADE_TB.grade,SUBJECT_TB.subject FROM GRADE_TB JOIN SUBJECT_TB JOIN TEACHER_TB 
                            ON SUBJECT_TB.grade_id = GRADE_TB.id AND SUBJECT_TB.teacher_id = TEACHER_TB.id WHERE TEACHER_TB.emp_id = ?''',(emp_id,))
        return self.cur.fetchall()

if __name__ == '__main__':
    db = teleDb()
    db.crecls("CSPC29","03.10-04.00","Monday")