import dbCreate as db
import pystdcb as sb
import pytchcb as tb
import codeSnippets as cs
from telegram.ext import PicklePersistence, Updater, Filters, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler
# from telegram.ext import *
from telegram.ext.dispatcher import run_async
import telegram, datetime
from pytz import timezone
##
bottkn = open('data/bottkn.txt').read()
## Updater decleration
pp = PicklePersistence(filename='data/CRApersistance')
updater = Updater(token=bottkn,persistence=pp,use_context=True)
disp = updater.dispatcher
jobque = updater.job_queue
daytuple = tuple(range(len(cs.datajson['daylst'])))
## Job Queue Functions


## JobQueue Dispachers
jobque.run_daily(callback = tb.update_Day_tt,time = datetime.time(hour = 18, minute = 00, tzinfo = timezone('Asia/Kolkata')),context=telegram.ext.CallbackContext)
jobque.run_daily(tb.callback_daily,datetime.time(hour = 0, minute = 30, tzinfo = timezone('Asia/Kolkata')),context=telegram.ext.CallbackContext)

jobque.run_daily(sb.callback_daily,datetime.time(hour = 0, minute = 45, tzinfo = timezone('Asia/Kolkata')))
for i in cs.datajson["periodlst"]:
    tm = ((i.split('-'))[1]).split('.')
    jobque.run_daily(callback = sb.class_Remindar,time = datetime.time(hour = int(tm[0]), minute = int(tm[1]), tzinfo = timezone('Asia/Kolkata')),context=i,name = i + '.__name__')

## Conversation dict Constants keys
SETUP_KEY = 100

## Functions
@cs.send_action(action=telegram.ChatAction.TYPING)
def start(update, context):
    '''
        Start function
        -- It is the start of the conversation
    '''
    emp_id = db.chktch(update.effective_chat.id)
    rollno = db.chkusr(update.effective_chat.id)
    context.user_data['updtch'] = False
    context.user_data['updusr'] = False
    
    if emp_id != None and rollno == None :
        text = [['Menu']]
        update.message.reply_text(text='''Welcome Back ! {}\nYou have logged in as\na *Student* with Roll no:*{}*.'''.format(update.message.from_user.first_name,emp_id), parse_mode= 'Markdown')
        update.message.reply_text("Select *Menu* to see the list of things that you can ask me.", parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup(text))
        return tb.MAIN_MENU_KEY
    elif emp_id == None and rollno != None :
        text = [['Menu']]
        update.message.reply_text(text='''Welcome Back! {}\nYou have logged in as\na *Professor* with Employee Id *{}*.'''.format(update.message.from_user.first_name,emp_id), parse_mode= 'Markdown')
        update.message.reply_text("Select *Menu* to see the list of things that you can ask me.", parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup(text))
        return sb.MAIN_MENU_KEY
    else:
        text = [['Professor'],['Student']]
        update.message.reply_text(text='''Hi! {}\nWelcome to your Personal\nTimetable Manager - \n" *CR ALT*."'''.format(update.message.from_user.first_name), parse_mode= 'Markdown')
        update.message.reply_text(text='''Please tell me, *who are you ?*.''', parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup(text))
        return SETUP_KEY

## Invalid functions
@cs.send_action(action=telegram.ChatAction.TYPING)
def ivstart (update, context):
    ''' 
    Function to send error when user enters Invalid option in Start Menu
    '''
    emp_id = db.chktch(update.effective_chat.id)
    rollno = db.chkusr(update.effective_chat.id)
    if emp_id != None and rollno == None :
        update.message.reply_text(text='''Select *Menu* to see the list\nPlease prefer using\n*CUSTOM KEYBOARD*''', parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup([['Menu']]))
        return tb.MAIN_MENU_KEY
    elif emp_id == None and rollno != None :
        update.message.reply_text(text='''Select *Menu* to see the list\nPlease prefer using\n*CUSTOM KEYBOARD*''', parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup([['Menu']]))
        return sb.MAIN_MENU_KEY
    else:
        text = [['Professor'],['Student']]
        update.message.reply_text(text='''Please tell me, *who are you?*\nPlease prefer using\n*CUSTOM KEYBOARD*''', parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup(text))
        return SETUP_KEY

## Back Functions
@cs.send_action(action=telegram.ChatAction.TYPING)
def bkSAC(update, context):
    '''
        Function to send back from std_auth_cov to start
    '''
    text = [['Professor'],['Student']]
    update.message.reply_text(text='''Please tell me *who are you?*''', parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup(text))
    return cs.END

@cs.send_action(action=telegram.ChatAction.TYPING)
def bkTAC(update, context):
    '''
        Function to send back from tch_auth_cov to start
    '''
    text = [['Professor'],['Student']]
    update.message.reply_text(text='''Please tell me *who are you?*''', parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup(text))
    return cs.END



###
### Conversation Handlers (Main Function)
###

##
## Student Handlers
##

## Student More option Menu Cov handler

std_Dev_Msg_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Message All\n(Dev option)")),sb.std_dev_msg)],
    states          =   {
                            sb.DEV_MSG_KEY    :   [    MessageHandler(~Filters.text("Back") & ~Filters.command,sb.snd_dev_msg),
                                                        MessageHandler(Filters.text("Back"),sb.bkSDMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.all,sb.ivDevMsg)],
    name            =   'stdDevMsgcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MORE_MENU_KEY
                        }
)

std_CT_Dev_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Contact\nDeveloper(s)")),sb.std_CT_dev)],
    states          =   {
                            sb.CT_MENU_KEY    :   [    MessageHandler(~Filters.text("Back") & ~Filters.poll ,sb.Snd_Msg_Dev),
                                                        MessageHandler(Filters.text("Back"),sb.bkSCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(Filters.poll,sb.ivCTDev)],
    name            =   'stdCTDevcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MORE_MENU_KEY
                        }
)

std_More_Menu_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("More")),sb.more_Menu)],
    states          =   {
                            sb.MORE_MENU_KEY    :   [   MessageHandler(( Filters.text('Know about\nDeveloper(s)')),sb.Std_Know_Abt_Dev),
                                                        MessageHandler(( Filters.text('Logout')),sb.std_logout),
                                                        std_CT_Dev_cov,std_Dev_Msg_cov,
                                                        MessageHandler((Filters.text("Back")),sb.bkSMMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivMoreMenu)],
    name            =   'stdMoreMenucov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MAIN_MENU_KEY,
                            sb.STOPPING         :   sb.STOPPING
                        }
)

## Student Attendance Menu Cov handler

std_setAtd_Stat_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(db.getallsub())),sb.Statkb_SASTC)],
    states          =   {
                            sb.SETATD_STAT_KEY   :   [   MessageHandler(( Filters.text(['Present','Absent']) | 
                                                        Filters.regex(r"[0-9][0-9]?:[0-9][0-9]?")),sb.set_atd),
                                                        MessageHandler((Filters.text("Back")),sb.bkSSASTC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(['Present','Absent','Back'])),sb.ivStat_SASC)],
    name            =   "stdSetStdStatcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.SETATD_SUB_KEY
                        }

)

std_setAtd_Sub_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Set Attendance")),sb.subkb_SASUC)],
    states          =   {
                            sb.SETATD_SUB_KEY   :   [   std_setAtd_Stat_cov,
                                                        MessageHandler((Filters.text("Back")),sb.bkSSASC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(db.getallsub()) & ~Filters.text("Back")),sb.ivsub_SASC)],
    name            =   "stdSetAtdSubcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.ATD_MENU_KEY
                        }
)

std_Atd_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Attendance")),sb.atd_Menu)],
    states          =   {
                            sb.ATD_MENU_KEY     :   [   MessageHandler((Filters.text("Get Attendance")),sb.get_Std_Atd),
                                                        std_setAtd_Sub_cov, MessageHandler((Filters.text("Back")),sb.bkSAMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivAtdMenu)],
    name            =   "stdAtdMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MAIN_MENU_KEY
                        }
) 

##  Students Timetable Menu handler

std_DailyTT_Menu_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Daily Timetable")),sb.dayKb_DTMC)],
    states          =   {
                            sb.DAILY_TT_KEY     :   [   MessageHandler((Filters.text(cs.datajson['daylst'])),sb.day_std_tt),
                                                        MessageHandler((Filters.text("Back")),sb.bkDTMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(cs.datajson['daylst']) & ~Filters.text("Back")),sb.ivday_DTMC)],
    name            =   "stdDailyTtMenuCov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.TT_MENU_KEY
                        }
)

std_TT_Menu_cov     =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Timetable")),sb.tt_Menu)],
    states          =   {
                            sb.TT_MENU_KEY      :   [   MessageHandler((Filters.text("Today's Timetable")),sb.td_Std_TT),
                                                        std_DailyTT_Menu_cov,MessageHandler((Filters.text("Back")),sb.bkSTMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(( ~Filters.text("Today's Timetable") & ~Filters.text("Back")),sb.ivTTMenu)],
    name            =   "stdTtMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MAIN_MENU_KEY
                        }
)

##  Student Main Menu handler

std_Menu_cov        =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Menu")),sb.Menu)],
    states          =   {
                            sb.MAIN_MENU_KEY    :   [   std_TT_Menu_cov,
                                                        std_Atd_Menu_cov,
                                                        std_More_Menu_cov]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivmenu)],
    name            =   "stdMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   SETUP_KEY,
                            sb.STOPPING         :   cs.END
                        }
)

##  Student Authentication Menu handler

std_auth_cov     =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Student")),sb.rollno)],
    states          =   {
                            sb.AUTH_KEY      :    [  (MessageHandler(Filters.regex('^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$'),sb.Authentication)),
                                                        MessageHandler((Filters.text("Back")),bkSAC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.regex('^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$') & ~Filters.text("Back")),sb.ivrollno)],
    name            =   "stdAuthcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.STOP             :    sb.MAIN_MENU_KEY,
                            cs.END              :    SETUP_KEY
                        }
)

##
##  Teacher Handlers
##

##  Message students of given class Handlers

## Teacher More option Menu Cov handler

tch_Dev_Msg_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Message All\n(Dev option)")),tb.std_dev_msg)],
    states          =   {
                            tb.DEV_MSG_KEY    :   [    MessageHandler(~Filters.text("Back") & ~Filters.command,tb.snd_dev_msg),
                                                        MessageHandler(Filters.text("Back"),tb.bkTDMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.all,tb.ivDevMsg)],
    name            =   'tchDevMsgcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MORE_MENU_KEY
                        }
)

tch_CT_Dev_cov      =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Contact\nDeveloper(s)")),tb.tch_CT_dev)],
    states          =   {
                            tb.CT_MENU_KEY    :   [    MessageHandler(~Filters.text("Back") & ~Filters.poll ,tb.Snd_Msg_Dev),
                                                        MessageHandler(Filters.text("Back"),tb.bkTCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(Filters.poll,tb.ivCTDev)],
    name            =   'tchCTDevcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MORE_MENU_KEY
                        }
)

tch_More_Menu_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("More")),tb.more_Menu)],
    states          =   {
                            tb.MORE_MENU_KEY    :   [   MessageHandler(( Filters.text('Know about\nDeveloper(s)')),tb.Tch_Know_Abt_Dev),
                                                        MessageHandler(( Filters.text('Logout')),tb.tch_logout),
                                                        tch_CT_Dev_cov,tch_Dev_Msg_cov,
                                                        MessageHandler((Filters.text("Back")),tb.bkTMMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivMoreMenu)],
    name            =   'tchMoreMenucov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MAIN_MENU_KEY,
                            tb.STOPPING         :   tb.STOPPING
                        }
)

tch_MsgStd_Msg_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(list({grade[0] for grade in db.getallgrdsub()})+['Message All'])),tb.msgstd_MSMC)],
    states          =   {
                            tb.MSGSTD_MSG_KEY   :   [   MessageHandler(~Filters.text("Back") & ~Filters.command,tb.snd_MsgStd_msg),
                                                        MessageHandler((Filters.text("Back")),tb.bkMSMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.all),tb.ivmsg_MSMC)],
    name            =   "tchMsgStdMsgcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MSGSTD_GRD_KEY,
                            tb.STOPPING         :   tb.STOPPING
                        }
)

tch_MsgStd_Grd_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Message Students")),tb.avgrdkb_MSGC)],
    states          =   {
                            tb.MSGSTD_GRD_KEY   :   [   tch_MsgStd_Msg_cov,
                                                        MessageHandler(Filters.text("Back"),tb.bkMSGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivGrd_MSGC)],
    name            =   'tchMsgStdGrdcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.ANN_MENU_KEY,
                            tb.STOPPING         :   cs.END
                        }
)

##  Cancel class Option Handler

tch_CXLCls_GSP_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(cs.datajson['daylst'])),tb.GSP_CxCGC)],
    states          =   {
                            tb.CXLCLS_GSP_KEY   :   [   MessageHandler((Filters.text([(P + ":" + G + ":" + S) for P in cs.datajson['periodlst'] 
                                                                        for (G,S) in db.getallgrdsub() ])),tb.conf_CXLcls_CxCGC),
                                                        MessageHandler((Filters.text("Back")),tb.bkCxCGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivGSP_CxCGC)],
    name            =   "tchCXLClsGSPcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.CXLCLS_DAY_KEY,
                            tb.STOPPING         :   tb.STOPPING
                        }
)

tch_CXLCls_Day_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Cancel Class")),tb.daykb_CxCDC)],
    states          =   {
                            tb.CXLCLS_DAY_KEY   :   [   tch_CXLCls_GSP_cov,MessageHandler((Filters.text("Back")),tb.bkCxCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivday_CxCDC)],
    name            =   "tchCXLClsDaycov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.ANN_MENU_KEY,
                            tb.STOPPING         :   cs.END
                        }
)


##  Create class Option Handler

tch_CR8Cls_Perd_cov =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(cs.datajson['daylst'])),tb.period_CCPC)],
    states          =   {
                            tb.CR8CLS_Perd_KEY  :   [   MessageHandler((Filters.text(cs.datajson['periodlst'])),tb.conf_CR8cls_CCPC),
                                                        MessageHandler((Filters.text("Back")),tb.bkCCPC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivperiod_CCPC)],
    name            =   "tchCR8ClsPerdcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.CR8CLS_Day_KEY,
                            tb.STOPPING         :   tb.STOPPING
                        }
)

tch_CR8Cls_Day_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text([(grdsub[0] + ":" + grdsub[1]) for grdsub in db.getallgrdsub()])),tb.dayKb_CCDC)],
    states          =   {
                            tb.CR8CLS_Day_KEY   :   [   tch_CR8Cls_Perd_cov,MessageHandler((Filters.text("Back")),tb.bkCCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivday_CCDC)],
    name            =   "tchCR8ClsDaycov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.CR8CLS_GRD_KEY,
                            tb.STOPPING         :   tb.STOPPING
                        }
)

tch_CR8Cls_Grd_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Create Class")),tb.grdsubkb_CCGC)],
    states          =   {
                            tb.CR8CLS_GRD_KEY   :   [   tch_CR8Cls_Day_cov,MessageHandler((Filters.text("Back")),tb.bkCCGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivgrdsub_CCGC)],
    name            =   "tchCR8ClsGrdcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.ANN_MENU_KEY,
                            tb.STOPPING         :   cs.END
                        }
)


##  Announcement Menu Handler

tch_Ann_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Announcements")),tb.ann_Menu)],
    states          =   {
                            tb.ANN_MENU_KEY     :   [   tch_CR8Cls_Grd_cov,tch_CXLCls_Day_cov,tch_MsgStd_Grd_cov,
                                                        MessageHandler((Filters.text("Back")),tb.bkAnnMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivAnnMenu)],
    name            =   "tchAnnMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MAIN_MENU_KEY
                        }
)

##  Teacher Timetable Option Handlers


tch_GrdTT_Day_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(list({grade[0] for grade in db.getallgrdsub()}))),tb.dayKb_GTDC)],
    states          =   {
                            tb.GRADE_TT_DAY_KEY :   [   MessageHandler((Filters.text(cs.datajson['daylst'])),tb.day_grd_tch_tt),
                                                        MessageHandler((Filters.text("Back")),tb.bkGTDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(db.getallgrd()) & ~Filters.text("Back")),tb.ivday_GTDC)],
    name            =   "tchGradetTtDayCov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.GRADE_TT_GRD_KEY
                        }
)

tch_GrdTT_Grade_cov =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Grade Timetable")),tb.gradeKb_GTGC)],
    states          =   {
                            tb.GRADE_TT_GRD_KEY :   [   tch_GrdTT_Day_cov,
                                                        MessageHandler((Filters.text("Back")),tb.bkGTGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(db.getallsub()) & ~Filters.text("Back")),tb.ivgrade_GTGC)],
    name            =   "tchGradetTtGradeCov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.TT_MENU_KEY
                        }
)


tch_DailyTT_Menu_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Daily Timetable")),tb.dayKb_DTMC)],
    states          =   {
                            tb.DAILY_TT_KEY     :   [   MessageHandler((Filters.text(cs.datajson['daylst'])),tb.day_tch_tt),
                                                        MessageHandler((Filters.text("Back")),tb.bkDTMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(cs.datajson['daylst']) & ~Filters.text("Back")),tb.ivday_DTMC)],
    name            =   "tchDailyTtMenuCov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.TT_MENU_KEY
                        }
)

tch_TT_Menu_cov     =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Timetable")),tb.tt_Menu)],
    states          =   {
                            tb.TT_MENU_KEY      :   [   MessageHandler((Filters.text("Today's Timetable")),tb.td_Tch_TT),
                                                        tch_DailyTT_Menu_cov,tch_GrdTT_Grade_cov,
                                                        MessageHandler((Filters.text("Back")),tb.bkTTMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(( ~Filters.text("Back")),tb.ivTTMenu)],
    name            =   "tchTtMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MAIN_MENU_KEY
                        }
)

##  Teacher Main Menu cov handler

tch_Menu_cov        =      ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Menu")),tb.Menu)],
    states          =   {
                            tb.MAIN_MENU_KEY    :   [   tch_TT_Menu_cov,tch_Ann_Menu_cov,tch_More_Menu_cov]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivmenu)],
    name            =   "tchMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   SETUP_KEY,
                            tb.STOPPING         :   cs.END
                        }
)

## Teacher Authentication cov handler

tch_auth_cov     =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Professor")),tb.empid)],
    states          =   {
                            tb.AUTH_KEY      :   [   (MessageHandler((Filters.regex('^[iI][Ii][Ii][Tt][tT]0[0-9][0-9]$')), tb.Authentication )),
                                                        MessageHandler((Filters.text("Back")),bkTAC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.regex('^[iI][Ii][Ii][Tt][tT]0[0-9][0-9]$') & ~Filters.text("Back")),tb.ivempid)],
    name            =   "tchAuthcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.STOP             :   tb.MAIN_MENU_KEY,
                            cs.END              :   SETUP_KEY
                        }
)

##
##  Setup cov handler
##

Setup_cov           =   ConversationHandler(
    entry_points    =   [CommandHandler('start',start)],
    states          =   {
                            SETUP_KEY           :   [std_auth_cov, tch_auth_cov],
                            sb.MAIN_MENU_KEY    :   [std_Menu_cov],
                            tb.MAIN_MENU_KEY    :   [tch_Menu_cov]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Student") & ~Filters.text("Professor") & ~Filters.text("Menu")),ivstart)],
    name            =   "setupcov",
    persistent      =   True
)


##  Handler for Starting bot 
disp.add_handler(Setup_cov)
disp.add_error_handler(cs.error)

##  Handler for InlinequaryKeyboard messages

disp.add_handler(CallbackQueryHandler(sb.inline_set_atd,pattern='^[012].*'))
disp.add_handler(CallbackQueryHandler(tb.Snd_CR8Cls,pattern='^CR8CLS:.*'))
disp.add_handler(CallbackQueryHandler(tb.Snd_CXLCls,pattern='^CXLCLS:.*'))

## Starting polling
updater.start_polling()
print("Getting Updates from CR_ALT")
updater.idle()

