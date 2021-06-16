import datetime, time, json
import telegram
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
import logging
from pytz import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatAction
import dbCreate as db
import codeSnippets as cs

## Conversation dict Constants keys
MAIN_MENU_KEY, AUTH_KEY, MAIN_MENU_KEY, TT_MENU_KEY, DAILY_TT_KEY, STOPPING, GRADE_TT_GRD_KEY, GRADE_TT_DAY_KEY, ANN_MENU_KEY, CR8CLS_GRD_KEY= range(220,230)
CR8CLS_Day_KEY, CR8CLS_PERD_KEY, CXLCLS_DAY_KEY, CXLCLS_GSP_KEY, MSGSTD_GRD_KEY, MSGSTD_MSG_KEY, MORE_MENU_KEY, CT_MENU_KEY,DEV_MENU_KEY,DEV_MSG_MENU_KEY, DEV_MSG_KEY, RETURN_MENU, DEV_RMV_ACC_KEY, DEV_MNG_CR_KEY= range(230,244)

## Jobqueue Functions
def update_Day_tt(context):
    '''
        Jobqueue's Updaytt function
        it will up date day timetable on working days after 04:30 pm
    '''
    cs.jsonupd()
    day = datetime.datetime.now(tz=timezone('Asia/Kolkata')).strftime("%A")
    db.upddaytt(day)
    tchlst = db.getalltchuid()
    for i in tchlst:
        text = "Professor, Next {}\ntimetable was updated.\nYou can make changes in the timetable now".format(day)
        context.bot.send_message(chat_id=i, text=text)
        time.sleep(.2)
    for i in db.getCR():
        text = "CR, Next {}\ntimetable was updated.\nYou can make changes in the timetable now".format(day)
        chat_id = db.getStdChatId(i)
        if chat_id:
            context.bot.send_message(chat_id=i, text=text)
        time.sleep(.2)
    del day 

def callback_daily(context):
    '''
        Jobqueue's callback_daily function
    '''
    tchlst = db.getalltchuid()
    tchcnt = len(tchlst)

    for i in tchlst:
        day = datetime.datetime.now(tz=timezone('Asia/Kolkata')).strftime("%A")
        text = "Today's Timetable\n"+ tch_tt(i,day)
        context.bot.send_message(chat_id=i, text=text)
        time.sleep(.2)
    text = "Total no of Professor using CR_ALT = {}".format((tchcnt))
    for i in cs.devjson['devChat_id']:
        context.bot.send_message(chat_id=i, text=text)

@cs.send_action(action=ChatAction.TYPING)
def empid(update, context):
    '''
        Function to ask the user to enter his emp_id
    '''
    update.message.reply_text(text='''Please send me,\nYour IIITT Email ID\nto Log you in.''',
                                reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    return AUTH_KEY

@cs.send_action(action=ChatAction.TYPING)
def Authentication(update, context):
    '''
        Function to athenticate the user as teacher
    '''
    updtch = False
    if db.chktch(update.effective_chat.id) != None:
        updtch = True
    emp_id = db.tchsetup(update.effective_chat.id,(update.message.text),updtch)
    if emp_id :
        context.user_data['updtch'] = False
        update.message.reply_text(text="I linked Your Email Id {},\nto your account".format(emp_id))
        update.message.text = emp_id
        update.message.reply_text(text = "Select Menu to see the list of things that you can ask me.",
                                    reply_markup=telegram.ReplyKeyboardMarkup([['Menu']]))
        return cs.STOP  
    else:
        return ivempid(update, context)
    
@cs.send_action(action=ChatAction.TYPING)
def ivempid(update, context):
    '''
        Function to send error when user enters Invalid emp_id in Authentication Menu
    '''
    update.message.reply_text(text='''Its NOT a valid Email Id or\nSomeone has Already registered with this Email ID.'''+
                                '''Please send me\nA Valid Email ID.\nIf someone else is using your account please contact the Devoloper''',
                                reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    return AUTH_KEY

##
##   Teacher Menu Functions (Level 1)
##

#@cs.userauthorized(db.getalltchuid())
@cs.send_action(action=ChatAction.TYPING)
def Menu(update,context):
    '''
        Function to send Teacher Menu to the user
    '''
    menu = (["Timetable","Announcements","More"])
    if update.effective_chat.id in cs.devjson['devChat_id']:
        menu = menu  + ['DEV Menu']
    menu = cs.build_menu(buttons=menu)
    update.message.reply_text(text='''Ask me what you want to know from the Below list''',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return MAIN_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivmenu(update,context):
    '''
        Function to send error when user Enters an Invalid option in Teacher Main Menu
    '''
    update.message.reply_text(text='''Sorry, I can't do that''')
    return Menu(update,context)

##
##  Teacher Timetable Menu Functions (Level 2)
##

@cs.send_action(action=ChatAction.TYPING)
def tt_Menu(update,context):
    '''
        Function to send Teacher Timetable Menu to the user
    '''
    menu = cs.build_menu(buttons=["Today's Timetable","Daily Timetable","Grade Timetable","Back"])
    update.message.reply_text(text='''what do you want to know about Your Timetable?''',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return TT_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivTTMenu(update,context):
    '''
        Function to send error when user enters Invalid Option in Teacher Timetable Menu
    '''
    menu = cs.build_menu(buttons=["Today's Timetable","Daily Timetable","Grade Timetable","Back"])
    update.message.reply_text(text='''Sorry, I can't do that.\nPlease select from the Given list''',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return TT_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkTTMC(update,context):
    '''
        Function to send back from tch_TT_Menu_cov to tch_Menu_cov
    '''
    Menu(update,context)
    return cs.END

##  Student Dev Message to users
@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def bkTDMENUC(update,context):
    '''
        Function to send back from tch_More_Menu_cov to Tch_Menu_cov
    '''
    Menu(update,context)
    return cs.END
##
##  Teacher Timetable Reply Functions
##

def tch_tt(chat_id,day):
    '''
        Function to Return Teacher Timetable as a string
    '''
    perlst=db.getTeachtt(chat_id,day)
    text = "___Time___ :  Batch  : Subject\n"
    no_cls = True
    for i in perlst:
        no_cls  =   False
        text = text + i[0] + " : " + i[1]+ " : " + i[2]+"\n"
    if no_cls:
        return "No Classes"
    else:
        return text

#   Today Timetable Reply Functions (level 2)

@cs.send_action(action=ChatAction.TYPING)
def td_Tch_TT(update,context):
    '''
        Function to send Today's Timetable to the user
    '''
    text = tch_tt(update.effective_chat.id,update.effective_message.date.astimezone(timezone('Asia/Kolkata')).strftime("%A"))
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
        Function to send KeyBoard of Days to the user in Teacher_Timetable/Daily_Timetable path
    '''
    text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
    update.message.reply_text(text='''Which day Timetable do you want ?''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    return DAILY_TT_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivday_DTMC(update,context):
    '''
        Function to send error when user enters Invalid day in Teacher_Timetable/Daily_Timetable path
    '''
    text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
    update.message.reply_text(text='''Its not a Day from the list.\nPlease send me a day from the list''',
                            reply_markup=telegram.ReplyKeyboardMarkup(text))

    return DAILY_TT_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkDTMC(update,context):
    '''
        Function to send back from tch_DailyTT_Menu_cov to tch_TT_Menu_cov
    '''
    tt_Menu(update,context)
    return cs.END

##  Daily Timetable Reply Function(level 3) - Send Timetable to user

@cs.send_action(action=ChatAction.TYPING)
def day_tch_tt (update,context):
    '''
        Function to send given day's teacher timetable to the user
    '''
    text = tch_tt(chat_id = update.effective_chat.id,day = (update.message.text).capitalize())#
    if text == "No Classes":
        update.message.reply_text(text="No Classes on {}".format((update.message.text).capitalize()))
    else:
        text = "{}'s Timetable\n".format((update.message.text).capitalize()) + text
        update.message.reply_text(text=text)
    return DAILY_TT_KEY

##  Grade Timetable Reply Function(level 3) - Send Grade Keyboard to user
@cs.send_action(action=ChatAction.TYPING)
def gradeKb_GTGC(update,context):
    '''
        Function to send KeyBoard of Subjects to the user in Teacher_Timetable/Grade_Timetable path
    '''  
    tchgrdsublst = db.tchgrdsub(update.effective_chat.id)
    tchgrd = set()
    for i in tchgrdsublst:
        tchgrd.add(i[0])
    context.user_data['tchGrdTTGrdLst'] = list(tchgrd)
    update.message.reply_text(text='''Which Grade Timetable do you want ?''', 
                            reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(context.user_data['tchGrdTTGrdLst']+['Back'])))
    return GRADE_TT_GRD_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivgrade_GTGC(update,context):
    '''
        Function to send error when user enters Invalid Grade in Teacher_Timetable/Grade_Timetable path
    '''
    update.message.reply_text(text='''Its not a Grade from the list''')
    return gradeKb_GTGC(update,context)

@cs.send_action(action=ChatAction.TYPING)
def bkGTGC(update,context):
    '''
        Function to send back from tch_GradeTT_Menu_cov to tch_TT_Menu_cov
    '''
    tt_Menu(update,context)
    return cs.END

##  Grade Timetable Reply Function(level 3) - Send Day Keyboard to user

@cs.send_action(action=ChatAction.TYPING)
def dayKb_GTDC (update,context):
    '''
        Function to send KeyBoard of Days to the user in Teacher_Timetable/Daily_Timetable path
    '''
    if (update.message.text).upper() in context.user_data['tchGrdTTGrdLst']:
        context.user_data['GetGradeTTGrade'] = (update.message.text).upper()
        text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
        update.message.reply_text(
        text='''Which day Timetable of {} do you want ?'''.format((update.message.text).upper()), reply_markup=telegram.ReplyKeyboardMarkup(text))
        return GRADE_TT_DAY_KEY
    else:
        update.message.reply_text(text='''I know you won't attend this class.\nSo, I can't Tell you ''')
        return cs.END
    

@cs.send_action(action=ChatAction.TYPING)
def ivday_GTDC(update,context):
    '''
        Function to send error when user enters Invalid day in Teacher_Timetable/Daily_Timetable path
    '''
    text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
    update.message.reply_text(text='''Its not a Day from the list.\nPlease sent me a day from the list''',
                     reply_markup=telegram.ReplyKeyboardMarkup(text))
    return GRADE_TT_DAY_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkGTDC(update,context):
    '''
        Function to send back from tch_GrdTT_Day_cov to tch_GrdTT_Grade_cov
    '''
    gradeKb_GTGC(update,context)
    return cs.END

## Send Grade Timetable to user

def day_grd_tch_tt (update,context):
    '''
        Function to send given grade's timetable to the user
    '''
    perlst  =   db.getStdtt(context.user_data['GetGradeTTGrade'],(update.message.text).capitalize())
    text    =   "Timetable of {} on {}:\n".format(context.user_data['GetGradeTTGrade'],(update.message.text).capitalize())
    text    =   text + "___Time___ : Subject\n"
    no_cls  =   True 
    for i in perlst:
        no_cls  =   False
        text    =   text + i[0] + " : " + i[1]+"\n"
    if no_cls:
        text=  "No Classes"
    update.message.reply_text(text=text)
    return GRADE_TT_DAY_KEY

##
##  Announcement Menu Functions
##

@cs.send_action(action=ChatAction.TYPING)
def ann_Menu (update,context):
    '''
        Function to send Teacher's Announcement Menu to the user
    '''
    menu = cs.build_menu(buttons=["Create Class","Cancel Class","Message Students","Back"])
    update.message.reply_text(text='''what you want to Announce now?''',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return ANN_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivAnnMenu(update,context):
    '''
        Function to send error when user enters Invalid Option in Teacher Announcement Menu
    '''
    menu = cs.build_menu(buttons=["Create Class","Cancel Class","Message Students","Back"])
    update.message.reply_text(text='''Sorry, I can't do that.\nPlease select from the Given list''',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return ANN_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkAnnMC(update,context):
    '''
        Function to send back from tch_Ann_Menu_cov to tch_Menu_cov
    '''
    Menu(update,context)
    return cs.END

##  Create Class Functions (level 3) - Send Grade:Subject Keyboard to user

@cs.send_action(action=ChatAction.TYPING)
def grdsubkb_CCGC(update,context):
    '''
        Function to send KeyBoard of Grade:Subject to the user in Teacher_Announcement/Create_Class path
    '''
    tchgrdsublst = db.tchgrdsub(update.effective_chat.id)
    tchgrd = set()
    for i in tchgrdsublst:
        tchgrd.add(i[0]+":"+i[1])
    context.user_data['tchgrdsubkb'] = list(tchgrd)
    update.message.reply_text(text='''Tell me, For which Grade and subject you want me to create class ?''', 
                            reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(context.user_data['tchgrdsubkb']+['Back'])))
    return CR8CLS_GRD_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivgrdsub_CCGC(update,context):
    '''
        Function to send error when user enters Invalid day in Teacher_Timetable/Daily_Timetable path
    '''
    update.message.reply_text(text='''Its not a Grade and Subject from the list.\nPlease sent me a Grade and Subject from the list''',
                             reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(context.user_data['tchgrdsubkb']+['Back'])))
    return CR8CLS_GRD_KEY


def bkCCGC(update,context):
    '''
        Function to send back from tch_CR8Cls_Grd_cov to tch_Ann_Menu_cov
    '''
    ann_Menu(update,context)
    return cs.END

##  Create Class Functions (level 4) - Send Days Keyboard to user

@cs.send_action(action=ChatAction.TYPING)
def dayKb_CCDC(update,context):
    '''
        Function to send KeyBoard of Days to the user in Teacher_Announcements/Create_Class path
    '''
    if ((update.message.text) in context.user_data['tchgrdsubkb']) or (update.message.text) == 'Back':
        if (update.message.text) != 'Back':
            context.user_data['CR8ClsGrdSub'] = (update.message.text).upper()
        text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
        update.message.reply_text(
            text='''Which day do you want to take class for {}?'''.format((update.message.text)), reply_markup=telegram.ReplyKeyboardMarkup(text))
        return CR8CLS_Day_KEY
    else:
        update.message.reply_text(text='''I know you won't attend this class.\nSo, I can't DO IT ''')
        return cs.END
    

@cs.send_action(action=ChatAction.TYPING)
def ivday_CCDC(update,context):
    '''
        Function to send error when user enters Invalid day in Teacher_Announcements/Create_Class path
    '''
    text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
    update.message.reply_text(
            text='''Its not a Day from the list.\nPlease sent me a day from the list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    return CR8CLS_Day_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkCCDC(update,context):
    '''
        Function to send back from tch_CR8Cls_Day_cov to tch_CR8Cls_Grd_cov
    '''
    grdsubkb_CCGC(update,context)
    return cs.END

##  Create Class Functions (level 5) - Send Periods Keyboard to user

@cs.send_action(action=ChatAction.TYPING)
def period_CCPC(update,context):
    '''
        Function to send KeyBoard of Periods to the user in Teacher_Announcements/Create_Class path
    '''
    context.user_data['CR8ClsDay'] = (update.message.text)
    availableperlst = list()
    stdperiodlst = [i[0] for i in db.getStdtt((context.user_data['CR8ClsGrdSub']).split(':')[0],context.user_data['CR8ClsDay'])]
    tchperiodlst = [i[0] for i in db.getTeachtt((update.effective_chat.id),context.user_data['CR8ClsDay'])]
    for i in cs.datajson['periodlst']:
        
        if (i not in stdperiodlst) and (i not in tchperiodlst):
            availableperlst.append(i)
    context.user_data['availableperlst'] = availableperlst
    update.message.reply_text(text='''Which period of {} do you want ?'''.format((update.message.text)),
                                reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(context.user_data['availableperlst']+['Back'])))
    return CR8CLS_PERD_KEY
    

@cs.send_action(action=ChatAction.TYPING)
def ivperiod_CCPC(update,context):
    '''
        Function to send error when user enters Invalid Period in Teacher_Announcements/Create_Class path
    '''
    update.message.reply_text(text='''Its not a period from the list.\nPlease sent me a period from the list''',
                                reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(context.user_data['availableperlst']+['Back'])))
    return CR8CLS_PERD_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkCCPC(update,context):
    '''
        Function to send back from tch_CR8Cls_Perd_cov to tch_CR8Cls_Day_cov
    '''
    dayKb_CCDC(update,context)
    return cs.END

## InlineKeyboard for Class Creation
@cs.send_action(action=ChatAction.TYPING)
def conf_CR8cls_CCPC(update,context):
    '''
        Function to Ask conformation before class creation
    '''
    if (update.message.text) in context.user_data['availableperlst']:
        inlneCBdata = context.user_data['CR8ClsGrdSub'] + ":" + update.message.text + ":" + context.user_data['CR8ClsDay'] + ':' + update.message.from_user.first_name
        # grade:subject:period:day:Name
        tcdata = inlneCBdata.split(':')
        text='''You want me to Create Class for \nsubject {} of {} \non {} : {}'''.format(tcdata[1].upper(),tcdata[0].upper(),tcdata[3],tcdata[2])
    
        keyboard = [
                                    [InlineKeyboardButton("Yes",callback_data= 'CR8CLS:' + inlneCBdata),
                                    InlineKeyboardButton("No",callback_data= 'CR8CLS:No' ) ],
                                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text = text, reply_markup=reply_markup)
        Menu(update,context)
        return STOPPING
    else:
        update.message.reply_text(text='''This class was already taken.\nPlease Take another class''')
        return CR8CLS_PERD_KEY
        


##  Cancel Class Functions (level 3) - Send Days Keyboard to user

@cs.send_action(action=ChatAction.TYPING)
def daykb_CxCDC(update,context):
    '''
        Function to send KeyBoard of Days to the user in Teacher_Announcements/Cancel_Class path
    '''
    text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
    update.message.reply_text(text='''Which day class do you want to cancel ?''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    return CXLCLS_DAY_KEY
    

@cs.send_action(action=ChatAction.TYPING)
def ivday_CxCDC(update,context):
    '''
        Function to send error when user enters Invalid day in Teacher_Announcements/Cancel_Class path
    '''
    text = cs.build_menu(buttons=(cs.datajson['daylst']+['Back']))
    update.message.reply_text(text='''Its not a Day from the list.\nPlease sent me a day from the list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    return CXLCLS_DAY_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkCxCDC(update,context):
    '''
        Function to send back from tch_CXLCls_Day_cov to tch_Ann_Menu_cov
    '''
    ann_Menu(update,context)
    return cs.END

##  Cancel Class Functions (level 4) - Send Grade,Subject,Period Keyboard to user

@cs.send_action(action=ChatAction.TYPING)
def GSP_CxCGC(update,context):
    '''
        Function to send KeyBoard of Period,Grade,Subject to the user in Teacher_Announcements/Cancel_Class path
    '''
    context.user_data['CXLClsDay'] = (update.message.text)
    context.user_data['avGSPlst'] = [i[0] + ":" + i[1] + ":" + i[2] for i in db.getTeachtt((update.effective_chat.id),context.user_data['CXLClsDay'])]
    update.message.reply_text(text='''Which Class do you want to cancel on {} ?'''.format((update.message.text)),
                                reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(context.user_data['avGSPlst']+['Back'],n_cols=1)))
    return CXLCLS_GSP_KEY
    

@cs.send_action(action=ChatAction.TYPING)
def ivGSP_CxCGC(update,context):
    '''
        Function to send error when user enters Invalid Class in Teacher_Announcements/Cancel_Class path
    '''
    update.message.reply_text(text='''Its not a Class from the list.\nPlease sent me a class from the list''',
                                reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(context.user_data['avGSPlst']+['Back'],n_cols=1)))
    return CXLCLS_GSP_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkCxCGC(update,context):
    '''
        Function to send back from tch_CXLCls_GSP_cov to tch_CXLCls_Day_cov
    '''
    daykb_CxCDC(update,context)
    return cs.END

##  InlineKeyboard for Class Cancelation

@cs.send_action(action=ChatAction.TYPING)
def conf_CXLcls_CxCGC(update,context):
    '''
        Function to Ask conformation before class creation
    '''
    if (update.message.text) in context.user_data['avGSPlst']:
        inlneCBdata = update.message.text + ":" + context.user_data['CXLClsDay'] + ":"+ update.message.from_user.first_name 
        # period:grade:subject:day:Name
        tcdata = inlneCBdata.split(':')
        text='''You want me to Cancel Class for \nsubject {} of {} \non {} : {}'''.format(tcdata[2].upper(),tcdata[1].upper(),tcdata[3],tcdata[0])
    
        keyboard = [
                                    [InlineKeyboardButton("Yes",callback_data= 'CXLCLS:' + inlneCBdata),
                                    InlineKeyboardButton("No",callback_data= 'CXLCLS:No' ) ],
                                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text = text, reply_markup=reply_markup)
        Menu(update,context)
        return STOPPING
    else:
        update.message.reply_text(text='''The Class you told me Cancel does not exists''')
        return CXLCLS_GSP_KEY
        
##  Message Students Functions (level 3) - Send Grade Keyboard to user

@cs.send_action(action=ChatAction.TYPING)
def avgrdkb_MSGC(update,context):
    '''
        Function to send KeyBoard of Subjects to the user in Teacher_Timetable/Message_students path
    '''  
    tchgrdsublst = db.tchgrdsub(update.effective_chat.id)
    context.user_data['tchMsgStdGrdLst'] = list({grd[0] for grd in tchgrdsublst})
    update.message.reply_text(text='''For which grade do you want to send the message ?''', 
                                reply_markup=telegram.ReplyKeyboardMarkup(cs.build_menu(context.user_data['tchMsgStdGrdLst']+['Message All','Back'])))
    return MSGSTD_GRD_KEY

@cs.send_action(action=ChatAction.TYPING)
def ivGrd_MSGC(update,context):
    '''
        Function to send error when user enters Invalid Grade in Teacher_Timetable/Message_students path
    '''
    update.message.reply_text(text='''Its not a Grade from the list''')
    return avgrdkb_MSGC(update,context)

@cs.send_action(action=ChatAction.TYPING)
def bkMSGC(update,context):
    '''
        Function to send back from tch_MsgStd_Grd_cov to tch_Ann_Menu_cov
    '''
    ann_Menu(update,context)
    return cs.END

##  Message Students Functions (level 4) - Ask use to send message

@cs.send_action(action=ChatAction.TYPING)
def msgstd_MSMC(update,context):
    '''
        Function to ask the user to Send message that user want to pass to students
    '''
    if ((update.message.text) in (context.user_data['tchMsgStdGrdLst'] + ['Message All','Back'])) :
        if (update.message.text) != 'Back':
            context.user_data['tchMsgStdGrd'] = (update.message.text)
        update.message.reply_text(text="Send me the message that you want me to pass to Students",
                                    reply_markup=telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton(text='Send Poll',request_poll=telegram.KeyboardButtonPollType(type=None))],['Back']]))
        return MSGSTD_MSG_KEY
    else:
        update.message.reply_text(text='''I know you won't attend this class.\nSo, I can't DO IT''')
        return cs.END

@cs.send_action(action=ChatAction.TYPING)
def ivmsg_MSMC(update,context):
    '''
        Function to send error when user send Commands
    '''
    update.message.reply_text(text="There was an error Please try again")
    avgrdkb_MSGC(update,context)
    return cs.END

@cs.send_action(action=ChatAction.TYPING)
def bkMSMC(update,context):
    '''
        Function to send back from tch_MsgStd_Msg_cov to tch_MsgStd_Grd_cov
    '''
    avgrdkb_MSGC(update,context)
    return cs.END

@cs.send_action(action=ChatAction.TYPING)
def snd_MsgStd_msg(update,context):
    '''
        Function to send user msg to given students in class
    '''
    usrlst = list()
    if context.user_data['tchMsgStdGrd'] == 'Message All':
        grade = list({grade[0] for grade in db.tchgrdsub(update.effective_chat.id)})
        for grd in grade:
            usrlst = usrlst + db.grdstdid(grd) 
        cs.FwdMsgTolst(update = update,context = context, usrlst = usrlst, is_teacher = True)
    else:
        grade   = context.user_data['tchMsgStdGrd']
        usrlst  = db.grdstdid(grade)
        cs.FwdMsgTolst(update = update,context = context, usrlst = usrlst, is_teacher = True)
    update.message.forward(update.effective_chat.id)
    update.message.reply_text(text="I had forwarded your message to {} Student(s) in {} ".format(len(usrlst), grade))
    Menu(update,context)
    return STOPPING

##
##  More options Functions
##

@cs.send_action(action=ChatAction.TYPING)
def more_Menu(update,context):
    '''
        Function to send More Menu to the user
    '''
    menu = ['Know about\nDeveloper(s)',"Contact\nDeveloper(s)","Back","Logout"]
    menu = cs.build_menu(buttons=menu)
    update.message.reply_text(text='''These are the extra options\nthat you can use.\nRemember Logging Out Will\nDelete all Your Data''',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return MORE_MENU_KEY


@cs.send_action(action=ChatAction.TYPING)
def ivMoreMenu(update,context):
    '''
        Function to send error when user enters Invalid option in More Menu
    '''
    update.message.reply_text(text="Sorry, I can't do that.\nPlease select a Valid option from the List")
    return MORE_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkTMMC(update,context):
    '''
        Function to send back from Tch_More_Menu_cov to Tch_Menu_cov
    '''
    Menu(update,context)
    return cs.END

#   Know about your developer

@cs.send_action(action=ChatAction.TYPING)
def Tch_Know_Abt_Dev(update,context):
    '''
        Function to sent dev details to the user
    '''
    cs.KnowAbtDev(update,context)
    return MORE_MENU_KEY

## Contact developer Functions

@cs.send_action(action=ChatAction.TYPING)
def tch_CT_dev(update,context):
    '''
        Function to contact the Developer
    '''
    update.message.reply_text(text="Send me the message that you want me to pass to Developer(s)\nTip: Send me a message if you want a permanent change in time table",
                                    reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    return CT_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def bkTCDC(update,context):
    '''
        Function to send back from tch_CT_Dev_cov to tch_More_Menu_cov
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
    update.message.reply_text(text="I had forwarded your message to developer.\nThank you For Your Feedback on me ")
    more_Menu(update,context)
    return cs.END

##  Teacher Dev Message to users
@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def tch_devmenu_msg(update,context):
    '''
        Function to send dev Msg Menu to the user
    '''
    menu = ['Students',"Teachers","All Users","Back"]
    menu = cs.build_menu(buttons=menu)
    update.message.reply_text(text='''Please Tell me whom you want to send the message.''',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return DEV_MENU_KEY


@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def ivDevMenu(update,context):
    '''
        Function to send error when user enters Invalid option in More Menu
    '''
    update.message.reply_text(text="Sorry, I can't do that.\nPlease select a Valid option from the List")
    return DEV_MENU_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def bkTDMUC(update,context):
    '''
        Function to send back from tch_More_Menu_cov to Tch_Menu_cov
    '''
    more_Menu(update,context)
    return cs.END

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def tch_dev_msg(update,context):
    '''
        Function to contact the Developer
    '''
    context.user_data['tchDevUsrOpt'] = update.message.text
    update.message.reply_text(text="Send me the message that you want me to pass to {}".format(update.message.text),
                                    reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    return DEV_MSG_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def ivDevMsg(update,context):
    '''
        Function to send error when Somthing happens
    '''
    update.message.reply_text(text="There was an error, I was unable to forward your message")
    return DEV_MSG_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def bkTDMC(update,context):
    '''
        Function to send back from tch_Dev_Msg_cov to tch_Dev_Menu_cov
    '''
    tch_devmenu_msg(update,context)
    return cs.END

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=ChatAction.TYPING)
def snd_dev_msg(update,context):
    '''
        Function to send message to all users
    '''
    if context.user_data['tchDevUsrOpt'] == 'Students':
        usrlst = db.getallstduid()
    elif context.user_data['tchDevUsrOpt'] == 'Teachers':
        usrlst = db.getalltchuid()
    else:
        usrlst = db.getallstduid() + db.getalltchuid()
    cs.FwdMsgTolst(update = update,context = context, usrlst = usrlst, is_dev = True)
    update.message.reply_text(text="I had forwarded your message to {} User(s)".format(len(usrlst)))
    tch_devmenu_msg(update,context)
    return cs.END

#   LogOut the user 

@cs.send_action(action=telegram.ChatAction.TYPING)
def tch_logout(update,context):
    '''
        Function to Logout the user
    '''
    db.rmvtch(update.effective_chat.id)
    update.message.reply_text(text='''You have logged out Successfully.\nByeBye..''',reply_markup=telegram.ReplyKeyboardRemove())
    update.message.reply_text(text='''Send /start to restart the bot''')
    return STOPPING

#   Return To Menu Functon

## Dev functions

## DEV Menu Functions
@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def dev_Menu(update,context):
    '''
        Developer's Menu function
    '''
    menu = cs.build_menu(buttons=["No of Users","Manage CR","Message Users","Remove User\nAccount","Json Update",'Back'])
    update.message.reply_text( text = '''Ask me what you want to do from the Below list''',reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return DEV_MENU_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def ivDMenu(update,context):
    '''
        Function to send error when user enters Invalid option in Dev Menu
    '''
    update.message.reply_text(text="Sorry, I can't do that.\nPlease select a Valid option from the List")
    if update.message.text == "/menu":
        update.message.reply_text(text="/menu command is not supported in dev options")
    return DEV_MENU_KEY

@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def dev_no_usr(update,context):
    '''
        Developer's function - No of Users
    '''
    stdcnt = len(db.getallstduid())
    tchcnt = len(db.getalltchuid())
    text = '''Total no of Students = {}\nTotal no of Teachers = {}\nTotal no of devs = {}\nTotal no of users = {}'''.format(stdcnt,tchcnt,len(cs.devjson['devChat_id']),stdcnt+tchcnt)
    update.message.reply_text(text = text)
    return DEV_MENU_KEY

## DEV Option - Message users

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def devmenu_msg(update,context):
    '''
        Function to send dev Msg Menu to the user
    '''
    menu = ['Students',"Teachers","All Users","Back"]
    menu = cs.build_menu(buttons=menu)
    update.message.reply_text(text='''Please Tell me whom you want to send the message.''',
                                    reply_markup=telegram.ReplyKeyboardMarkup(menu))
    return DEV_MSG_MENU_KEY


@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def ivDevMsgMenu(update,context):
    '''
        Function to send error when user enters Invalid option in dev msg Menu
    '''
    update.message.reply_text(text="Sorry, I can't do that.\nPlease select a Valid option from the List")
    return DEV_MSG_MENU_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def bkDMMC(update,context):
    '''
        Function to send back from DEV_MSG_Menu_cov to DEV_Menu_cov
    '''
    dev_Menu(update,context)
    return cs.END

## Dev msg menu - select grade 

@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def dev_msg_usr(update,context):
    '''
        Function to contact the Developer
    '''
    context.user_data['DevUsrOpt'] = update.message.text
    update.message.reply_text(text="Send me the message that you want me to pass to {}".format(update.message.text),
                                    reply_markup=telegram.ReplyKeyboardMarkup([['Back'],[telegram.KeyboardButton(text='Send Poll',request_poll=telegram.KeyboardButtonPollType(type=None))]]))
    return DEV_MSG_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def ivDevMsg(update,context):
    '''
        Function to send error when user se to dev
    '''
    update.message.reply_text(text="There was an error, I was unable to forward your message")
    return DEV_MSG_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def bkSDMC(update,context):
    '''
        Function to send back from std_Dev_Msg_cov to std_Dev_Menu_cov
    '''
    devmenu_msg(update,context)
    return cs.END

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def ivDevRmvAcc(update,context):
    '''
        Function to send error when user enters Invalid data in dev_rmv_usr 
    '''
    update.message.reply_text(text="Sorry, I can't do that.\nThere was no such user with data - {}".format(update.message.text))
    return DEV_RMV_ACC_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def snd_dev_msg(update,context):
    '''
        Function to send message to all users
    '''
    if context.user_data['DevUsrOpt'] == 'Students':
        usrlst = db.getallstduid()
    elif context.user_data['DevUsrOpt'] == 'Teachers':
        usrlst = db.getalltchuid()
    elif context.user_data['DevUsrOpt'] == 'All Users':
        usrlst = db.getallstduid() + db.getalltchuid()
    elif context.user_data['DevUsrOpt'] in db.getalltchempid():
        usrlst = [db.getTchChatId(context.user_data['DevUsrOpt'])]
    elif context.user_data['DevUsrOpt'] in db.getallstdrollno():
        usrlst = [db.getStdChatId(context.user_data['DevUsrOpt'])]
    else:
        usrlst = [context.user_data['DevUsrOpt']]
    cs.FwdMsgTolst(update = update,context = context, usrlst = usrlst, is_dev = True)
    update.message.reply_text(text="I had forwarded your message to {} User(s)".format(len(usrlst)))
    devmenu_msg(update,context)
    return cs.END

@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def devgetRmvUsrid(update,context):
    '''
        Function to Ask dev to send chat id or roll no or emp id to remove account
    '''
    update.message.reply_text(text="Send me send the RollNo (or) EmailId (or) ChatId of the user you want to remove",
                                    reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    return DEV_RMV_ACC_KEY

@cs.userauthorized(cs.devjson['devChat_id'])
@cs.send_action(action=telegram.ChatAction.TYPING)
def bkDRAC(update,context):
    '''
        Function to send back from Dev_RMV_ACC_cov to DEV_Menu_cov
    '''
    dev_Menu(update,context)
    return cs.END

@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def devRmvUsr(update,context):
    '''
        Function to remove account of the user with the given chat id or roll no or emp id to remove account
    '''
    usrid = None
    if update.message.text.lower() in db.getalltchempid():
        usrid = db.getTchChatId(update.message.text.lower())
        db.rmvtch(usrid)
    elif update.message.text.upper() in db.getallstdrollno():
        usrid = db.getStdChatId(update.message.text.upper())
        db.rmvstd(usrid)
    elif update.message.text in db.getalltchuid():
        usrid = update.message.text
        db.rmvtch(update.message.text)
    elif update.message.text in db.getalltchuid():
        usrid = update.message.text
        db.rmvstd(update.message.text)
    if usrid == None:
        update.message.reply_text(text="There was no such user with given data - {}".format(update.message.text))
    else:
        context.bot.send_message(chat_id =  usrid, text = "We got a complaint that you are using another user's account.\nSo,We are removing your account.\
                                                        Please contact the developer for any query\nPlease send /start to start the bot",reply_markup=telegram.ReplyKeyboardRemove())
        update.message.reply_text(text="Account of {} removed successfully.".format(update.message.text))
    return bkDRAC(update,context)

## Dev Managing CR devgetCRRoll

@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def devgetCRRoll(update,context):
    '''
        Function to Ask Roll no of CR 
    '''
    text = ''
    roll_no = db.getCR()
    for i in roll_no:
        text = text + '\n {} - {}'.format(roll_no.split('U')[0],roll_no)
    
    update.message.reply_text(text='''List of CR Roll No :{}\nPlease Enter The Roll no of the CR.\nIf the roll no is already in the above list then \
                                        I will delete it else i will add it\nNote : one grade can have only one CR'''.format(text),
                                        reply_markup=telegram.ReplyKeyboardMarkup([['Back']]))
    return DEV_MNG_CR_KEY

@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def devMngCR(update,context):
    '''
        Function to Add and Remove CR from DB 
    '''
    roll_no = update.message.text.upper()
    if roll_no in db.getCR():
        db.delCR(roll_no)
        if db.getStdChatId(roll_no):
                context.bot.send_message(chat_id = db.getStdChatId(roll_no) , text = 'You are No longer a CR now.\nContact Dev if you want to be a CR')
        update.message.reply_text(text='''{} removed from CR list successfully'''.format(roll_no))
        return bkDRAC(update,context)
    else:
        rn = db.addCR(roll_no)
        if roll_no == rn:
            if db.getStdChatId(roll_no):
                context.bot.send_message(chat_id = db.getStdChatId(roll_no) , text = 'Congrats! You are A CR Now.You can Find CR Menu in Main Menu(/menu)')
            update.message.reply_text(text='''CR Added successfully''')
            return bkDRAC(update,context)
        else:
            update.message.reply_text(text='''CR Already exists for {} with Roll no {}'''.format(roll_no.split('U')[0],roll_no))
            return DEV_MNG_CR_KEY

@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def ivDevMngCR(update,context):
    '''
        Function to send error when user enters Invalid roll no in dev_mng_cr 
    '''
    update.message.reply_text(text='''Please enter a valid Roll no''')
    return DEV_MENU_KEY

## Force json update Function 
@cs.send_action(action=telegram.ChatAction.TYPING)
@cs.userauthorized(cs.devjson['devChat_id'])
def forceJsonUpdate(update,context):
    '''
        Function to update values of variables from json files
    '''
    cs.jsonupd()
    update.message.reply_text(text='''Json Files updated successfully''')
    return DEV_MENU_KEY

@cs.send_action(action=ChatAction.TYPING)
def Return_menu(update,context):
    '''
        Functon to return to menu to the user
    '''
    Menu(update,context)
    return RETURN_MENU