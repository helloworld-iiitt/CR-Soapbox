import datetime, json, re, time, urllib, requests, json
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, PicklePersistence,  CallbackContext, CallbackQueryHandler
import logging, pytz
from pytz import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from python.dbCreate import teleDb
#from dbCreate import teleDb
stdtkn = open('data/stdtkn.txt').read()
tchtkn = open('data/tchtkn.txt').read()
fbhyr = open('json/developer.json').read() #access json file
devjson = json.loads(fbhyr)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
END = ConversationHandler.END
periodlst = ['10.10-11.00','11.00-11.50','11.50-12.40','01.30-02.20','02.20-03.10','03.10-04.00']
class tchchat:
    '''
        Class for telegram chat bot - CR_Alt (TEACHER VER)
    '''

    #Constants to use in dict as keys for Conversation Handler
    Setup_MH, Empupd_MH, Menu_opt_MH, Day_MH, Grade_btt_MH, Grade_sub_MH, Announce_grd_MH, Announce_msg_MH, Announce_conf_MH = range(9)
    Take_cls_MH,Take_grd_MH, Take_day_MH, Ccl_cls_MH, Ccl_day_MH, Ccl_grd_MH, STOPPING= range(9,16)
    updtch = False
    END = ConversationHandler.END
    #init function
    def __init__(self,db):
        '''
            Init  self.updater,Jobqueue,
            Adds message handlers, nested conversation handlers,
            starts polling
        '''
        self.db = db
        self.daylst = ['Monday','Tuesday','Wednesday','Thursday','Friday',"Back"]
        pp = PicklePersistence(filename='data/Tchcraltbot')
        self.updater = Updater(token=tchtkn,persistence=pp,use_context=True)
        dp =  self.updater.dispatcher
        j =  self.updater.job_queue
        j.run_daily(self.updaytt,datetime.time(hour = 18, minute = 00, tzinfo = timezone('Asia/Kolkata')),(0,1,2,3,4),context=telegram.ext.CallbackContext)
        j.run_daily(self.callback_daily,datetime.time(hour = 2, minute = 0, tzinfo = timezone('Asia/Kolkata')),(0,1,2,3,4),context=telegram.ext.CallbackContext)

        # daily timetable cov

        Daily_tt_cov =  ConversationHandler(
                    entry_points=[MessageHandler((Filters.text("Daily Timetable")),self.daykb)],
                    states= {
                        self.Day_MH : [MessageHandler((Filters.regex(".*[dD][aA][yY]$")),self.tchdtt),
                                        MessageHandler((Filters.text('Back')),self.bckmenu)]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.regex(".*[dD][aA][yY]$") & ~Filters.text('Back') ),self.ivdlyday)],
                    name= "dailyttcov",
                    persistent=True
                )

        # Grade timetable cov

        Grade_tt_sub_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.regex("^[CEce][SsCc][Ee][0-9][0-9]$") ),self.grdttdaykb)],
                    states= {
                        self.Grade_sub_MH : [MessageHandler((Filters.regex(".*[dD][aA][yY]$")),self.grddtt),
                                        MessageHandler((Filters.text('Back')),self.bckgrdgrdkb),CommandHandler('menu', self.menucall)
                                        ]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.regex(".*[dD][aA][yY]$") & ~Filters.text('Back') & Filters.command('devann') & ~Filters.command('menu')),self.ivgrdday)],#
                    map_to_parent={ self.STOPPING : END,
                                    self.Grade_btt_MH: self.Grade_btt_MH},
                    name= "gradesubcov",
                    persistent=True
                )

        Grade_tt_btt_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.text("Batch Timetable")),self.grdgrdkb)],
                    states= {
                        self.Grade_btt_MH : [Grade_tt_sub_cov,
                                        MessageHandler((Filters.text('Back')),self.bckmenu)
                                        ]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.regex("^[CEce][SsCc][Ee][0-9][0-9]$") & ~Filters.text('Back')),self.ivgrdgrd)],
                    name= "gradebttcov",
                    persistent=True
                )

        # Announcement cov
        Announce_msg_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.regex("^[CEce][SsCc][Ee][0-9][0-9]$") ),self.annmsg)],
                    states= {
                        self.Announce_msg_MH : [MessageHandler((Filters.regex('^MSG-.*')),self.anncon),
                                        MessageHandler((Filters.text('Back')),self.bckanngrdkb),CommandHandler('menu', self.menucall)]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.regex('^MSG-.*') & ~Filters.text('Back') & Filters.command('devann') & ~Filters.command('menu')),self.ivannmsg)],
                    map_to_parent={ self.STOPPING : END,
                                    self.Announce_grd_MH: self.Announce_grd_MH},
                    name= "annmsgcov",
                    persistent=True
                )

        Announce_grd_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.text("Announcement")),self.anngrdkb)],
                    states= {
                        self.Announce_grd_MH : [Announce_msg_cov,
                                        MessageHandler((Filters.text('Back')),self.bckmenu)
                                        ]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.regex("^[CEce][SsCc][Ee][0-9][0-9]$") & ~Filters.text('Back')),self.ivanngrd)],
                    name= "anngrdcov",
                    persistent=True
                )

        # Take class cov

        Take_day_cov = ConversationHandler(
                    entry_points=[MessageHandler(Filters.regex(".*[dD][aA][yY]$"),self.tkeperkb)],
                    states= {
                        self.Take_day_MH : [MessageHandler(Filters.regex(r"^[0-9][0-9].[0-9][0-9]-[0-9][0-9].[0-9][0-9]$"),self.tkecls),
                                        MessageHandler((Filters.text('Back')),self.bcktkedaykb),CommandHandler('menu', self.menucall)]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.regex(r"^[0-9][0-9].[0-9][0-9]-[0-9][0-9].[0-9][0-9]$") & ~Filters.text('Back') & Filters.command('devann') & ~Filters.command('menu')),self.ivtkper)],
                    map_to_parent={ self.STOPPING : self.STOPPING},
                    name= "tkedaycov",
                    persistent=True
                )

        Take_grd_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.regex(r"^[CEce][SsCc][Ee][0-9][0-9]:[A-Za-z][A-Za-z][A-Za-z][A-Za-z][0-9][0-9]$") | 
                        Filters.regex(r"^[CEce][SsCc][Ee][0-9][0-9]:[Ee][0-9]$") | Filters.regex(r"^[CEce][SsCc][Ee][0-9][0-9]:T&P$")),self.tkedaykb)],
                    states= {
                        self.Take_grd_MH : [Take_day_cov,
                                        MessageHandler((Filters.text('Back')),self.bcktkegrdkb),CommandHandler('menu', self.menucall)]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.regex(".*[dD][aA][yY]$") & ~Filters.text('Back') & Filters.command('devann') & ~Filters.command('menu')),self.ivtkday)],#
                    map_to_parent={ self.STOPPING : END},
                    name= "tkegrdcov",
                    persistent=True
                )

        Take_cls_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.text("Take Class")),self.tkegrdkb)],
                    states= {
                        self.Take_cls_MH : [Take_grd_cov,
                                        MessageHandler((Filters.text('Back')),self.bckmenu)]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.regex(r"^[CEce][SsCc][Ee][0-9][0-9]:[A-Za-z][A-Za-z][A-Za-z][A-Za-z][0-9][0-9]$") & 
                        ~Filters.regex(r"^[CEce][SsCc][Ee][0-9][0-9]:[Ee][0-9]$") & ~Filters.regex(r"^[CEce][SsCc][Ee][0-9][0-9]:T&P$")),self.ivtkgs),
                        MessageHandler((~Filters.text('Back')),self.ivtkgs)],
                    name= "tkeclscov",
                    persistent=True
                )

        # cancel class cov

        Ccl_day_cov = ConversationHandler(
                    entry_points=[MessageHandler(Filters.regex(".*[dD][aA][yY]$"),self.ccgrdkb)],
                    states= {
                        self.Ccl_day_MH : [(MessageHandler(
                        (Filters.regex(r"^[0-9][0-9].[0-9][0-9]-[0-9][0-9].[0-9][0-9]:[CEce][SsCc][Ee][0-9][0-9]:[A-Za-z][A-Za-z][A-Za-z][A-Za-z][0-9][0-9]$")) |
                        (Filters.regex(r"^[0-9][0-9].[0-9][0-9]-[0-9][0-9].[0-9][0-9]:[CEce][SsCc][Ee][0-9][0-9]:[Ee][0-9]$")) |
                        (Filters.regex(r"^[0-9][0-9].[0-9][0-9]-[0-9][0-9].[0-9][0-9]:[CEce][SsCc][Ee][0-9][0-9]:T&P$")),self.ccls)),
                                        MessageHandler((Filters.text('Back')),self.bckccdaykb),CommandHandler('menu', self.menucall)
                                        ]
                    },
                    allow_reentry= True,
                    fallbacks = [(MessageHandler(
                        (~Filters.regex(r"^[0-9][0-9].[0-9][0-9]-[0-9][0-9].[0-9][0-9]:[CEce][SsCc][Ee][0-9][0-9]:[A-Za-z][A-Za-z][A-Za-z][A-Za-z][0-9][0-9]$")) &
                        (~Filters.regex(r"^[0-9][0-9].[0-9][0-9]-[0-9][0-9].[0-9][0-9]:[CEce][SsCc][Ee][0-9][0-9]:[Ee][0-9]$")) &
                        (~Filters.regex(r"^[0-9][0-9].[0-9][0-9]-[0-9][0-9].[0-9][0-9]:[CEce][SsCc][Ee][0-9][0-9]:T&P$")),self.ivccpgs)),
                        MessageHandler((~Filters.text('Back') & Filters.command('devann') & ~Filters.command('menu')),self.ivccpgs)],
                    map_to_parent={self.STOPPING : END
                                    },
                    name= "ccldaycov",
                    persistent=True
                )

        Ccl_cls_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.text("Cancel Class")),self.ccdaykb)],
                    states= {
                        self.Ccl_cls_MH : [Ccl_day_cov,
                                        MessageHandler((Filters.text('Back')),self.bckmenu)
                                        ]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler(~Filters.text('Back') & ~Filters.regex(".*[dD][aA][yY]$"),self.ivccday)],
                    name= "cclclscov",
                    persistent=True
        )

        # Menu cov 

        Menu_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.text('Menu') | Filters.text('Cancel')) ,self.menu)],
                    states= {
                        self.Menu_opt_MH : [MessageHandler(Filters.text("Today's Timetable"),self.tchtdt),
                                                MessageHandler(Filters.text('Change Your EMPLOYEE ID'),self.empupd),
                                                Daily_tt_cov,Take_cls_cov,Ccl_cls_cov,
                                                Grade_tt_btt_cov,Announce_grd_cov
                                                ]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((Filters.command('devann') & ~Filters.command('menu')) & ~Filters.text("Today's Timetable") 
                                    & ~Filters.text('Change Your EMPLOYEE ID') & ~Filters.text("Cancel Class") 
                                    & ~Filters.text("Take Class") & ~Filters.text("Announcement") 
                                    & ~Filters.text("Batch Timetable") & ~Filters.text("Daily Timetable"),self.ivmnuopt)],
                    name= "menucov",
                    persistent=True
                )

        # Start cov

        Setup_cov = ConversationHandler(
                entry_points=[CommandHandler('start', self.start)],
                states={
                    self.Setup_MH : [(MessageHandler((Filters.regex('^[iI][Ii][Ii][Tt][tT]0[0-9][0-9]$')), self.empid ))],
                    self.Empupd_MH : [(MessageHandler((Filters.regex('^[iI][Ii][Ii][Tt][tT]0[0-9][0-9]$')), self.empid )),
                                            Menu_cov]
                },
                allow_reentry= True,
                fallbacks=[MessageHandler((~ Filters.regex('^[iI][Ii][Ii][Tt][tT]0[0-9][0-9]$')) & (Filters.command('devann') & ~Filters.command('menu'))
                                                & ~Filters.text('Menu') & ~Filters.text('Cancel'),self.ivid)],
                name= "setupcov",
                persistent=True
            )

        dp.add_handler(CommandHandler("devann", self.usrann, Filters.regex('MSG'),pass_args=True))
        dp.add_handler(Setup_cov)
        dp.add_handler(CallbackQueryHandler(self.annsnd,pattern='^[01].*'))
        dp.add_handler(CallbackQueryHandler(self.tkeclsmsg,pattern='^[23].*'))
        dp.add_handler(CallbackQueryHandler(self.cclsmsg,pattern='^[45].*'))
        dp.add_handler(CallbackQueryHandler(self.inlineannall,pattern='^[67].*',))
        dp.add_error_handler(self.error)
        

    # Jobqueue Functions
    def updaytt(self,context: telegram.ext.CallbackContext):
        '''
            Jobqueue's Updaytt function
            it will up date day timetable on working days after 04:30 pm
        '''
        self.db.upddaytt()
        tchlst = self.db.gettchlst()

        for i in tchlst:
            text = "Sir/Madam Next {} \n timetable was updated.\nYou can make changes in the timetable now".format( datetime.datetime.now(tz= timezone('Asia/Kolkata')).strftime("%A"))
            context.bot.send_message(chat_id=i[0], text=text, parse_mode= 'Markdown')
            time.sleep(1)

    def callback_daily(self,context: telegram.ext.CallbackContext):
        '''
            Jobqueue's callback_daily function
        '''
        tchlst = self.db.gettchlst()
        tchcnt = len(tchlst)

        for i in tchlst:
            text = "*Today's Timetable*\n"+self.tchtt(i[0])
            context.bot.send_message(chat_id=i[0], text=text, parse_mode= 'Markdown')
            time.sleep(1)
        for i in devjson["devChat_id"]:
            context.bot.send_message(chat_id="i", text="Total no of users using\nCR ATL(TCH)\n = *{}*".format(tchcnt), parse_mode= 'Markdown')


    # Invalid Input Functions

    def error(self,update, context):
        """Log Errors caused by Updates."""
        logger.warning('caused error "%s"', context.error)


    def ivid(self, update, context):
        '''
            Function to send error when user enters Invalid Roll Number in Roll no setup cov
        '''
        update.message.reply_text(text='''*Invalid or Already registered Employee ID*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please try again with  \n*A Valid Employee ID*''', parse_mode= 'Markdown')
        if context.user_data['updtch']:
            return self.Empupd_MH
        else:
            return self.Setup_MH

    def ivmnuopt(self, update, context):
        '''
            Executed when Bot get undesired input in Menu cov
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Option*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Menu_opt_MH

    def ivccday(self, update, context):
        '''
            Executed when Bot get undesired input in Cancel cls cov -  day input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Day*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Ccl_cls_MH

    def ivccpgs(self, update, context):
        '''
            Executed when Bot get undesired input in Cancel cls cov - Period:Grade:Subject input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Period*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Ccl_day_MH

    def ivtkgs(self, update, context):
        '''
            Executed when Bot get undesired input in Take cls cov - Grade:Subject input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Subject*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Take_cls_MH

    def ivtkday(self, update, context):
        '''
            Executed when Bot get undesired input in Take cls cov -  day input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Day*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Take_grd_MH

    def ivtkper(self, update, context):
        '''
            Executed when Bot get undesired input in Take cls cov - Period input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Period*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Take_day_MH

    def ivanngrd(self, update, context):
        '''
            Executed when Bot get undesired input in Announcement cov - Grade input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Grade*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Announce_grd_MH

    def ivannmsg(self, update, context):
        '''
            Executed when Bot get undesired input in Announcement cov - msg input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Message*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please Start the message with \n* MSG-* ''', parse_mode= 'Markdown')
        return self.Announce_msg_MH

    def ivanncon(self, update, context):
        '''
            Executed when Bot get undesired input in Announcement cov - msg input
        '''
        update.message.reply_text(text='''Please Send Either \n*Send* or *Back*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD*''', parse_mode= 'Markdown')
        return self.Announce_conf_MH

    def ivgrdgrd(self, update, context):
        '''
            Executed when Bot get undesired input in Grade cov - Grade input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Grade*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Grade_btt_MH

    def ivgrdday(self, update, context):
        '''
            Executed when Bot get undesired input in Grade cov -  day input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Day*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Grade_sub_MH

    def ivdlyday(self, update, context):
        '''
            Executed when Bot get undesired input in Grade cov -  day input
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Day*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Day_MH

    # Go Back functions
    def bckmenu(self,update,context):
        '''
            End the first level conv and send back to main menu
        '''
        self.menu(update,context)
        return END

    def bckgrdgrdkb(self,update,context):
        '''
            End the second level conv of grade timetable
            and send back to grade list level(First level)
        '''
        self.grdgrdkb(update,context)
        return END

    def bckccdaykb(self,update,context):
        '''
            End the second level conv of Cancel class
            and send back to grade list level(Second level)
        '''
        self.ccdaykb(update,context)
        return END

    def bcktkegrdkb(self,update,context):
        '''
            End the second level conv of Take class
            and send back to grade:subject list level(First level)
        '''
        self.tkegrdkb(update,context)
        return END

    def bcktkedaykb(self,update,context):
        '''
            End the Third level conv of Take class
            and send back to Day list level(Second level)
        '''
        self.tkedaykb(update,context)
        return END
        
    def bckanngrdkb(self,update,context):
        '''
            End the second level conv of announcement class
            and send back to Grade list level(first level)
        '''
        self.anngrdkb(update,context)
        return END

    def menucall (self,update,context):
        '''
            Return to the menu
        '''
        self.menu(update,context)
        return self.STOPPING

    # Start or Setup Functions

    def start (self, update, context):
        '''
            Function to execute when /start is input and asks for user employee id 
        '''
        emp_id = self.db.chktch(update.effective_chat.id)
        context.user_data['updtch'] = False
        if emp_id == None:
            update.message.reply_text(text='''Hi ! {}'''.format(update.message.from_user.first_name), parse_mode= 'Markdown')
            update.message.reply_text(text='''Welcome to your Personal\nTimetable and Announcement Manager - \n             " *CR ALT* "''', parse_mode= 'Markdown')
            update.message.reply_text(text='''Please enter  *Your IIITT Employee ID* for Signing up''', parse_mode= 'Markdown')
            return self.Setup_MH
        else:
            text = [['Menu']]
            update.message.reply_text(text='''Welcome! {}'''.format(update.message.from_user.first_name), parse_mode= 'Markdown')
            update.message.reply_text(text='''You have logged in with {}'''.format(emp_id), parse_mode= 'Markdown')
            update.message.reply_text("Click on *Menu* to visit Menu", parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup(text))
            return self.Empupd_MH

    def empid(self, update, context):
        '''
            Function to link the Eployee id with chat id 
        '''
        emp_id = self.db.tchsetup(update.effective_chat.id,(update.message.text).upper(),context.user_data['updtch'])
        if emp_id:
            context.user_data['updtch'] = False
            update.message.reply_text(text="Your Employee {}, \n linked to your account \nSuccessfully".format(emp_id))
            update.message.text = emp_id
            return self.start(update, context)  
        else:
            return self.ivid(update, context)

    def empupd(self,update,context):
        '''
            Updates Teacher Employee id to the given Chat id
        '''
        context.user_data['updtch'] = True
        update.message.reply_text("Please Enter Your *IIITT* Employee id :", parse_mode= 'Markdown', reply_markup=telegram.ReplyKeyboardMarkup([["Cancel"]]))
        return END

    # Menu Functions

    def menu(self, update, context):
        '''
            Default Menu Function
        '''
        logger.info("User %s is using CR ALT (Techer ver).", update.message.from_user.first_name)
        text = [["Today's Timetable","Daily Timetable"],["Batch Timetable","Announcement"],["Take Class","Cancel Class"],['Change Your EMPLOYEE ID']]
        update.message.reply_text(text='''Select an option from the\ngiven menu''', reply_markup=telegram.ReplyKeyboardMarkup(text))
        return self.Menu_opt_MH

    # Teacher Timetable Functions

    def tchtt(self,chat_id,day= datetime.datetime.now(tz=timezone('Asia/Kolkata')).strftime("%A")):
        '''
            Return Teacher Timetable as a string
        '''
        perlst=self.db.getTeachtt(chat_id,day)
        text = "Time        :  Batch  : Subject\n"
        for i in perlst:
            text = text + i[0] + " : " + i[1]+ " : " + i[2]+"\n"
        if len(text)>32:
            return text
        else:
            return "No Classes"
    
    def tchtdt(self, update, context):
        '''
            Sends today's Timetable to the Teacher
        '''
        text = self.tchtt(update.effective_chat.id)
        if text == "No Classes":
            update.message.reply_text(text="No Classes Today")
            return self.Menu_opt_MH
        else:
            update.message.reply_text(text=text)
            return self.Menu_opt_MH

    def tchdtt(self, update, context):
        '''
            Sends the Timetable of the given day to the teacher
        '''
        if (update.message.text).capitalize() in self.daylst:#
            text = self.tchtt(update.effective_chat.id,(update.message.text).capitalize())#
            if text == "No Classes":
                update.message.reply_text(text="No Classes on {}".format((update.message.text).capitalize()))
                return self.Day_MH
            else:
                update.message.reply_text(text=text)
                return self.Day_MH
        else:
            update.message.reply_text(text="Select a *valid day*\nfrom the given list",parse_mode= 'Markdown')
            return self.Day_MH
    
    def daykb (self, update, context):
        '''
            Send Days as keyboard
        '''
        text = [[self.daylst[0],self.daylst[1]],[self.daylst[2],self.daylst[3]],[self.daylst[4],self.daylst[5]]]
        update.message.reply_text(text='''Select a Day from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
        return self.Day_MH

    # Grade Timetable functions

    def grdgrdkb(self, update, context):
        '''
            Send grades as Keyboard
        '''
        tchgrd = self.db.tchgrdsub(update.effective_chat.id)
        tchgrdlst = [["Back"]]
        self.grdgrdchklst = ['Back']
        tchgrdset = set()
        for i in tchgrd:
            tchgrdset.add(i[0])
        for i in tchgrdset:
            tchgrdlst.append([i])
            self.grdgrdchklst.append(i)
        update.message.reply_text(text='''Select a Grade from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(tchgrdlst))
        return self.Grade_btt_MH

    def grdttdaykb(self, update, context):
        '''
            Stores the grade of grade timetable function,send days as keyboard 
        '''
        if (update.message.text).upper() in self.grdgrdchklst:
            context.user_data['Grdttsub'] = (update.message.text).upper()
            text = [[self.daylst[0],self.daylst[1]],[self.daylst[2],self.daylst[3]],[self.daylst[4],self.daylst[5]]]
            update.message.reply_text(text='''Select a Day from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
            return self.Grade_sub_MH
        else:
            update.message.reply_text(text='''Select a *Valid Grade* \nfrom the given list''',parse_mode = 'Markdown')
            return self.Grade_btt_MH
    
    def grddtt(self, update, context):
        '''
            Returns grade timetable to teacher
        '''
        grdday = (update.message.text)#
        if (grdday).capitalize() in self.daylst:
            perlst=self.db.getStdtt(context.user_data['Grdttsub'],grdday.capitalize())
            text = "Time     : Subject\n"
            for i in perlst:
                text = text + i[0] + " : " + i[1]+"\n"
            if len(text)>19:
                update.message.reply_text(text=text)
            else:
                update.message.reply_text(text="No Classes on {}".format((grdday).capitalize()))     
        else:
            update.message.reply_text(text="Select a *Valid Day* \nfrom the given list",parse_mode = 'Markdown')
        return self.Grade_sub_MH

    # Announcement functions

    def anngrdkb(self, update, context):
        '''
            Send grades as Keyboard
        '''
        tchgrd = self.db.tchgrdsub(update.effective_chat.id)
        tchgrdlst = [["Back"]]
        self.anngrdchklst = ['Back']
        tchgrdset = set()
        for i in tchgrd:
            tchgrdset.add(i[0])
        for i in tchgrdset:
            tchgrdlst.append([i])
            self.anngrdchklst.append(i)  
        update.message.reply_text(text='''Select a Grade from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(tchgrdlst))
        return self.Announce_grd_MH

    def annmsg(self, update, context):
        '''
            Asks teacher to send the msg to which she want to pass to the given grade
        '''
        if (update.message.text).upper() in self.anngrdchklst:
            if not update.message.text == 'Back':
                context.user_data['Annmsggrd'] = (update.message.text).upper()
                context.user_data['Usrnm'] =  update.message.from_user.first_name
            update.message.reply_text(text="Please send the message you want us to pass to *{}* Batch".format(context.user_data['Annmsggrd']), parse_mode= 'Markdown') 
            update.message.reply_text(text="send the message starts with MSG-(YOUR MESSAGE). Example:")
            update.message.reply_text(text="MSG-Hi students welcome to CR ALT",reply_markup=telegram.ReplyKeyboardMarkup([["Back"]]))
            return self.Announce_msg_MH
        else:
            update.message.reply_text(text='''Select a *Valid Grade* \nfrom the given list''',parse_mode = 'Markdown')
            return self.Announce_grd_MH

    def anncon(self, update, context):
        '''
            Asks teacher to conform before sending the msg 
        '''
        context.user_data['Annmsg'] = (update.message.text)[4:]
        text='''You want us to send message *"{}"* to *{}* Batch'''.format(context.user_data['Annmsg'],context.user_data['Annmsggrd'])
        annikdata =  context.user_data['Usrnm']  + '<>' + context.user_data['Annmsggrd'] + '<>' + context.user_data['Annmsg']
        keyboard = [
                            [InlineKeyboardButton("Send",callback_data= '1' + annikdata),
                            InlineKeyboardButton("Cancel",callback_data= '0' ) ],
                        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text = text, reply_markup=reply_markup, parse_mode= 'Markdown')
        return self.bckanngrdkb(update, context)

    def annsnd(self, update, context):
        '''
            Send teacher msg to students
        '''
        query = update.callback_query
        query.answer()
        if query.data[:1] == '1':
            anndata = query.data[1:].split('<>',2)
            text = urllib.parse.quote_plus(anndata[2])
            stdchtidlst = self.db.grdstdid(anndata[1].upper())
            query.edit_message_text(text='''Please wait we are sending Your message to the students''')
            text = "Sir/Madam {}, sends you this message -\n".format(anndata[0] ) + text
            cnt = 0
            for i in stdchtidlst:
                chat_id = i[0]
                URL = "http://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}".format(stdtkn,text,chat_id)
                requests.get(URL)
                cnt = cnt + 1
            query.edit_message_text(text="Your Message was sent to *{}* students in *{}* Batch".format(cnt,anndata[1]),parse_mode= 'Markdown')
        else:
            query.edit_message_text(text="You Cancelled your request")

    # take class functions

    def tkegrdkb(self, update, context):
        '''
            Send grades:subject as Keyboard
        '''
        tchgrd = self.db.tchgrdsub(update.effective_chat.id)
        tchgrdlst = [["Back"]]
        self.gschklst = ['Back']
        for i in tchgrd:
            tchgrdlst.append([i[0]+":"+i[1]])
            self.gschklst.append(i[0]+":"+i[1])
            
        update.message.reply_text(text='''Select a Grade:Subject from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(tchgrdlst))
        return self.Take_cls_MH

    def tkedaykb(self, update, context):
        '''
            Stores the grade:subject of  take class function,send days as keyboard 
        '''
        if (update.message.text in self.gschklst):
            if (not update.message.text == 'Back'):
                context.user_data['tkegrd'] = (update.message.text).upper()
            text = [[self.daylst[0],self.daylst[1]],[self.daylst[2],self.daylst[3]],[self.daylst[4],self.daylst[5]]]#
            update.message.reply_text(text='''Select a Day from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
            return self.Take_grd_MH
        else:
            update.message.reply_text(text='''Select a valid *Grade:Subject*\nfrom the given list''',parse_mode = 'Markdown')
            return self.Take_cls_MH

    def tkeperkb(self, update, context):
        '''
            Stores the day of  take class function,send period as keyboard 
        '''
        if (update.message.text).capitalize() in self.daylst:
            if (not update.message.text == 'Back'):
                context.user_data['tkeday'] = (update.message.text).capitalize()
            grade = context.user_data['tkegrd'].split(':')[0]
            persublst = self.db.getStdtt(grade,context.user_data['tkeday'])
            perlst = list()
            tchperlst = list()
            fbydata = json.loads(open('json/branchYearlist.json').read()) #access json file
            text = [["Back"]]
            for i in persublst:
                perlst.append(i[0])
            for i in self.db.getTeachtt(update.effective_chat.id,context.user_data['tkeday']):
                tchperlst.append(i[0])
            self.perchklst = ['Back']
            for i in periodlst:
                if (i not in perlst) and ((i not in tchperlst) or (grade[3:] == str(max(fbydata['year'])%100))):
                    text.append([i])
                    self.perchklst.append(i)
            update.message.reply_text(text=''' For "{}" Select a Period from the\ngiven list'''.format(context.user_data['tkegrd']), reply_markup=telegram.ReplyKeyboardMarkup(text))
            return self.Take_day_MH
        else:
            update.message.reply_text(text='''Select a *Valid Day*\nfrom the given list''',parse_mode= 'Markdown')
            return self.Take_grd_MH

    def tkecls(self, update, context):
        '''
            Create class in the timetable
        '''
        if update.message.text in self.perchklst:
            tcikdata = context.user_data['tkegrd'] + ':' + update.message.text + ':' + context.user_data['tkeday'] + ':' + update.message.from_user.first_name 
            tcdata = tcikdata.split(':')
            text='''You want us to Create Class for \nsubject {} of {} \non {} : {}'''.format(tcdata[1].upper(),tcdata[0].upper(),tcdata[3],tcdata[2])
            # tcikdate = grade:subject:period:day:Name
            keyboard = [
                                [InlineKeyboardButton("Yes",callback_data= '3' + tcikdata),
                                InlineKeyboardButton("No",callback_data= '2' ) ],
                            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(text = text, reply_markup=reply_markup, parse_mode= 'Markdown')
        else:
            update.message.reply_text(text = 'There was an error *Please try again*', parse_mode= 'Markdown')
        return self.menucall(update, context)

    def tkeclsmsg(self,update,context: telegram.ext.CallbackContext):
        '''
            Send message to the students
        '''
        query = update.callback_query
        query.answer()
        if query.data[:1] == '3':
            tcdata = query.data[1:].split(':')
            chk = self.db.crecls(tcdata[0].upper(),tcdata[1].upper(),tcdata[2],tcdata[3])
            if not chk == -1:
                query.edit_message_text(text='''Please wait we are sending Your message to the students''',parse_mode= 'Markdown' )
                text='''Class for subject {} of {} created on {} : {} by Sir/Mam {}'''.format(tcdata[1],tcdata[0],tcdata[3],tcdata[2],tcdata[4])
                stdchtidlst = self.db.grdstdid(tcdata[0])
                text =text + '\nPlease Check your Timetable ' 
                cnt = 0
                for i in stdchtidlst:
                    chat_id = i[0]
                    URL = "http://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}".format(stdtkn,text,chat_id)
                    requests.get(URL)
                    cnt = cnt + 1
                query.edit_message_text(text=text + "\nYour Message was sent to *{}* students in *{}* Batch".format(cnt,tcdata[0]),parse_mode= 'Markdown')
            else:
                query.edit_message_text(text='''There was an error :\n*Selected period slot is not empty*,\nplease try again ''',parse_mode= 'Markdown' )
        else:
            query.edit_message_text(text="You Cancelled your request")

    # Cancel class

    def ccdaykb (self, update, context):
        '''
            Send Days as keyboard for cancel class
        '''
        text = [[self.daylst[0],self.daylst[1]],[self.daylst[2],self.daylst[3]],[self.daylst[4],self.daylst[5]]]
        update.message.reply_text(text='''Select a Day from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
        return self.Ccl_cls_MH

    def ccgrdkb (self, update, context):
        '''
            Store day 
            Send Period:Grade:Subject as Keyboard
        '''
        if (update.message.text).capitalize() in self.daylst:
            if (not update.message.text == 'Back'):
                context.user_data['ccday'] = (update.message.text).capitalize()
            perlst=self.db.getTeachtt(update.effective_chat.id,context.user_data['ccday'])
            text = [["Back"]]
            self.pgschklst = ['Back']
            for i in perlst:
                text.append([i[0] + ":" + i[1]+ ":" + i[2]])
                self.pgschklst.append(i[0] + ":" + i[1]+ ":" + i[2])
            update.message.reply_text(text=''' Select a Period from {} Timetable in list'''.format(context.user_data['ccday']), reply_markup=telegram.ReplyKeyboardMarkup(text))
            return self.Ccl_day_MH
        else:
            update.message.reply_text(text='''Select a *Valid Day*\nfrom the given list''',parse_mode = 'Markdown')
            return self.Ccl_cls_MH

    def ccls(self, update, context):
        '''
        Delete class from the gven day and period
        '''
        if update.message.text in self.pgschklst:
            ccdata = update.message.text.split(':')
            text='''You want us to Cancel Class for \nsubject {} of {} \non {} : {}'''.format(ccdata[2].upper(),ccdata[1],context.user_data['ccday'],ccdata[0])
            ccikdata = update.message.text + ':' + context.user_data['ccday'] + ':' + update.message.from_user.first_name
            #ccikdata = Period:Grade:Subject:Day:Name
            keyboard = [
                                [InlineKeyboardButton("Yes",callback_data= '5' + ccikdata),
                                InlineKeyboardButton("No",callback_data= '4' ) ],
                            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(text = text, reply_markup=reply_markup, parse_mode= 'Markdown')
        else:
            update.message.reply_text(text = 'There was an error *Please try again*', parse_mode= 'Markdown')
        return self.menucall(update, context)

    def cclsmsg(self,update,contextcontext: telegram.ext.CallbackContext):
        '''
            Send message to the students
        '''
        query = update.callback_query
        query.answer()
        if query.data[:1] == '5':
            ccdata = query.data[1:].split(':')
            chk = self.db.delcls(ccdata[1].upper(),ccdata[2].upper(),ccdata[0],ccdata[3])
            if chk == 1:
                query.edit_message_text(text='''Please wait we are sending Your message to the students''',parse_mode= 'Markdown' )
                text='''Class for subject {} of {} on {} : {} was Cancelled by Sir/Mam {}'''.format(ccdata[2].upper(),ccdata[1],ccdata[3],ccdata[0],ccdata[4])
                stdchtidlst = self.db.grdstdid(ccdata[1])
                text =text + '\nPlease Check your Timetable ' 
                cnt = 0
                for i in stdchtidlst:
                    chat_id = i[0]
                    URL = "http://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}".format(stdtkn,text,chat_id)
                    requests.get(URL)
                    cnt = cnt + 1
                query.edit_message_text(text=text + "\nYour Message was sent to *{}* students in *{}* Batch".format(cnt,ccdata[1]),parse_mode= 'Markdown')
            else:
                query.edit_message_text(text='''There was an error :\n*Selected period Does not exist*,\nplease try again ''',parse_mode= 'Markdown' )
        else:
            query.edit_message_text(text="You Cancelled your request")


    # Admin options
    def usrann(self,update, context):
        '''
            conformation for Sending msg to all users in the bot using inlinekeyboard
        '''
        payload = context.args
        text = 'You want to send this message to every one:\n'
        msgtext = str()
        chk = False
        if payload[0] == 'MSG' and (update.effective_chat.id in devjson['devChat_id']):
            payload.pop(0)
            for i in payload:
                if i == "<>":
                    msgtext += '\n' 
                else:
                    msgtext += i + ' '
            text += msgtext
            keyboard = [
                            [InlineKeyboardButton("Send",callback_data= '7' + msgtext),
                            InlineKeyboardButton("Cancel",callback_data= '6' ) ],
                        ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(text = text, reply_markup=reply_markup)

    def inlineannall(self,update,context: telegram.ext.CallbackContext):
        '''
            Sending msg to all users in the bot
        '''
        query = update.callback_query
        query.answer()
        if query.data[:1] == '7':
            stdchtidlst = self.db.getaltchuid()
            query.edit_message_text(text='''Please wait we are sending Your message to the users''')
            text = ("Message from CR_ALT Bot Developers : \n" + query.data[1:])
            cnt = 0
            for i in stdchtidlst:
                chat_id = i[0]
                context.bot.send_message(chat_id= chat_id , text=text)
                cnt = cnt + 1
            query.edit_message_text(text="Your Message was sent to {} users".format(cnt))
        else:
            query.edit_message_text(text="You Cancelled your request")

if __name__ == '__main__':
    db = teleDb()
    hi = tchchat(db)
    hi.updater.start_polling()
    print("Getting Updates of CR_ALT(TCH)")
    hi.updater.idle()