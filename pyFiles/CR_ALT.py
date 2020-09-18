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
bottkn = open('data/bottkn.txt').read().strip()
## Updater decleration
pp = PicklePersistence(filename='data/CRApersistance')
updater = Updater(token=bottkn,persistence=pp,use_context=True, workers=50)
disp = updater.dispatcher
jobque = updater.job_queue
daytuple = tuple(range(len(cs.datajson['daylst'])))
## Job Queue Functions
## JobQueue Dispachers
jobque.run_daily(callback = tb.update_Day_tt,time = datetime.time(hour = 18, minute = 0, tzinfo = timezone('Asia/Kolkata')))
jobque.run_daily(callback = tb.callback_daily,time = datetime.time(hour = 0, minute = 30, tzinfo = timezone('Asia/Kolkata')))

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
    
    if emp_id == None and rollno != None :
        text = [['Menu']]
        update.message.reply_text(text='''Welcome Back ! {}\nYou have logged in as\na Student with Roll no: {}.'''.format(update.message.from_user.first_name,rollno))
        update.message.reply_text("Select Menu to see the list of things that you can ask me.",reply_markup=telegram.ReplyKeyboardMarkup(text))
        return sb.MAIN_MENU_KEY
    elif emp_id != None and rollno == None :
        text = [['Menu']]
        update.message.reply_text(text='''Welcome Back! {}\nYou have logged in as\na Professor with Email Id: {}.'''.format(update.message.from_user.first_name,emp_id))
        update.message.reply_text("Select Menu to see the list of things that you can ask me.",reply_markup=telegram.ReplyKeyboardMarkup(text))
        return tb.MAIN_MENU_KEY
    else:
        db.rmvtch(update.effective_chat.id)
        db.rmvstd(update.effective_chat.id)
        text = [['Professor'],['Student']]
        update.message.reply_text(text='''Hi! {}\nWelcome to your Personal\nTimetable Manager - \n"CR_ALT"'''.format(update.message.from_user.first_name))
        update.message.reply_text(text='''Please tell me, who are you ?.''',reply_markup=telegram.ReplyKeyboardMarkup(text))
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
        update.message.reply_text(text='''Select Menu to see the list.\nPlease prefer using\nCUSTOM KEYBOARD''',reply_markup=telegram.ReplyKeyboardMarkup([['Menu']]))
        return tb.MAIN_MENU_KEY
    elif emp_id == None and rollno != None :
        update.message.reply_text(text='''Select Menu to see the list.\nPlease prefer using\nCUSTOM KEYBOARD''',reply_markup=telegram.ReplyKeyboardMarkup([['Menu']]))
        return sb.MAIN_MENU_KEY
    else:
        text = [['Professor'],['Student']]
        update.message.reply_text(text='''Please tell me, who are you?.\nPlease prefer using\nCUSTOM KEYBOARD''',reply_markup=telegram.ReplyKeyboardMarkup(text))
        return SETUP_KEY

## Back Functions
@cs.send_action(action=telegram.ChatAction.TYPING)
def bkSAC(update, context):
    '''
        Function to send back from std_auth_cov to start
    '''
    text = [['Professor'],['Student']]
    update.message.reply_text(text='''Please tell me who are you?''',reply_markup=telegram.ReplyKeyboardMarkup(text))
    return cs.END

@cs.send_action(action=telegram.ChatAction.TYPING)
def bkTAC(update, context):
    '''
        Function to send back from tch_auth_cov to start
    '''
    text = [['Professor'],['Student']]
    update.message.reply_text(text='''Please tell me who are you?''',reply_markup=telegram.ReplyKeyboardMarkup(text))
    return cs.END

## Function to send message to student about class creation
@cs.send_action(action=telegram.ChatAction.TYPING)
def Snd_CR8Cls(update,context: telegram.ext.CallbackContext):
    '''
        Function to Send message to users about created class
    '''
    query = update.callback_query
    query.answer()
    if query.data != 'CR8CLS:No':
        tcdata = query.data[1:].split(':')
        if not tcdata[3] in [grade[0] for grade in db.getTeachtt((update.effective_chat.id),tcdata[4])] :
            chkCR8Cls = db.CR8cls(tcdata[1],tcdata[2],tcdata[3],tcdata[4])
        else:
            query.edit_message_text(text='''You already have a class at that time:\nCreate class at another period''')
            return
        if not chkCR8Cls == -1:
            query.edit_message_text(text='''Please wait I am  forwarding Your message about Created Class to students''')
            text='''Class for subject {} of {} created on {} : {} by {}.\nPlease Check your Timetable'''.format(tcdata[2],tcdata[1],tcdata[4],tcdata[3],tcdata[5])
            usrlst = db.grdstdid(tcdata[1])
            cs.SndMsgTolst(update,context,usrlst,text)
            query.edit_message_text(text="Your Message was sent to {} students in {} Batch".format(len(usrlst),tcdata[1]))
        else:
            query.edit_message_text(text='''You are late:\nSelected period has already been taken,\nBetter luck next time!''' )
    else:
        query.edit_message_text(text="You have Cancelled your request to create class")


## Function to send message to student about class Cancelation
@cs.send_action(action=telegram.ChatAction.TYPING)
def Snd_CXLCls(update,context: telegram.ext.CallbackContext):
    '''
        Function to Send message to users about created class
    '''
    query = update.callback_query
    query.answer()
    if query.data != 'CXLCLS:No':
        tcdata = query.data[1:].split(':')
        if not db.delcls(tcdata[2],tcdata[3],tcdata[1],tcdata[4]) == -1:
            query.edit_message_text(text='''Please wait I am  forwarding Your message about Cancelled Class to students''' )
            text='''Class for subject {} of {} on {} : {} was Cancelled by {}.\nPlease Check your Timetable'''.format(tcdata[3].upper(),tcdata[2],tcdata[4],tcdata[1],tcdata[5])
            usrlst = db.grdstdid(tcdata[2])
            cs.SndMsgTolst(update,context,usrlst,text)
            query.edit_message_text(text="I forwarded your message about Class Cancelation to {} students in {} Batch".format(len(usrlst),tcdata[2]))
        else:
            query.edit_message_text(text='''The Class you told me to Cancel does not exists''')
    else:
        query.edit_message_text(text="You have Cancelled your request to Cancel class")

## Function to send message to student about class Replacement
@cs.send_action(action=telegram.ChatAction.TYPING)
def Snd_RPLCls(update,context: telegram.ext.CallbackContext):
    '''
        Function to Send message to users about created class
    '''
    query = update.callback_query
    query.answer()
    # RPLCLS:period:grade:subject:day:RPLSub:Name
    if query.data != 'RPLCLS:No':
        tcdata = query.data[1:].split(':')
        if not db.delcls(tcdata[2],tcdata[3],tcdata[1],tcdata[4]) == -1:
            if not db.CR8cls(tcdata[2],tcdata[5],tcdata[1],tcdata[4]) == -1:
                query.edit_message_text(text='''Please wait I am  forwarding Your message about Replaced Class to students''' )
                text='''Class for subject {} of {} on {} : {} was Replaced by subject {}  by CR - {}.\nPlease Check your Timetable'''.format(tcdata[3].upper(),tcdata[2],tcdata[4],tcdata[1],tcdata[5],tcdata[6])
                usrlst = db.grdstdid(tcdata[2])
                cs.SndMsgTolst(update,context,usrlst,text)
                query.edit_message_text(text="I forwarded your message about Replacement of Class to {} students in {} Batch".format(len(usrlst),tcdata[2]))
            else:
                query.edit_message_text(text='''You are late:\nSelected period has already been taken,\nBetter luck next time!''')
        else:
            query.edit_message_text(text='''The Class you told me to Replace does not exists''')
    else:
        query.edit_message_text(text="You have Cancelled your request to Replace class")


###
### Conversation Handlers (Main Function)
###     

std_CR_RPLCls_Sub_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text([(P +  ":" + S) for P in cs.datajson['periodlst'] 
                                                for (G,S) in db.getallgrdsub() ])),sb.subkb_CRSC)],
    states          =   {
                            sb.RPLCLS_SUB_KEY   :   [   MessageHandler((Filters.text([ str(S) for (G,S) in db.getallgrdsub() ])),sb.conf_RPLcls_CRGC),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCRSC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivsub_CRSC)],
    name            =   "stdCRRPLClsSubcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.RPLCLS_GSP_KEY,
                            sb.STOPPING         :   sb.STOPPING,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

std_CR_RPLCls_GSP_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(cs.datajson['daylst'])),sb.GSP_CRGC)],
    states          =   {
                            sb.RPLCLS_GSP_KEY   :   [   std_CR_RPLCls_Sub_cov,
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCRGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivGSP_CRGC)],
    name            =   "stdCXLClsGSPcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.RPLCLS_DAY_KEY,
                            sb.STOPPING         :   sb.STOPPING,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

std_CR_RPLCls_Day_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Replace Class")),sb.daykb_CRDC)],
    states          =   {
                            sb.RPLCLS_DAY_KEY   :   [   std_CR_RPLCls_GSP_cov,
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCRDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivday_CRDC)],
    name            =   "stdRplClsDaycov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.CR_MENU_KEY,
                            sb.STOPPING         :   cs.END,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)


##  Create class Option Handler

std_CR8Cls_Perd_cov =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text([ str(S) for (G,S) in db.getallgrdsub() ])),sb.period_CCPC)],
    states          =   {
                            sb.CR8CLS_PERD_KEY  :   [   MessageHandler((Filters.text(cs.datajson['periodlst'])),sb.conf_CR8cls_CCPC),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCCPC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivperiod_CCPC)],
    name            =   "stdCRCR8ClsPerdcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.CR8CLS_SUB_KEY,
                            sb.STOPPING         :   sb.STOPPING,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

std_CR_CR8Cls_Sub_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(cs.datajson['daylst'])),sb.subkb_CCGC)],
    states          =   {
                            sb.CR8CLS_SUB_KEY   :   [   std_CR8Cls_Perd_cov,
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCCGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivsub_CCGC)],
    name            =   "stdCRCR8ClsSubcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.CR8CLS_Day_KEY,
                            sb.STOPPING         :   sb.STOPPING,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

std_CR_CR8Cls_Day_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Create Class")),sb.dayKb_CCDC)],
    states          =   {
                            sb.CR8CLS_Day_KEY   :   [   std_CR_CR8Cls_Sub_cov,
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivday_CCDC)],
    name            =   "stdCRCR8ClsGrdcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.CR_MENU_KEY,
                            sb.STOPPING         :   cs.END,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

##  Cancel Class

std_CR_CXLCls_GSP_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(cs.datajson['daylst'])),sb.GSP_CxCGC)],
    states          =   {
                            sb.CXLCLS_GSP_KEY   :   [   MessageHandler((Filters.text([(P +  ":" + S) for P in cs.datajson['periodlst'] 
                                                                        for (G,S) in db.getallgrdsub() ])),sb.conf_CXLcls_CxCGC),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCxCGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivGSP_CxCGC)],
    name            =   "stdCXLClsGSPcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.CXLCLS_DAY_KEY,
                            sb.STOPPING         :   sb.STOPPING,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

std_CR_CXLCls_Day_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Cancel Class")),sb.daykb_CxCDC)],
    states          =   {
                            sb.CXLCLS_DAY_KEY   :   [   std_CR_CXLCls_GSP_cov,
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCxCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivday_CxCDC)],
    name            =   "stdCXLClsDaycov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.CR_MENU_KEY,
                            sb.STOPPING         :   cs.END,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

## message students

std_CR_MsgStd_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler(Filters.text('"Message Students"'),sb.msgstd_SCMC)],
    states          =   {
                            sb.CR_MSG_KEY   :   [   MessageHandler(~Filters.text("Back") & ~Filters.command,sb.snd_MsgStd_msg),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkSCMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((Filters.command),sb.ivmsg_SCMC)],
    name            =   "stdCRMsgStdcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.CR_MENU_KEY,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)
Std_CR_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("CR Menu")),sb.CR_Menu)],
    states          =   {
                            sb.CR_MENU_KEY     :   [   std_CR_CR8Cls_Day_cov,std_CR_CXLCls_Day_cov,std_CR_MsgStd_cov,std_CR_RPLCls_Day_cov,
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkCRMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivCRMenu)],
    name            =   "stdCrMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MAIN_MENU_KEY,
                            sb.RETURN_MENU      :   sb.MAIN_MENU_KEY
                        }
)
## Dev menu handler

std_Dev_MNG_CR_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Manage CR")),sb.devgetCRRoll)],
    states          =   {
                            sb.DEV_MNG_CR_KEY :   [   MessageHandler(Filters.regex('^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$'),sb.devMngCR),
                                                        MessageHandler(Filters.text("Back"),sb.bkDRAC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.regex('^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$') & ~Filters.text("Back"),sb.ivDevMngCR)],
    name            =   'stdDevMngCRCov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.DEV_MENU_KEY
                        }
)  

std_Dev_RMV_ACC_cov =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Remove User\nAccount")),sb.devgetRmvUsrid)],
    states          =   {
                            sb.DEV_RMV_ACC_KEY :   [   MessageHandler(Filters.text(db.getalltchempid()) | Filters.regex('^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$'),sb.devRmvUsr),
                                                        MessageHandler(Filters.text("Back"),sb.bkDRAC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.text(db.getallstduid() + db.getalltchuid() + db.getallstdrollno() + db.getalltchempid()+["Back"]),sb.ivDevRmvAcc)],
    name            =   'stdDevRmvAccCov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.DEV_MENU_KEY
                        }
)  

std_Dev_Msg_cov     =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(['Students','Teachers','All Users']+db.getallstduid()+db.getalltchuid()+ db.getallstdrollno() + db.getalltchempid())),sb.dev_msg_usr)],
    states          =   {
                            sb.DEV_MSG_KEY      :   [    MessageHandler(~Filters.text("Back") & ~Filters.command,sb.snd_dev_msg),
                                                        MessageHandler(Filters.text("Back"),sb.bkSDMC)],
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.all,sb.ivDevMsg)],
    name            =   'stdDevMsgcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.DEV_MSG_MENU_KEY
                        }
)

std_Dev_Msg_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Message Users")),sb.devmenu_msg)],
    states          =   {
                            sb.DEV_MSG_MENU_KEY :   [   std_Dev_Msg_cov,
                                                        MessageHandler(Filters.text("Back"),sb.bkDMMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.text(['Students','Teachers',"One User",'All Users']),sb.ivDevMsgMenu)],
    name            =   'stdDevMsgMenucov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.DEV_MENU_KEY
                        }
)       

##
## Student Handlers
##

std_Dev_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("DEV Menu")),sb.dev_Menu)],
    states          =   {
                            sb.DEV_MENU_KEY     :   [   MessageHandler((Filters.text("No of Users")),sb.dev_no_usr),
                                                        MessageHandler((Filters.text("Json Update")),sb.forceJsonUpdate),
                                                        std_Dev_Msg_Menu_cov,std_Dev_RMV_ACC_cov,std_Dev_MNG_CR_cov,
                                                        MessageHandler((Filters.text("Back")),sb.bkSTMENUC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(( ~Filters.text("No of Users") & ~Filters.text("Back")),sb.ivDMenu)],
    name            =   "stdDevMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MAIN_MENU_KEY
                        }
)

std_CT_Dev_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Contact\nDeveloper(s)")),sb.std_CT_dev)],
    states          =   {
                            sb.CT_MENU_KEY      :   [   MessageHandler(~Filters.text("Back") & ~Filters.poll ,sb.Snd_Msg_Dev),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler(Filters.text("Back"),sb.bkSCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(Filters.poll,sb.ivCTDev)],
    name            =   'stdCTDevcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MORE_MENU_KEY,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

std_More_Menu_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("More")),sb.more_Menu)],
    states          =   {
                            sb.MORE_MENU_KEY    :   [   MessageHandler(( Filters.text('Know about\nDeveloper(s)')),sb.Std_Know_Abt_Dev),
                                                        MessageHandler(( Filters.text('Logout')),sb.std_logout),
                                                        std_CT_Dev_cov,
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkSMMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivMoreMenu)],
    name            =   'stdMoreMenucov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MAIN_MENU_KEY,
                            sb.STOPPING         :   sb.STOPPING,
                            sb.RETURN_MENU      :   sb.MAIN_MENU_KEY
                        }
)

## Student Attendance Menu Cov handler

std_setAtd_Stat_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(db.getallsub())),sb.Statkb_SASTC)],
    states          =   {
                            sb.SETATD_STAT_KEY   :   [   MessageHandler(( Filters.text(['Present','Absent']) | 
                                                        Filters.regex(r"^[0-9][0-9]?:[0-9]?[0-9]$")),sb.set_atd),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkSSASTC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(['Present','Absent','Back'])),sb.ivStat_SASC)],
    name            =   "stdSetStdStatcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.SETATD_SUB_KEY,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }

)

std_setAtd_Sub_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Set Attendance")),sb.subkb_SASUC)],
    states          =   {
                            sb.SETATD_SUB_KEY   :   [   std_setAtd_Stat_cov,
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkSSASC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(db.getallsub()) & ~Filters.text("Back")),sb.ivsub_SASC)],
    name            =   "stdSetAtdSubcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.ATD_MENU_KEY,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

std_Atd_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Attendance")),sb.atd_Menu)],
    states          =   {
                            sb.ATD_MENU_KEY     :   [   MessageHandler((Filters.text("Get Attendance")),sb.get_Std_Atd),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        std_setAtd_Sub_cov, MessageHandler((Filters.text("Back")),sb.bkSAMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),sb.ivAtdMenu)],
    name            =   "stdAtdMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MAIN_MENU_KEY,
                            sb.RETURN_MENU      :   sb.MAIN_MENU_KEY
                        }
) 

##  Students Timetable Menu handler

std_DailyTT_Menu_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Daily Timetable")),sb.dayKb_DTMC)],
    states          =   {
                            sb.DAILY_TT_KEY     :   [   MessageHandler((Filters.text(cs.datajson['daylst'])),sb.day_std_tt),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),sb.bkDTMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(cs.datajson['daylst']) & ~Filters.text("Back")),sb.ivday_DTMC)],
    name            =   "stdDailyTtMenuCov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.TT_MENU_KEY,
                            sb.RETURN_MENU      :   sb.RETURN_MENU
                        }
)

std_TT_Menu_cov     =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Timetable")),sb.tt_Menu)],
    states          =   {
                            sb.TT_MENU_KEY      :   [   MessageHandler((Filters.text("Today's Timetable")),sb.td_Std_TT),
                                                        CommandHandler('menu',sb.Return_menu),
                                                        std_DailyTT_Menu_cov,MessageHandler((Filters.text("Back")),sb.bkSTMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(( ~Filters.text("Today's Timetable") & ~Filters.text("Back")),sb.ivTTMenu)],
    name            =   "stdTtMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   sb.MAIN_MENU_KEY,
                            sb.RETURN_MENU      :   sb.MAIN_MENU_KEY
                        }
)

##  Student Main Menu handler

std_Menu_cov        =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Menu")),sb.Menu)],
    states          =   {
                            sb.MAIN_MENU_KEY    :   [   std_TT_Menu_cov,
                                                        std_Atd_Menu_cov,
                                                        std_More_Menu_cov,
                                                        std_Dev_Menu_cov,
                                                        Std_CR_Menu_cov]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(['Timetable','Attendance','Dev Menu','More'])),sb.ivmenu)],
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
                            sb.AUTH_KEY         :   [  (MessageHandler(Filters.regex('^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$'),sb.Authentication)),
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

###     

## Dev menu handler
tch_Dev_MNG_CR_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Manage CR")),tb.devgetCRRoll)],
    states          =   {
                            sb.DEV_MNG_CR_KEY :   [   MessageHandler(Filters.regex('^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$'),tb.devMngCR),
                                                        MessageHandler(Filters.text("Back"),tb.bkDRAC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.regex('^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$') & ~Filters.text("Back"),tb.ivDevMngCR)],
    name            =   'tchDevMngCRCov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.DEV_MENU_KEY
                        }
)  

tch_Dev_RMV_ACC_cov =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Remove User\nAccount")),tb.devgetRmvUsrid)],
    states          =   {
                            tb.DEV_RMV_ACC_KEY :   [   MessageHandler(Filters.text(db.getallstduid() + db.getalltchuid() + db.getallstdrollno() + db.getalltchempid()),tb.devRmvUsr),
                                                        MessageHandler(Filters.text("Back"),tb.bkDRAC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.text(db.getallstduid() + db.getalltchuid() + db.getallstdrollno() + db.getalltchempid()+["Back"]),tb.ivDevRmvAcc)],
    name            =   'tchDevRmvAccCov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.DEV_MENU_KEY
                        }
)  

tch_Dev_Msg_cov     =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(['Students','Teachers','All Users']+db.getallstduid()+db.getalltchuid()+ db.getallstdrollno() + db.getalltchempid())),tb.dev_msg_usr)],
    states          =   {
                            tb.DEV_MSG_KEY      :   [    MessageHandler(~Filters.text("Back") & ~Filters.command,tb.snd_dev_msg),
                                                        MessageHandler(Filters.text("Back"),tb.bkSDMC)],
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.all,tb.ivDevMsg)],
    name            =   'tchDevMsgcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.DEV_MSG_MENU_KEY
                        }
)

tch_Dev_Msg_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Message Users")),tb.devmenu_msg)],
    states          =   {
                            tb.DEV_MSG_MENU_KEY :   [   tch_Dev_Msg_cov,
                                                        MessageHandler(Filters.text("Back"),tb.bkDMMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(~Filters.text(['Students','Teachers',"One User",'All Users']),tb.ivDevMsgMenu)],
    name            =   'tchDevMsgMenucov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.DEV_MENU_KEY
                        }
)       

tch_Dev_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("DEV Menu")),tb.dev_Menu)],
    states          =   {
                            tb.DEV_MENU_KEY     :   [   MessageHandler((Filters.text("No of Users")),tb.dev_no_usr),
                                                        MessageHandler((Filters.text("Json Update")),tb.forceJsonUpdate),
                                                        tch_Dev_Msg_Menu_cov,tch_Dev_RMV_ACC_cov,tch_Dev_MNG_CR_cov,
                                                        MessageHandler((Filters.text("Back")),tb.bkTDMENUC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(( ~Filters.text("No of Users") & ~Filters.text("Back")),tb.ivDMenu)],
    name            =   "tchDevMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MAIN_MENU_KEY
                        }
)

tch_CT_Dev_cov      =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Contact\nDeveloper(s)")),tb.tch_CT_dev)],
    states          =   {
                            tb.CT_MENU_KEY      :   [    MessageHandler(~Filters.text("Back") & ~Filters.poll ,tb.Snd_Msg_Dev),
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler(Filters.text("Back"),tb.bkTCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(Filters.poll,tb.ivCTDev)],
    name            =   'tchCTDevcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MORE_MENU_KEY,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)

tch_More_Menu_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("More")),tb.more_Menu)],
    states          =   {
                            tb.MORE_MENU_KEY    :   [   MessageHandler(( Filters.text('Know about\nDeveloper(s)')),tb.Tch_Know_Abt_Dev),
                                                        MessageHandler(( Filters.text('Logout')),tb.tch_logout),
                                                        tch_CT_Dev_cov,tch_Dev_Menu_cov,
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkTMMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivMoreMenu)],
    name            =   'tchMoreMenucov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MAIN_MENU_KEY,
                            tb.STOPPING         :   tb.STOPPING,
                            tb.RETURN_MENU      :   tb.MAIN_MENU_KEY
                        }
)

tch_MsgStd_Msg_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(list({grade[0] for grade in db.getallgrdsub()})+['Message All'])),tb.msgstd_MSMC)],
    states          =   {
                            tb.MSGSTD_MSG_KEY   :   [   MessageHandler(~Filters.text("Back") & ~Filters.command,tb.snd_MsgStd_msg),
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkMSMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.all),tb.ivmsg_MSMC)],
    name            =   "tchMsgStdMsgcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MSGSTD_GRD_KEY,
                            tb.STOPPING         :   tb.STOPPING,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)

tch_MsgStd_Grd_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Message Students")),tb.avgrdkb_MSGC)],
    states          =   {
                            tb.MSGSTD_GRD_KEY   :   [   tch_MsgStd_Msg_cov,
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler(Filters.text("Back"),tb.bkMSGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivGrd_MSGC)],
    name            =   'tchMsgStdGrdcov',
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.ANN_MENU_KEY,
                            tb.STOPPING         :   cs.END,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)

##  Cancel class Option Handler

tch_CXLCls_GSP_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(cs.datajson['daylst'])),tb.GSP_CxCGC)],
    states          =   {
                            tb.CXLCLS_GSP_KEY   :   [   MessageHandler((Filters.text([(P + ":" + G + ":" + S) for P in cs.datajson['periodlst'] 
                                                                        for (G,S) in db.getallgrdsub() ])),tb.conf_CXLcls_CxCGC),
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkCxCGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivGSP_CxCGC)],
    name            =   "tchCXLClsGSPcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.CXLCLS_DAY_KEY,
                            tb.STOPPING         :   tb.STOPPING,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)

tch_CXLCls_Day_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Cancel Class")),tb.daykb_CxCDC)],
    states          =   {
                            tb.CXLCLS_DAY_KEY   :   [   tch_CXLCls_GSP_cov,
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkCxCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivday_CxCDC)],
    name            =   "tchCXLClsDaycov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.ANN_MENU_KEY,
                            tb.STOPPING         :   cs.END,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)


##  Create class Option Handler

tch_CR8Cls_Perd_cov =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(cs.datajson['daylst'])),tb.period_CCPC)],
    states          =   {
                            tb.CR8CLS_PERD_KEY  :   [   MessageHandler((Filters.text(cs.datajson['periodlst'])),tb.conf_CR8cls_CCPC),
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkCCPC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivperiod_CCPC)],
    name            =   "tchCR8ClsPerdcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.CR8CLS_Day_KEY,
                            tb.STOPPING         :   tb.STOPPING,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)

tch_CR8Cls_Day_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text([(grdsub[0] + ":" + grdsub[1]) for grdsub in db.getallgrdsub()])),tb.dayKb_CCDC)],
    states          =   {
                            tb.CR8CLS_Day_KEY   :   [   tch_CR8Cls_Perd_cov,
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkCCDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivday_CCDC)],
    name            =   "tchCR8ClsDaycov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.CR8CLS_GRD_KEY,
                            tb.STOPPING         :   tb.STOPPING,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)

tch_CR8Cls_Grd_cov  =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Create Class")),tb.grdsubkb_CCGC)],
    states          =   {
                            tb.CR8CLS_GRD_KEY   :   [   tch_CR8Cls_Day_cov,
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkCCGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivgrdsub_CCGC)],
    name            =   "tchCR8ClsGrdcov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.ANN_MENU_KEY,
                            tb.STOPPING         :   cs.END,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)


##  Announcement Menu Handler

tch_Ann_Menu_cov    =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Announcements")),tb.ann_Menu)],
    states          =   {
                            tb.ANN_MENU_KEY     :   [   tch_CR8Cls_Grd_cov,tch_CXLCls_Day_cov,tch_MsgStd_Grd_cov,
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkAnnMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text("Back")),tb.ivAnnMenu)],
    name            =   "tchAnnMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MAIN_MENU_KEY,
                            tb.RETURN_MENU      :   tb.MAIN_MENU_KEY
                        }
)

##  Teacher Timetable Option Handlers


tch_GrdTT_Day_cov   =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text(list({grade[0] for grade in db.getallgrdsub()}))),tb.dayKb_GTDC)],
    states          =   {
                            tb.GRADE_TT_DAY_KEY :   [   MessageHandler((Filters.text(cs.datajson['daylst'])),tb.day_grd_tch_tt),
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkGTDC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(db.getallgrd()) & ~Filters.text("Back")),tb.ivday_GTDC)],
    name            =   "tchGradetTtDayCov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.GRADE_TT_GRD_KEY,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)

tch_GrdTT_Grade_cov =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Grade Timetable")),tb.gradeKb_GTGC)],
    states          =   {
                            tb.GRADE_TT_GRD_KEY :   [   tch_GrdTT_Day_cov,
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkGTGC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(db.getallsub()) & ~Filters.text("Back")),tb.ivgrade_GTGC)],
    name            =   "tchGradetTtGradeCov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.TT_MENU_KEY,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)


tch_DailyTT_Menu_cov=   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Daily Timetable")),tb.dayKb_DTMC)],
    states          =   {
                            tb.DAILY_TT_KEY     :   [   MessageHandler((Filters.text(cs.datajson['daylst'])),tb.day_tch_tt),
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkDTMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(cs.datajson['daylst']) & ~Filters.text("Back")),tb.ivday_DTMC)],
    name            =   "tchDailyTtMenuCov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.TT_MENU_KEY,
                            tb.RETURN_MENU      :   tb.RETURN_MENU
                        }
)

tch_TT_Menu_cov     =   ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Timetable")),tb.tt_Menu)],
    states          =   {
                            tb.TT_MENU_KEY      :   [   MessageHandler((Filters.text("Today's Timetable")),tb.td_Tch_TT),
                                                        tch_DailyTT_Menu_cov,tch_GrdTT_Grade_cov,
                                                        CommandHandler('menu',tb.Return_menu),
                                                        MessageHandler((Filters.text("Back")),tb.bkTTMC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler(( ~Filters.text("Back")),tb.ivTTMenu)],
    name            =   "tchTtMenucov",
    persistent      =   True,
    map_to_parent   =   {
                            cs.END              :   tb.MAIN_MENU_KEY,
                            tb.RETURN_MENU      :   tb.MAIN_MENU_KEY
                        }
)

##  Teacher Main Menu cov handler

tch_Menu_cov        =      ConversationHandler(
    entry_points    =   [MessageHandler((Filters.text("Menu")),tb.Menu)],
    states          =   {
                            tb.MAIN_MENU_KEY    :   [   tch_Dev_Menu_cov,tch_TT_Menu_cov,tch_Ann_Menu_cov,tch_More_Menu_cov]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(['Timetable','Dev Menu','Announcements','More'])),tb.ivmenu)],
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
                            tb.AUTH_KEY         :   [   MessageHandler((Filters.text(cs.tchEmaillist)), tb.Authentication ),
                                                        MessageHandler((Filters.text("Back")),bkTAC)]
                        },
    allow_reentry   =   True,
    fallbacks       =   [MessageHandler((~Filters.text(cs.tchEmaillist) & ~Filters.text("Back")),tb.ivempid)],
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
disp.add_handler(CallbackQueryHandler(Snd_CR8Cls,pattern='^CR8CLS:.*'))
disp.add_handler(CallbackQueryHandler(Snd_CXLCls,pattern='^CXLCLS:.*'))
disp.add_handler(CallbackQueryHandler(Snd_RPLCls,pattern='^RPLCLS:.*'))

## Starting WebHooking
# url = cs.serverjson["webhook_url"] + ":" + cs.serverjson["port"] + "/" + bottkn
# updater.start_webhook(listen=cs.serverjson["listen"],
#                     port=int(cs.serverjson["port"]),
#                     url_path=bottkn,
#                     key=cs.serverjson["key"],
#                     cert=cs.serverjson["cert"],
#                     webhook_url= url)
## Start polling
updater.start_polling()
print("Getting Updates from CR_ALT")
updater.idle()

