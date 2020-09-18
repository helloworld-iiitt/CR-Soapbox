import json
import sqlite3
import datetime
from pytz import timezone
import codeSnippets as cs

dbfname = 'database/teleBot.sqlite'
conn =  sqlite3.connect(dbfname, check_same_thread=False)
cur=conn.cursor()


def setup(): 
    '''
    update tables - BRANCH_TB, YEAR_TB, GRADE_TB, TEACHER_TB, SUBJECT_TB
    '''
    for i in cs.clgdtlsjson["daylst"]:
        cur.execute('''INSERT OR IGNORE INTO DAY_TB (day) VALUES ( ? )''', ( i, ) ) #daytable
    
    for i in cs.clgdtlsjson["periodlst"]:
        cur.execute('''INSERT OR IGNORE INTO PERIOD_TB (period) VALUES ( ? )''', ( i, ) ) #periodtable
    
    for i in cs.clgdtlsjson["branch"]:
        cur.execute('''INSERT OR IGNORE INTO BRANCH_TB (branch) VALUES ( ? )''', ( i, ) ) #Branchtable
    
    for i in cs.clgdtlsjson["year"]:
        cur.execute('''INSERT OR IGNORE INTO YEAR_TB (year) VALUES ( ? )''', ( i, ) )  #Yeartable

    for i in cs.clgdtlsjson["branch"]:
        for j in cs.clgdtlsjson["year"]:
            cur.execute('SELECT id FROM BRANCH_TB WHERE branch = (?) ', (i, ))
            branch_id = cur.fetchone()[0]
            cur.execute('SELECT id FROM YEAR_TB WHERE year = ? ', (j, ))
            year_id = cur.fetchone()[0]
            grade = i+str(j%100)
            cur.execute('''INSERT OR IGNORE INTO GRADE_TB (grade,branch_id,year_id) VALUES ( ?, ?, ?)''', (grade,branch_id,year_id ) ) #Gradetable

    for i in cs.clgdtlsjson["teacher"]:
        emp_id= i
        tname= cs.clgdtlsjson["teacher"] [emp_id]
        cur.execute('''INSERT OR IGNORE INTO TEACHER_TB (tech_name,emp_id) VALUES ( ?,? )''', ( tname,emp_id ) )
    
    conn.commit()
    
    for i in cs.sublstjson:
        cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (i, ))
        grade_id = cur.fetchone()[0]
        for j in cs.sublstjson[i]:
            cur.execute('SELECT id FROM TEACHER_TB WHERE tech_name = ? ', (j["teacher"], )) # Have to change name to employee id
            teacher_id = cur.fetchone()[0]
            cur.execute('''INSERT OR IGNORE INTO SUBJECT_TB (subject,grade_id,teacher_id) VALUES ( ?, ?, ?)''', (j["subject"],grade_id,teacher_id ) ) #Subjecttable
    conn.commit()

def updatett(): #Update timetable
    '''
    Updates table - TIMETABLE_TB
    '''
    timetbl = open('json/timetable.json').read() #access json file
    cs.timetbljson = json.loads(timetbl)
    gradelst = cs.timetbljson.keys()
    for i in gradelst:
        daylst = cs.timetbljson[i].keys()
        for j in daylst:
            periodlst = cs.timetbljson[i][j].keys()
            for k in periodlst:
                subject = cs.timetbljson[i][j][k]

                cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (i, ))
                grade_id = cur.fetchone()[0]
                cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (j.capitalize(), ))
                day_id = cur.fetchone()[0]
                cur.execute('SELECT id FROM PERIOD_TB WHERE period = ? ', (k, ))
                period_id = cur.fetchone()[0]
                cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? AND grade_id = ?', (subject, grade_id))
                subject_id = cur.fetchone()[0]
                cur.execute('''INSERT OR IGNORE INTO TIMETABLE_TB (day_id,period_id,subject_id) VALUES ( ?, ?, ?)''', (day_id,period_id,subject_id) ) #TimeTable
    conn.commit()

def upddaytt(day): #Update timetable
    '''
    Updates table - TIMETABLE_TB
    '''
    gradelst = cs.timetbljson.keys()
    try:
        cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (day.capitalize(), ))
        day_id = cur.fetchone()[0]
        cur.execute('''DELETE FROM TIMETABLE_TB WHERE day_id = ?''',(day_id,))#delete the present day timetable 
        for i in gradelst:
            daylst = cs.timetbljson[i].keys()
            j = day
            if j in daylst:
                periodlst = cs.timetbljson[i][j].keys()
                for k in periodlst:
                    subject = cs.timetbljson[i][j][k]

                    cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (i, ))
                    grade_id = cur.fetchone()[0]
                    cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (j.capitalize(), ))
                    day_id = cur.fetchone()[0]
                    cur.execute('SELECT id FROM PERIOD_TB WHERE period = ? ', (k, ))
                    period_id = cur.fetchone()[0]
                    cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? AND grade_id = ?', (subject, grade_id))
                    subject_id = cur.fetchone()[0]
                    cur.execute('''INSERT OR IGNORE INTO TIMETABLE_TB (day_id,period_id,subject_id) VALUES ( ?, ?, ?)''', (day_id,period_id,subject_id) ) #insert next week same day TimeTable
        conn.commit()
    except:
        pass

def getStdtt(grade,day):
    '''
    Returns the students time table of the given day
        -- default day is set to the present day
        -- returns list of tuples of (period, subject)
    '''
    cur.execute('''SELECT PERIOD_TB.period,SUBJECT_TB.subject 
        FROM TIMETABLE_TB JOIN DAY_TB JOIN PERIOD_TB JOIN SUBJECT_TB JOIN GRADE_TB JOIN TEACHER_TB
        ON TIMETABLE_TB.day_id = DAY_TB.id AND TIMETABLE_TB.period_id = PERIOD_TB.id
        AND TIMETABLE_TB.subject_id = SUBJECT_TB.id AND SUBJECT_TB.grade_id = GRADE_TB.id 
        AND SUBJECT_TB.teacher_id = TEACHER_TB.id
        WHERE GRADE_TB.grade = ? AND DAY_TB.day = ? ORDER BY PERIOD_TB.id''', (grade,day))
    return cur.fetchall()

def getTeachtt(chat_id,day):
    '''
    Returns the teachers time table of the given day
        -- default day is set to the present day
        -- returns list of tuples of ( period, Grade, subject)
    '''
    emp_id = chktch(chat_id)
    cur.execute('''SELECT PERIOD_TB.period,GRADE_TB.grade,SUBJECT_TB.subject 
        FROM TIMETABLE_TB JOIN DAY_TB JOIN PERIOD_TB JOIN SUBJECT_TB JOIN GRADE_TB JOIN TEACHER_TB
        ON TIMETABLE_TB.day_id = DAY_TB.id AND TIMETABLE_TB.period_id = PERIOD_TB.id
        AND TIMETABLE_TB.subject_id = SUBJECT_TB.id AND SUBJECT_TB.grade_id = GRADE_TB.id 
        AND SUBJECT_TB.teacher_id = TEACHER_TB.id
        WHERE TEACHER_TB.emp_id = ? AND DAY_TB.day = ? ORDER BY PERIOD_TB.id''', (emp_id,day))
    return cur.fetchall()

def delcls (grade,subject,period,day):
    '''
    Delete the period of the given grade and day
        --default day is set to present day
    '''
    try:
        cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (grade, ))
        grade_id = cur.fetchone()[0]
        cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? AND grade_id  = ?', (subject,grade_id))
        subject_id = cur.fetchone()[0]
        cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (day, ))
        day_id = cur.fetchone()[0]
        cur.execute('SELECT id FROM PERIOD_TB WHERE period = ? ', (period, ))
        period_id = cur.fetchone()[0]
        cur.execute('''SELECT day_id FROM TIMETABLE_TB WHERE day_id = ? AND subject_id = ? AND period_id = ?''',(day_id,subject_id,period_id))
        cur.fetchone()[0]
        cur.execute('''DELETE FROM TIMETABLE_TB WHERE day_id = ? AND subject_id = ? AND period_id = ?''',(day_id,subject_id,period_id))
        conn.commit()
        return 1
    except:
        return -1

def CR8cls (grade,subject,period,day):
    '''
    Create the period on the given day for the given subject
        --default day is set to present day
        --if created returns 1 else returns -1
    '''
    try:
        cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (grade, ))
        grade_id = cur.fetchone()[0]
        cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? AND grade_id = ?', (subject,grade_id))
        subject_id = cur.fetchone()[0]
        cur.execute('SELECT id FROM DAY_TB WHERE day = ? ', (day, ))
        day_id = cur.fetchone()[0]
        cur.execute('SELECT id FROM PERIOD_TB WHERE period = ? ', (period, ))
        period_id = cur.fetchone()[0] 
        cur.execute('''SELECT SUBJECT_TB.subject FROM TIMETABLE_TB JOIN SUBJECT_TB ON TIMETABLE_TB.subject_id = SUBJECT_TB.id 
        WHERE SUBJECT_TB.grade_id = (?) AND TIMETABLE_TB.day_id = (?) AND TIMETABLE_TB.period_id= (?)''',(grade_id,day_id,period_id))
        try:
            cur.fetchone()[0]
            return -1
        except:
            pass
        cur.execute('''INSERT INTO TIMETABLE_TB(day_id,period_id, subject_id) VALUES ( ?, ?,  ?) ''',(day_id,period_id,subject_id))
        conn.commit()
        cur.execute('''SELECT SUBJECT_TB.subject FROM TIMETABLE_TB JOIN SUBJECT_TB ON TIMETABLE_TB.subject_id = SUBJECT_TB.id 
        WHERE SUBJECT_TB.grade_id = (?) AND TIMETABLE_TB.day_id = (?) AND TIMETABLE_TB.period_id= (?)''',(grade_id,day_id,period_id))
        return  cur.fetchone()[0]
    except:
        return -1

def usrsetup(chat_id,roll_no,updusr = False):
    '''
    Stores the chat_id(text), roll_no(text) of the user
    update the ATTEND_TB with the user grade subjects
    '''
    grade = roll_no.split('U')[0]
    try:
        cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (grade, ))
        grade_id = cur.fetchone()[0]
        if not updusr:
            cur.execute('''INSERT OR IGNORE INTO USER_TB (chat_id,roll_no,grade_id) VALUES ( ?, ?, ?)''', (chat_id,roll_no,grade_id) )
        else:
            cur.execute('''UPDATE USER_TB SET roll_no = ? , grade_id = ? WHERE chat_id = ?''',(roll_no,grade_id,chat_id ))
        cur.execute('SELECT id FROM SUBJECT_TB WHERE grade_id = ?',(grade_id,))
        sublst = cur.fetchall()
        cur.execute('SELECT id FROM USER_TB WHERE roll_no = ? AND chat_id = ?',(roll_no,chat_id))
        chat_id = cur.fetchone()[0]
        for i in sublst:
            cur.execute('''INSERT OR IGNORE INTO ATTEND_TB (chat_id,subject_id,attend_pcls,attend_tcls) VALUES ( ?, ?, ?, ?)''', (chat_id,i[0],0,0) )
    except:
        return chkusr(chat_id)
    conn.commit()
    return roll_no

def tchsetup(chat_id,emp_id,updusr = False):
    '''
    Stores the chat_id, Employee_id of the user
    '''
    try:
        cur.execute('SELECT id FROM TEACHER_TB WHERE emp_id = ? ', (emp_id,))
        cur.fetchone()[0]
        if not updusr:
            cur.execute('''INSERT INTO TCHUSR_TB (chat_id,emp_id) VALUES ( ?, ?)''', (chat_id,emp_id))
        else:
            cur.execute('''UPDATE TCHUSR_TB SET emp_id = ?  WHERE chat_id = ?''',(emp_id, chat_id))
        conn.commit()
        return emp_id
    except:
        return chktch(chat_id)

def setstdatt(chat_id,subject,attend_pcls=1,attend_tcls=1):
    '''
    Record the attendance of the student for the given subject with 
        presented class and total classes
        -- (it will set the given values to presented class and total classes if presented class >1 and total classes >1 ,total classes==0)
        -- default is set to present in single class of the given subject

    '''
    cur.execute('SELECT id FROM SUBJECT_TB WHERE subject = ? ', (subject, ))
    subject_id = cur.fetchone()[0]
    cur.execute('SELECT id FROM USER_TB WHERE chat_id = ?',(chat_id,))
    chat_id = cur.fetchone()[0]
    cur.execute('SELECT attend_pcls,attend_tcls FROM ATTEND_TB WHERE chat_id = ? AND subject_id =?',(chat_id,subject_id))
    attend = cur.fetchall()
    if ((attend_pcls == 0 or attend_pcls == 1) and attend_tcls == 1 ):
        attend_pcls = attend_pcls + int(attend[0][0])
        attend_tcls = attend_tcls + int(attend[0][1])
    cur.execute('UPDATE ATTEND_TB SET attend_pcls = ? , attend_tcls = ? WHERE chat_id = ? AND subject_id =?',(attend_pcls,attend_tcls,chat_id,subject_id ))
    conn.commit()

def getstdatt(chat_id):
    '''
    Returns the list of tuple of (subject, presented_classes, total_classes)
    '''
    cur.execute('SELECT id FROM USER_TB WHERE chat_id = ?',(chat_id,))
    chat_id = cur.fetchone()[0]
    cur.execute('''SELECT SUBJECT_TB.subject,ATTEND_TB.attend_pcls,ATTEND_TB.attend_tcls
        FROM ATTEND_TB JOIN SUBJECT_TB ON ATTEND_TB.subject_id = SUBJECT_TB.id WHERE chat_id = ?''',(chat_id,))
    return cur.fetchall()

def getusrgrd(chat_id):
    '''
    Returns grade in str
    '''
    cur.execute('SELECT GRADE_TB.grade FROM USER_TB JOIN GRADE_TB ON USER_TB.grade_id = GRADE_TB.id WHERE chat_id = ?',(chat_id,))
    return cur.fetchone()[0]

def getsubgrd(grade):
    '''
    Returns list of subjects in the given grade
    '''
    cur.execute('SELECT SUBJECT_TB.subject FROM SUBJECT_TB JOIN GRADE_TB ON SUBJECT_TB.grade_id = GRADE_TB.id WHERE GRADE_TB.grade = ?',(grade,))
    subtpl = cur.fetchall()
    sublst = list()
    for i in subtpl:
        sublst.append(i[0])
    return sublst

def chkusr(chat_id):
    '''
        Check if user is already in the list
        Returns roll no if exists else return None
    '''
    cur.execute('SELECT roll_no FROM USER_TB WHERE chat_id = ?',(chat_id,))
    try:
        return cur.fetchone()[0]
    except:
        return None

def chktch(chat_id):
    '''
        Check if teacher is already in the list
        Returns employee no if exists else return None
    '''
    cur.execute('SELECT emp_id FROM TCHUSR_TB WHERE chat_id = ?',(chat_id,))
    try:
        return cur.fetchone()[0]
    except:
        return None

def getStdChatId(roll_no):
    '''
        Returns the chat id of student with the given roll no
    '''
    cur.execute('SELECT chat_id FROM USER_TB WHERE roll_no = ?',(roll_no,))
    try:
        return cur.fetchone()[0]
    except:
        return None

def getTchChatId(emp_id):
    '''
        Returns the chat id of student with the given emp_id
    '''
    cur.execute('SELECT chat_id FROM TCHUSR_TB WHERE emp_id = ?',(emp_id,))
    try:
        return cur.fetchone()[0]
    except:
        return None

def grdstdid(grade):
    '''
        Returns List of chat_id of students in the grade
    '''
    cur.execute('''SELECT USER_TB.chat_id FROM USER_TB JOIN GRADE_TB 
                        ON USER_TB.grade_id = GRADE_TB.id WHERE GRADE_TB.grade = ?''',(grade,))
    stdtpl = cur.fetchall()
    stdlst = list()
    for i in stdtpl:
        stdlst.append(i[0])
    return stdlst

def tchgrdsub(chat_id):
    '''
        Returns List of tuple of grade,subject that a teacher will attend
    '''
    emp_id = chktch(chat_id)
    cur.execute('''SELECT GRADE_TB.grade,SUBJECT_TB.subject FROM GRADE_TB JOIN SUBJECT_TB JOIN TEACHER_TB 
                        ON SUBJECT_TB.grade_id = GRADE_TB.id AND SUBJECT_TB.teacher_id = TEACHER_TB.id WHERE TEACHER_TB.emp_id = ?''',(emp_id,))
    return cur.fetchall()

def getallgrdsub():
    '''
        Returns List of tuple of grade,subject in the Timetable
    '''
    cur.execute('''SELECT GRADE_TB.grade,SUBJECT_TB.subject FROM GRADE_TB JOIN SUBJECT_TB JOIN TEACHER_TB 
                        ON SUBJECT_TB.grade_id = GRADE_TB.id AND SUBJECT_TB.teacher_id = TEACHER_TB.id''')
    return cur.fetchall()

def getallstduid():
    '''
        Returns List of chat_id of students in bot 
    '''
    cur.execute('''SELECT chat_id FROM USER_TB ''')
    usrtpl = cur.fetchall()
    usrlst = list()
    for i in usrtpl:
        usrlst.append(i[0])
    return usrlst

def getalltchuid():
    '''
        Returns List of chat_id of Teachers in bot 
    '''
    cur.execute('''SELECT chat_id FROM TCHUSR_TB''')
    usrtpl = cur.fetchall()
    usrlst = list()
    for i in usrtpl:
        usrlst.append(i[0])
    return usrlst

def getallstdrollno():
    '''
        Returns List of chat_id of students in bot 
    '''
    cur.execute('''SELECT roll_no FROM USER_TB ''')
    usrtpl = cur.fetchall()
    usrlst = list()
    for i in usrtpl:
        usrlst.append(i[0])
    return usrlst

def getalltchempid():
    '''
        Returns List of chat_id of Teachers in bot 
    '''
    cur.execute('''SELECT emp_id FROM TCHUSR_TB''')
    usrtpl = cur.fetchall()
    usrlst = list()
    for i in usrtpl:
        usrlst.append(i[0])
    return usrlst

def getallsub():
    '''
        Returns All the subjects in the timetable
    '''
    cur.execute('''SELECT subject FROM SUBJECT_TB''')
    subtpl = cur.fetchall()
    sublst = list()
    for i in subtpl:
        sublst.append(i[0])
    return sublst

def getallgrd():
    '''
        Returns All the Grades in the timetable
    '''
    cur.execute('''SELECT grade FROM GRADE_TB''')
    grdtpl = cur.fetchall()
    grdlst = list()
    for i in grdtpl:
        grdlst.append(i[0])
    return grdlst

def rmvstd(chat_id):
    '''
        Remove the chat id of student from the database
    '''
    try:
        cur.execute('SELECT id FROM USER_TB WHERE chat_id = ?',(chat_id,))
        chat_id_id = cur.fetchone()[0]
        cur.execute('DELETE FROM ATTEND_TB WHERE chat_id = ?',(chat_id_id,))
        cur.execute('DELETE FROM USER_TB WHERE chat_id = ?',(chat_id,))
        conn.commit()
        return 1
    except:
        return -1

def rmvtch(chat_id):
    '''
        Remove the chat id of teacher from the database
    '''
    cur.execute('DELETE FROM TCHUSR_TB WHERE chat_id = ?',(chat_id,))
    conn.commit()

def addCR(roll_no):
    '''
        Function to add CR to DB returns rollno of the cr of the class
    '''
    grade = roll_no.split('U')[0]
    cur.execute('SELECT id FROM GRADE_TB WHERE grade = ? ', (grade, ))
    grade_id = cur.fetchone()[0]
    try:
        cur.execute('''INSERT INTO CR_TB (grade_id,roll_no) VALUES ( ?, ?)''', (grade_id,roll_no) )
        conn.commit()
        return roll_no
    except:
        cur.execute('SELECT roll_no FROM CR_TB WHERE grade_id = ? ', (grade_id, ))
        return cur.fetchone()[0]

def getCR():
    '''
        return the list of roll no of CR 
    '''
    cur.execute('SELECT roll_no FROM CR_TB ')
    rolltpl = cur.fetchall()
    rolllst = list()
    for i in rolltpl:
        rolllst.append(i[0])
    return rolllst

def delCR(roll_no):
    '''
        Function to delete CR from DB
    '''
    cur.execute('DELETE FROM CR_TB WHERE roll_no = ?',(roll_no,))
    conn.commit()
'''
--init--
Create tables - BRANCH_TB, YEAR_TB, GRADE_TB, TEACHER_TB, SUBJECT_TB, USER_TB, ATTEND_TB 
Create and update tables - DAY_TB, PERIOD_TB
'''

ftable = open('sqlite/tbCreateDb').read()
cur.executescript(ftable)
conn.commit()
setup()
updatett()
