import datetime, json, re, time, json
import telegram
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
import logging, pytz
from pytz import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatAction
import dbCreate as db
import codeSnippets as cs
## Conversation dict Constants keys
MAIN_MENU_KEY, AUTH_KEY, TT_MENU_KEY, DAILY_TT_KEY, ATD_MENU_KEY = range(0,5)
SETATD_SUB_KEY, SETATD_STAT_KEY, MORE_MENU_KEY, CT_MENU_KEY, STOPPING, DEV_MSG_KEY= range(5,11)



##
##   Authentication Cov Functions (Level- 0(part-i))
##
@cs.send_action(action=ChatAction.TYPING)
def rollno(update, context):
    '''
        Function to ask the user to enter his roll no
    '''
    update.message.reply_text(text='''Please tell me\n*Your IIITT Roll Number*\nto Log you in.''', 
                                parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    return AUTH_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivrollno(update, context):
    '''
        Function to send error when user enters Invalid rollno in Authentication Menu
    '''
    update.message.reply_text(text='''Its *NOT a valid* Roll No or\nSomeone has *Already registered* with this Roll No\nPlease tell me *A Valid Roll No*\n
                                        If someone else is using your account please contact the *Devoloper*''', parse_mode= 'Markdown')
    return AUTH_KEY

@cs.send_action(action=ChatAction.TYPING)
def Authentication(update, context):
    '''
        Function to athenticate the user as student (sequence part)
    '''
    updusr = False
    if db.chkusr(update.effective_chat.id) != None:
        updusr = True
    rollno = db.usrsetup(update.effective_chat.id,(update.message.text).upper(),updusr)
    if rollno :
        update.message.reply_text(text="I linked Your Rollno *{}*, \nto your account".format(rollno), parse_mode= 'Markdown')
        update.message.text = rollno
        update.message.reply_text("Select *Menu* to see the list of things that you can ask me.", parse_mode= 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup([['Menu']]))
        return cs.STOP  
    else:
        return ivrollno(update, context)

##
##   Student Menu Functions (Level 1)
##
# @cs.userauthorized(db.getallstduid())
@cs.send_action(action=ChatAction.TYPING)
def Menu(update,context):
    '''
        Function to send Student Main Menu to the user
    '''
    menu = cs.build_menu(buttons=["Timetable","Attendance","More"])
    update.message.reply_text(text='''Ask me what you want to know from the Below list''',parse_mode = 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return MAIN_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivmenu(update, context):
    '''
        Function to send error when user Enters an Invalid option in Student Main Menu
    '''
    update.message.reply_text(text='''Sorry 😭, I can't do that''', parse_mode= 'Markdown')
    return Menu(update,context)

##
##  Student Timetable Menu Functions (Level 2)
##
@cs.send_action(action=ChatAction.TYPING)
def tt_Menu(update,context):
    '''
        Function to send Student Timetable Menu to the user
    '''
    menu = cs.build_menu(buttons=["Today's Timetable","Daily Timetable","Back"])
    update.message.reply_text(text='''Tell me, what you want to know about *Your Timetable*?''',parse_mode = 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return TT_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivTTMenu(update,context):
    '''
        Function to send error when user enters Invalid rollno in Student Timetable Menu
    '''
    menu = cs.build_menu(buttons=["Today's Timetable","Daily Timetable","Back"])
    update.message.reply_text(text='''Sorry 😭, I can't do that\nPlease select from the *Given list*''', parse_mode= 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return TT_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkSTMC(update,context):
    '''
        Function to send back from std_TT_Menu_cov to std_Menu_cov
    '''
    Menu(update,context)
    return cs.END

##
##  Student Timetable Reply Functions
##
def std_tt(chat_id,day= datetime.datetime.now(tz= timezone('Asia/Kolkata')).strftime("%A")):
    '''
        Function to Return student Timetable as a string
    '''
    perlst  =   db.getStdtt(db.getusrgrd(chat_id),day)
    text    =   "Time     : Subject\n"
    no_cls  =   True 
    for i in perlst:
        no_cls  =   False
        text    =   text + i[0] + " : " + i[1]+"\n"
    if no_cls:
        return "No Classes"
    else:
        return text

#   Today Timetable Reply Functions (level 2)

@cs.send_action(action=ChatAction.TYPING)
def td_Std_TT (update,context):
    '''
        Function to send Today's Timetable to the user
    '''
    text = std_tt(update.effective_chat.id)
    if text == 'No Classes':
        update.message.reply_text(text="No Classes Today")
    else :
        text = "Todays's Timetable\n" + text
        update.message.reply_text(text=text)
    return TT_MENU_KEY

##  Daily Timetable Reply Function(level 3) - Send Day Keyboard to user

@cs.send_action(action=ChatAction.TYPING)
def dayKb_DTMC (update,context):
    '''
        Function to send KeyBoard of Days to the user in Student Timetable/Daily_Timetable path
    '''
    text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
    update.message.reply_text(text='''Tell me, Which day Timetable do you want ?''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    return DAILY_TT_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivday_DTMC(update,context):
    '''
        Function to send error when user enters Invalid day in Student Timetable/Daily_Timetable path
    '''
    text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
    update.message.reply_text(text='''Its not a Day from the list\nPlease sent me a day from the list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    return DAILY_TT_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkDTMC(update,context):
    '''
        Function to send back from std_DailyTT_Menu_cov to std_TT_Menu_cov
    '''
    tt_Menu(update,context)
    return cs.END

##  Daily Timetable Reply Function(level 3) - Send Timetable to user

@cs.send_action(action=ChatAction.TYPING)
def day_std_tt (update,context):
    '''
        Function to send given day's timetable to the user
    '''
    text = std_tt(chat_id=update.effective_chat.id, day= (update.message.text).capitalize())
    if text == 'No Classes':
        update.message.reply_text(text="No Classes on *{}*".format((update.message.text).capitalize()), parse_mode= 'Markdown')
    else :
        text = "*{}*'s Timetable\n".format((update.message.text).capitalize()) + text
        update.message.reply_text(text=text, parse_mode= 'Markdown')
    return DAILY_TT_KEY

##
##  Student ATTENDANCE Menu Functions (Level 2)
##

@cs.send_action(action=ChatAction.TYPING)
def atd_Menu(update,context):
    '''
        Function to send Student Attendance Menu to the user
    '''
    menu = cs.build_menu(buttons=["Get Attendance","Set Attendance","Back"])
    update.message.reply_text(text='''Tell me, what do you want to know about *Your Attendance*?''',parse_mode = 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return ATD_MENU_KEY


@cs.send_action(action=ChatAction.TYPING)
def ivAtdMenu(update,context):
    '''
        Function to send error when user enters Invalid rollno in Student Attendance Menu
    '''
    menu = cs.build_menu(buttons=["Get Attendance","Set Attendance","Back"])
    update.message.reply_text(text='''Sorry 😭, I can't do that\nPlease select from the *Given list*''', parse_mode= 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return ATD_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkSAMC(update,context):
    '''
        Function to send back from std_Atd_Menu_cov to std_Menu_cov
    '''
    Menu(update,context)
    return cs.END

##
##  Student Get attendance Functions
##

## Get attedance reply Functions level-2

@cs.send_action(action=ChatAction.TYPING)
def get_Std_Atd(update,context):
    '''
        Function to send user Attendance to the user
    '''
    atdlst = db.getstdatt(update.effective_chat.id)
    text = "Your Attendance :\nSubject\t:\tpst\t:\tttl\t:\t%\t:\tBnk/atd\n"
    for i in atdlst:
        per = 0
        bnk = None
        if i[2] !=0 :
            per = (int(i[1])/int(i[2]))*100
            per = float("{:.1f}".format(per))
            if (per>75):
                bnk = int((4/3)*int(i[1]))-int(i[2])
            else:
                bnk = (3*int(i[2])-4*int(i[1]))
        text = text + str(i[0]) + '\t:\t' + str(i[1]) + '\t:\t' + str(i[2]) + '\t:\t' + str(per) + "\t:\t" + str(bnk)+"\n"
    update.message.reply_text(text=text)
    return ATD_MENU_KEY

##  Set attedance reply Functions level-2 - Ask for subject

@cs.send_action(action=ChatAction.TYPING)
def subkb_SASUC(update,context):
    '''
        Function to send Subject Keyboard to the user
    '''
    sublst = db.getsubgrd(db.getusrgrd(update.effective_chat.id))
    update.message.reply_text(text='Which subject *Attedence* do you want to set', parse_mode= 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(sublst+['Back'])))
    return SETATD_SUB_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivsub_SASC(update,context):
    '''
        Function to send error when user enters Invalid Subject in Student Attendance Menu
    '''
    sublst = db.getsubgrd(db.getusrgrd(update.effective_chat.id))
    update.message.reply_text(text='''Sorry 😭, I can't do that\nPlease select a Subject from *Your Class*''', parse_mode= 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(sublst+['Back'])))
    return SETATD_SUB_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkSSASC(update,context):
    '''
        Function to send back from std_setAtd_Menu_cov to std_Atd_Menu_cov
    '''
    atd_Menu(update,context)
    return cs.END

##  Set attedance reply Functions level-3 - Ask for status

@cs.send_action(action=ChatAction.TYPING)
def Statkb_SASTC(update,context):
    '''
        Function to send Status Keyboard to the user (i.e Present,Absent)
        -- It also store the subject from the user
    '''
    if (update.message.text).upper() in db.getsubgrd(db.getusrgrd(update.effective_chat.id)):
        context.user_data['SetAtdSub'] = (update.message.text).upper()
        update.message.reply_text(text='So, Tell me the status of *{}*'.format(context.user_data['SetAtdSub']),parse_mode= 'Markdown',
                                        reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(['Present','Absent','Back'])))
        update.message.reply_text(text='''If you want to enter \nthe pnt and ttl class \nseperatly then enter\nThem in this pattern-\n
                                        *pp:tt* \n(ex: 05:10)-\n5 out of 10 classes attended''', parse_mode= 'Markdown')
        return  SETATD_STAT_KEY
    else:
        ivsub_SASC(update,context)
        return  cs.END

@cs.send_action(action=ChatAction.TYPING)
def ivStat_SASC(update,context):
    '''
        Function to send error when user enters Invalid Status in Student Attendance Menu
    '''
    update.message.reply_text(text='''Sorry 😭, I can't do that\nPlease select a Valid status from the List''', parse_mode= 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(['Present','Absent','Back'])))
    return SETATD_STAT_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkSSASTC(update,context):
    '''
        Function to send back from std_setAtd_Stat_cov to std_setAtd_Sub_cov
    '''
    subkb_SASUC(update,context)
    return cs.END

## Set attedance reply Functions level-3 - Process the request

@cs.send_action(action=ChatAction.TYPING)
def set_atd(update,context):
    '''
        Function to Sets attendance for the given subject
    '''
    subnm = context.user_data['SetAtdSub']
    status= update.message.text
    if status == 'Present':
        db.setstdatt(update.effective_chat.id,subnm,1,1)
    elif status == 'Absent':
        db.setstdatt(update.effective_chat.id,subnm,0,1)
    else:
        attend = status.split(':')
        if (int(attend[0]) > int(attend[1])):
            update.message.reply_text(text="Presented classes can't be greaterthan Total Classes\nPlease *Try Again*", parse_mode= 'Markdown')
            return SETATD_STAT_KEY
        elif (int(attend[0]) < 0 or int(attend[1]) < 0):
            update.message.reply_text(text="Presented classes and Total Classes Can't be Negative\nPlease *Try Again*", parse_mode= 'Markdown')
            return SETATD_STAT_KEY
        else:
            db.setstdatt(update.effective_chat.id,subnm,attend[0],attend[1])
    get_Std_Atd(update,context)
    return bkSSASTC(update,context)

##
##  More Menu Functions
##
@cs.send_action(action=ChatAction.TYPING)
def more_Menu(update,context):
    '''
        Function to send More Menu to the user
    '''
    menu = ['Know about\nDeveloper(s)',"Contact\nDeveloper(s)","Back","Logout"]
    if update.effective_chat.id in cs.devjson['devChat_id']:
        menu = ['Message All\n(Dev option)'] + menu
    menu = cs.build_menu(buttons=menu)
    update.message.reply_text(text='''These are the extra options that you can use\nRemember Logging Out Will Delete all Your Data''',parse_mode = 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return MORE_MENU_KEY


@cs.send_action(action=ChatAction.TYPING)
def ivMoreMenu(update,context):
    '''
        Function to send error when user enters Invalid option in More Menu
    '''
    update.message.reply_text(text="Sorry 😭, I can't do that\nPlease select a Valid option from the List",parse_mode  =   'Markdown')
    return MORE_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkSMMC(update,context):
    '''
        Function to send back from std_More_Menu_cov to std_Menu_cov
    '''
    Menu(update,context)
    return cs.END

##  Know your Developer

@cs.send_action(action=ChatAction.TYPING)
def Std_Know_Abt_Dev(update,context):
    '''
        Function to sent dev details to the user
    '''
    cs.KnowAbtDev(update,context)
    return MORE_MENU_KEY

##  Contact Developer

@cs.send_action(action=ChatAction.TYPING)
def std_CT_dev(update,context):
    '''
        Function to contact the Developer
    '''
    update.message.reply_text(text="Send me the message that you want me to pass to Developer(s)",parse_mode  = 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    update.message.reply_text(text="Please Send me your feedback (I will accept Stickers too 😉)",parse_mode  = 'Markdown')
    return CT_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkSCDC(update,context):
    '''
        Function to send back from std_CT_Dev_cov to std_More_Menu_cov
    '''
    more_Menu(update,context)
    return cs.END

@cs.send_action(action=ChatAction.TYPING)
def ivCTDev(update,context):
    '''
        Function to send error when user send Poll to dev
    '''
    update.message.reply_text(text="Please Don't Send polls to developer")
    return CT_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def Snd_Msg_Dev(update,context):
    '''
        Function to send Feedback of user to dev
    '''
    cs.FwdMsgTolst(update,context,cs.devjson['devChat_id'])
    update.message.reply_text(text="I had forwarded your message to developer\nThank you For Your Feedback on me 🤗")
    more_Menu(update,context)
    return cs.END

@cs.send_action(action=ChatAction.TYPING)

##  Student Dev Message to all users

@cs.userauthorized(cs.devjson['devChat_id'])
def std_dev_msg(update,context):
    '''
        Function to contact the Developer
    '''
    update.message.reply_text(text="Send me the message that you want me to pass to Users",parse_mode  = 'Markdown',
                                    reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    return DEV_MSG_KEY

@cs.userauthorized(cs.devjson['devChat_id'])

@cs.send_action(action=ChatAction.TYPING)
def ivDevMsg(update,context):
    '''
        Function to send error when user send Poll to dev
    '''
    update.message.reply_text(text="There was an error, I was unable to forward your message")
    return DEV_MSG_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def bkSDMC(update,context):
    '''
        Function to send back from std_Dev_Msg_cov to std_More_Menu_cov
    '''
    more_Menu(update,context)
    return cs.END

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def snd_dev_msg(update,context):
    '''
        Function to send message to all users
    '''
    cs.FwdMsgTolst(update,context,db.getallstduid() + db.getalltchuid())
    update.message.reply_text(text="I had forwarded your message to all Users")
    more_Menu(update,context)
    return cs.END

##
##   JobQueue Functions
##
@run_async
def callback_daily(context: telegram.ext.CallbackContext):
    '''
        Jobqueue's callback_daily function to send timetable to user at night
    '''
    usrlst = db.getallstduid()
    for i in usrlst:
        text = "*Today's Timetable:*\n" + std_tt(i)
        context.bot.send_message(chat_id=i,text= text,parse_mode = 'Markdown')
        time.sleep(1)
    text = "Total no of STUDENTS using CR_ALT = {}".format(len(usrlst))
    cs.SndMsgTolst(context,cs.devjson['devChat_id'],text)

@run_async
def class_Remindar(context: telegram.ext.CallbackContext):
    '''
        Jobqueue's callback_daily function to send Class_ATD_reminder to user 
    '''
    for i in db.getallstduid():
        periodlst = db.getStdtt(db.getusrgrd(i),datetime.datetime.now(tz= timezone('Asia/Kolkata')).strftime("%A"))
        perlst = [j[0] for j in periodlst]
        if str(context.job.context) in perlst:
            subject = periodlst[perlst.index(context.job.context)][1]
            keyboard = [
                InlineKeyboardButton("Yes",callback_data= str('1'+subject)),
                InlineKeyboardButton("No",callback_data= str('0'+subject)),
                InlineKeyboardButton("Cancel",callback_data= str('2'+subject))
            ]
            reply_markup = InlineKeyboardMarkup(cs.build_menu(keyboard))
            context.bot.send_message(chat_id=i, text= "Did you attend the class of subject {} @ {}".format(subject,context.job.context),
                        reply_markup=reply_markup)
            time.sleep(1)

def inline_set_atd(update,context):
    '''
        Inline function to set attendance
    '''
    query = update.callback_query
    query.answer()
    if query.data[:1] == '1':
        db.setstdatt(update.effective_chat.id,query.data[1:],1,1)
        query.edit_message_text(text="You were PRESENT for {} class".format(query.data[1:]))
    elif query.data[:1] == '0':
        db.setstdatt(update.effective_chat.id,query.data[1:],0,1)
        query.edit_message_text(text="You were Absent for {} class".format(query.data[1:]))
    else:
        query.edit_message_text(text="{} class was CANCELED".format(query.data[1:]))

@cs.send_action(action=telegram.ChatAction.TYPING)
def std_logout(update,context):
    '''
        Function to Logout the user
    '''
    db.rmvstd(update.effective_chat.id)
    update.message.reply_text(text='''You have logged out Successfully\nByeBye..👋\n''',parse_mode = 'Markdown',reply_markup=telegram.ReplyKeyboardRemove())
    update.message.reply_text(text='''Send */start* to restart the bot''',parse_mode = 'Markdown')
    
    return STOPPING
