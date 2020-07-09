import datetime, json, re, time
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler,  PicklePersistence, CallbackContext, CallbackQueryHandler
import logging, pytz
from pytz import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from python.dbCreate import teleDb
#from dbCreate import teleDb
stdtkn = open('data/stdtkn.txt').read()
bot = telegram.Bot(token=stdtkn)
fbhyr = open('json/developer.json').read() #access json file
fbydata = json.loads(open('json/branchYearlist.json').read()) #access json file
devjson = json.loads(fbhyr)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
END = ConversationHandler.END
logger = logging.getLogger(__name__)
class stdchat:
    '''
        Class for telegram chat bot - CR_Alt (STUDENT VER)
    '''
    #Constants to use in dict as keys for Conversation Handler
    Setup_MH, Rollupd_MH, Menu_opt_MH, Day_MH, Set_Atd_MH, Set_Atdpa_MH= range(6)

    #init function

    def __init__(self,db):
        '''
            Init  self.updater,Jobqueue,
            Adds message handlers, nested conversation handlers,
            starts polling
        '''
        self.db = db
        self.daylst = fbydata["daylst"]
        self.daylst.append("Back")
        self.dayinkb = list()
        if len(self.daylst)%2 == 0 :
            for i,j in zip(self.daylst[0::2],self.daylst[1::2]):
                self.dayinkb.append([i,j])
        else:
            last = (self.daylst).pop()
            for i,j in zip(self.daylst[0::2],self.daylst[1::2]):
                self.dayinkb.append([i,j])
            self.daylst.append(last)
            self.dayinkb.append([last])
        
        pp = PicklePersistence(filename='data/Stdcraltbot')
        self.updater = Updater(token=stdtkn,persistence=pp,use_context=True)
        dp =  self.updater.dispatcher
        j =  self.updater.job_queue
        daytuple = tuple(range(len(self.daylst)-1))

        ## Have to edit based on period list 
        j.run_daily(self.callback_daily,datetime.time(hour = 1, minute = 15, tzinfo = timezone('Asia/Kolkata')),daytuple,context=telegram.ext.CallbackContext)
        j.run_daily(self.daily_11_00,datetime.time(hour = 11, minute = 00, tzinfo = timezone('Asia/Kolkata')),daytuple,context=telegram.ext.CallbackContext)
        j.run_daily(self.daily_11_50,datetime.time(hour = 11, minute = 50, tzinfo = timezone('Asia/Kolkata')),daytuple,context=telegram.ext.CallbackContext)
        j.run_daily(self.daily_12_40,datetime.time(hour = 12, minute = 40, tzinfo = timezone('Asia/Kolkata')),daytuple,context=telegram.ext.CallbackContext)
        j.run_daily(self.daily_14_20,datetime.time(hour = 14, minute = 20, tzinfo = timezone('Asia/Kolkata')),daytuple,context=telegram.ext.CallbackContext)
        j.run_daily(self.daily_15_10,datetime.time(hour = 15, minute = 10, tzinfo = timezone('Asia/Kolkata')),daytuple,context=telegram.ext.CallbackContext)
        j.run_daily(self.daily_16_00,datetime.time(hour = 16, minute = 00, tzinfo = timezone('Asia/Kolkata')),daytuple,context=telegram.ext.CallbackContext)
        ##

        # Daily timetable conv

        Daily_tt_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.text("Daily Timetable")),self.daykb)],
                    states= {
                        self.Day_MH : [MessageHandler((Filters.text & (Filters.regex(r".*[Dd][Aa][Yy]") ) 
                                                            & (~Filters.command('devann'))),self.stddtt),
                                            MessageHandler((Filters.text('Back')),self.bckmenu)
                                            ]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.command('devann') & ~ Filters.regex('.*[Dd][Aa][Yy]') & ~ Filters.text('Back')),self.ivdlyday)],
                    name= "dailyttcov",
                    persistent=True
                )

        # Set attendance conv

        Set_atdpa_cov = ConversationHandler(
                    entry_points=[MessageHandler(((Filters.regex(r"^[A-Za-z][A-Za-z][A-Za-z][A-Za-z][0-9][0-9]$") | 
                                    Filters.regex(r"^[Ee][0-9]$") | Filters.regex(r"^T&P$") ) ),self.selsubatd)],
                    states= {
                    self.Set_Atdpa_MH : [MessageHandler(((Filters.text("Present") | Filters.text("Absent") |
                                        Filters.regex(r"..?:..?") ) & (~Filters.command('devann'))),self.setsubat),
                                        MessageHandler((Filters.text('Back')),self.bckgetsublst)
                                        ]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler((~Filters.command('devann') & ~Filters.text("Present") & ~Filters.text("Absent") & ~Filters.regex(r"..?:..?") & ~Filters.text('Back') ),self.ivatdpa)],
                    name= "atdpacov",
                    persistent=True
                )
        Set_atd_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.text("Set Attendance")),self.getsubkb)],
                    states= {
                        self.Set_Atd_MH : [Set_atdpa_cov,
                                            MessageHandler((Filters.text('Back')),self.bckmenu)
                                            ]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler(((~Filters.command('devann') & ~ Filters.regex(r"^[A-Za-z][A-Za-z][A-Za-z][A-Za-z][0-9][0-9]$") & 
                                    ~ Filters.regex(r"^[Ee][0-9]$") & ~Filters.regex(r"^T&P$") & ~Filters.text('Back')) ),self.ivatdsub)],
                    name= "atdcov",                    
                    persistent=True
                )

        # Menu conv
        
        Menu_cov = ConversationHandler(
                    entry_points=[MessageHandler((Filters.text('Menu') | Filters.text('Cancel')) ,self.menu)],
                    states= {
                        self.Menu_opt_MH : [MessageHandler((Filters.text("Today's Timetable")),self.stdtdt),
                                                Daily_tt_cov,MessageHandler((Filters.text("Get Attendance")),self.getstdatd),
                                                Set_atd_cov,(MessageHandler(Filters.text('Change Your ROLL NO'),self.rollupd))]
                    },
                    allow_reentry= True,
                    fallbacks = [MessageHandler(~Filters.command('devann') & ~Filters.text("Today's Timetable") & ~Filters.text("Get Attendance") 
                                        & ~Filters.text('Change Your ROLL NO') & ~Filters.text("Set Attendance") & ~Filters.text("Daily Timetable"),self.ivmnuopt)],
                    name= "menucov",
                    persistent=True
                )

        # Setup conv or Start conv

        Setup_cov = ConversationHandler(
                    entry_points=[CommandHandler('start', self.start)],
                    states={
                        self.Setup_MH : [(MessageHandler(Filters.regex(r'^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$'), self.rollno ))],
                        self.Rollupd_MH : [(MessageHandler(Filters.regex(r'^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$'), self.rollno )),
                                                Menu_cov]
                    },
                    allow_reentry= True,
                    fallbacks=[MessageHandler(~Filters.command('devann') & ~Filters.regex(r'^[CcEe][SsCc][Ee][1-2][0-9][Uu]0[0-3][0-9]$') & ~Filters.text('Menu') & ~Filters.text('Cancel'), self.ivroll ),
                                ],
                    name= "setupcov",
                    persistent=True,
                )
        
        dp.add_handler(Setup_cov)
        dp.add_handler(CommandHandler("devann", self.usrann, Filters.regex('MSG'),pass_args=True))
        dp.add_handler(CallbackQueryHandler(self.inlinesetatt,pattern='^[012].*'))
        dp.add_handler(CallbackQueryHandler(self.inlineannall,pattern='^[34].*'))
        dp.add_error_handler(self.error)
        

    # Invalid input functions
    def error(self,update, context):
        """Log Errors caused by Updates."""
        logger.warning('caused error "%s"', context.error)


    def ivroll(self, update, context):
        ''' Function to send error when user enters Invalid Roll Number in Roll no setup cov'''
        update.message.reply_text(text='''*Invalid or Already registered Roll Number*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please try again with  \n*A Valid Roll Number*''', parse_mode= 'Markdown')
        if context.user_data['updusr']:
            return self.Rollupd_MH
        else:
            return self.Setup_MH

    def ivdlyday(self, update, context):
        ''' Function to send error when user enters Invalid Day in daily timetable'''
        update.message.reply_text(text='''Please Send \n*A Valid Day*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD*''', parse_mode= 'Markdown')
        return self.Day_MH

    def ivatdpa(self, update, context):
        ''' Function to send error when user enters Invalid Attendance in attendance cov'''
        update.message.reply_text(text='''Please Send  \n*Present, Absent or \nAttendance in pp:tt pattern*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD*''', parse_mode= 'Markdown')
        return self.Set_Atdpa_MH
        
    def ivatdsub(self, update, context):
        ''' Function to send error when user enters Invalid Subject in Set attendance cov'''
        update.message.reply_text(text='''Please Send \n*A Valid Subject*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD*''', parse_mode= 'Markdown')
        return self.Set_Atd_MH
        
    def ivmnuopt(self, update, context):
        '''
            Executed when Bot get undesired input in Menu cov
        '''
        update.message.reply_text(text='''Please Send a \n*Valid Option*''', parse_mode= 'Markdown')
        update.message.reply_text(text='''Please prefer using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        return self.Menu_opt_MH


    # Go Back functions
    def bckmenu(self,update,context):
        '''
            End the first level conv and send back to main menu
        '''
        self.menu(update,context)
        return END

    def bckgetsublst(self,update,context):
        '''
            End the second level conv of attend function and send back to subject list
        '''
        self.getsubkb(update,context)
        return END


    # Jobqueue Functions

    

    def callback_daily(self,context: telegram.ext.CallbackContext):
        '''
            Jobqueue's callback_daily function
        '''
        usrlst = self.db.getusrlst()
        self.usrcnt = len(usrlst)

        for i in usrlst:
            text = "*Today's Timetable*\n"+self.stdtt(i[0])
            context.bot.send_message(chat_id=i[0], text=text, parse_mode= 'Markdown')
        for i in devjson["devChat_id"]:
            context.bot.send_message(chat_id=i, text="Total no of users using\nCR ATL = *{}*".format(tchcnt), parse_mode= 'Markdown')

    # job functions for asking attendance
    def daily (self,pernm,context):
        '''
            Jobqueue's daily function to Ask for attendance
        '''
        stdchtidlst = self.db.getusrlst()
        for k in stdchtidlst:
            persublst=self.db.getStdtt(self.db.getusrgrd(k[0]),datetime.datetime.now(tz= timezone('Asia/Kolkata')).strftime("%A"))
            perlst = list()
            for i in persublst:
                if i[0] == pernm:
                    keyboard = [
                        [InlineKeyboardButton("Yes",callback_data= str('1'+i[1])),
                        InlineKeyboardButton("No",callback_data= str('0'+i[1]))],
                        [InlineKeyboardButton("Cancel",callback_data= str('2'+i[1]))]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    context.bot.send_message(chat_id=k[0], text= "Did you attend the class of subject {} @ {}".format(i[1],pernm),
                        reply_markup=reply_markup)
                    break

    def daily_11_00 (self,context: telegram.ext.CallbackContext):
        self.daily('10.10-11.00',context)
    def daily_11_50 (self,context: telegram.ext.CallbackContext):
        self.daily('11.00-11.50',context)
    def daily_12_40 (self,context: telegram.ext.CallbackContext):
        self.daily('11.50-12.40',context)
    def daily_14_20 (self,context: telegram.ext.CallbackContext):
        self.daily('01.30-02.20',context)
    def daily_15_10 (self,context: telegram.ext.CallbackContext):
        self.daily('02.20-03.10',context)
    def daily_16_00 (self,context: telegram.ext.CallbackContext):
        self.daily('03.10-04.00',context)
    
    def inlinesetatt(self,update,context):
        '''
            Inline function for set attendance
        '''
        query = update.callback_query
        query.answer()
        if query.data[:1] == '1':
            self.db.setstdatt(update.effective_chat.id,query.data[1:],int(query.data[:1]),1)
            query.edit_message_text(text="You were PRESENT for {} class".format(query.data[1:]))
        elif query.data[:1] == '0':
            self.db.setstdatt(update.effective_chat.id,query.data[1:],int(query.data[:1]),1)
            query.edit_message_text(text="You were ABSENT for {} class".format(query.data[1:]))
        else:
            query.edit_message_text(text="{} class was CANCELED".format(query.data[1:]))

    # Setup Functions or Start Functions

    def start(self, update, context):
        '''
            Function to execute when /start is input and asks for user roll_no or id_no 
        '''
        roll_no = self.db.chkusr(update.effective_chat.id)
        context.user_data['updusr'] = False
        if roll_no == None:
            update.message.reply_text(text='''Hi! {}'''.format(update.message.from_user.first_name), parse_mode= 'Markdown')
            update.message.reply_text(text='''Welcome to your Personal\nTimetable and attendance Manager - \n             " *CR ALT* "''', parse_mode= 'Markdown')
            update.message.reply_text(text='''Please enter  *YOUR IIITT ROLL NO* for Signing up''', parse_mode= 'Markdown')
            return self.Setup_MH
        else:
            update.message.reply_text(text='''Welcome! {}'''.format(update.message.from_user.first_name), parse_mode= 'Markdown')
            update.message.reply_text(text='''You have logged in with *{}*'''.format(roll_no), parse_mode= 'Markdown')
            update.message.reply_text("Click on *Menu* to visit Menu", parse_mode= 'Markdown',reply_markup=telegram.ReplyKeyboardMarkup([["Menu"]]))
            return self.Rollupd_MH

    def rollno(self, update, context):
        '''
            Function to link the roll number with chat id 
        '''
        rollno = self.db.usrsetup(update.effective_chat.id,(update.message.text).upper(),context.user_data['updusr'])
        if rollno:
            context.user_data['updusr'] = False
            update.message.reply_text(text="Your Roll no {}, \n linked to your account \nSuccessfully".format(rollno))
            update.message.text = rollno
            return self.start(update, context)  
        else:
            return self.ivroll(update, context)

    def rollupd(self,update,context):
        '''
            Updates User roll no
        '''
        context.user_data['updusr'] = True
        update.message.reply_text("Please Enter Your *IIITT* roll no to login:", parse_mode= 'Markdown', reply_markup=telegram.ReplyKeyboardMarkup([["Cancel"]]))
        return END

    # Menu Functions

    def menu(self, update, context):
        '''
            Default Menu Function
        '''
        logger.info("User %s is using CR ALT.", update.message.from_user.first_name) ### Comment out Before Launch
        text = [["Today's Timetable","Daily Timetable"],["Get Attendance","Set Attendance"],["Change Your ROLL NO"]]
        update.message.reply_text(text='''Select an option from the\ngiven menu''', reply_markup=telegram.ReplyKeyboardMarkup(text))
        return self.Menu_opt_MH

    # Student timetable Functions

    def stdtt(self,chat_id,day= datetime.datetime.now(tz= timezone('Asia/Kolkata')).strftime("%A")):
        '''
            Return student Timetable as a string
        '''
        perlst=self.db.getStdtt(self.db.getusrgrd(chat_id),day)
        text = "Time     : Subject\n"
        for i in perlst:
            text = text + i[0] + " : " + i[1]+"\n"
        if len(text)>19:
            return text
        else:
            return "No Classes"
    
    def stdtdt(self, update, context):
        '''
            Sends today's Timetable to the student
        '''
        text = self.stdtt(update.effective_chat.id)
        if text == "No Classes":
            update.message.reply_text(text="No Classes Today")
            return self.Menu_opt_MH
        else:
            update.message.reply_text(text=text)
            return self.Menu_opt_MH

    def stddtt(self, update, context):
        '''
            Sends the Timetable of the given day to the student
        '''
        if (update.message.text).capitalize() in self.daylst:
            text = self.stdtt(update.effective_chat.id,(update.message.text).capitalize())
            if text == "No Classes":
                update.message.reply_text(text="No Classes on {}".format((update.message.text).capitalize()))
            else:
                update.message.reply_text(text=text)
        else:
            update.message.reply_text(text="Please send *A Valid Day*\nfrom the given list ", parse_mode = 'Markdown')
        return self.Day_MH
    
    def daykb (self, update, context):
        '''
            Send Days as keyboard
        '''
        text = self.dayinkb
        update.message.reply_text(text='''Select a Day from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
        return self.Day_MH

    
    # Get student's Attendance Functions
    
    def getstdatd (self, update, context):
        '''
            sends student's attendance 
        '''
        atdlst = self.db.getstdatt(update.effective_chat.id)
        text = "Subject: pst : ttl : % : Bnk/atd\n"
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
            text = text + str(i[0]) + ' : ' + str(i[1]) + ' : ' + str(i[2]) + ' : ' + str(per) + " : " + str(bnk)+"\n"
        update.message.reply_text(text=text)
        return self.Menu_opt_MH

    # Set student's attendance Functions
        
    def getsubkb(self, update, context):
        '''
            Send subjects as keyboard
        '''
        sublst=self.db.getsubgrd(self.db.getusrgrd(update.effective_chat.id))
        text = list()
        self.subchklst = list()
        if len(sublst)%2 == 0:
            for i,j in zip(sublst[0::2],sublst[1::2]):
                text.append([i[0],j[0]])
                self.subchklst.append(i[0])
                self.subchklst.append(j[0])
            text.append(['Back'])
            self.subchklst.append('Back')
        else:
            sublst.append(['Back'])
            for i,j in zip(sublst[0::2],sublst[1::2]):
                text.append([i[0],j[0]])
                self.subchklst.append(i[0])
                self.subchklst.append(j[0])
        update.message.reply_text(text='''Select a Subject from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
        return self.Set_Atd_MH
    
    def selsubatd(self, update, context):
        '''
            Asks user for the status of the given subject (Present,Absent)
        '''
        if (update.message.text).upper() in self.subchklst:
            context.user_data['Subject'] = (update.message.text).upper()
            text = [["Present","Absent"],["Back"]]
            update.message.reply_text(text='''Select the status of {}\n '''.format((update.message.text).upper()), reply_markup=telegram.ReplyKeyboardMarkup(text))
            update.message.reply_text(text='''If you want to enter \nthe pnt and ttl class \nseperatly then enter\nThem in this pattern - \n *pp:tt* or *p:t* or *p:tt* \n(ex: 05:10)-\n5 out of 10 classes attended''', parse_mode= 'Markdown')
            return self.Set_Atdpa_MH
        else:
            update.message.reply_text(text='''Select a Valid Subject\nfrom the given list''', parse_mode = 'Markdown')
            return self.Set_Atd_MH


    def setsubat(self, update, context):
        '''
            Sets attendance for the given subjects
        '''
        subnm = context.user_data['Subject']
        resp = update.message.text
        if resp == 'Present':
            self.db.setstdatt(update.effective_chat.id,subnm)
        elif resp == 'Absent':
            self.db.setstdatt(update.effective_chat.id,subnm,0,1)
        else:
            att = resp.split(':')
            try:
                if (int(att[0]) > int(att[1])):
                    update.message.reply_text(text="Sorry,Present classes can't be greater than total classes")
                    raise Exception("Sorry,Present classes can't be greater than total classes")
                self.db.setstdatt(update.effective_chat.id,subnm,att[0],att[1])
            except:
                update.message.reply_text(text="Invalid Input, Try Again")
        self.getstdatd(update,context)
        self.getsubkb( update, context)
        return END

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
                            [InlineKeyboardButton("Send",callback_data= '3' + msgtext),
                            InlineKeyboardButton("Cancel",callback_data= '4' ) ],
                        ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(text = text, reply_markup=reply_markup)

    def inlineannall(self,update,context):
        '''
            Sending msg to all users in the bot
        '''
        query = update.callback_query
        query.answer()
        if not query.data == '4':
            stdchtidlst = self.db.getalstduid()
            query.edit_message_text(text='''Please wait we are sending Your message to the users''')
            text = ("Message from CR_ALT Bot Developers : \n" + str(query.data[1:]))
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
    hi = stdchat(db)
    hi.updater.start_polling()
    print("Getting Updates of CR_ALT")
    hi.updater.idle()