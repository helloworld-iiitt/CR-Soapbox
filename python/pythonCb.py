import datetime, json, re, time
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
# from python.dbCreate import teleDb
from dbCreate import teleDb

tkn = open('data/tkn.txt').read()
bot = telegram.Bot(token=tkn)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
class stdchat:
    '''
        Class for telegram chat bot - IIITT_TT_Bot
    '''
    def __init__(self,db):
        '''
            Init updater,Jobqueue,
            Adds message handlers,
            starts polling
        '''
        self.db = db
        self.subdic = dict()
        self.daylst = ['Monday','Tuesday','Wednesday','Thursday','Friday',"Go to Menu"]
        updater = Updater(token=tkn,use_context=True)
        dp = updater.dispatcher
        j = updater.job_queue
        j.run_daily(self.callback_daily,datetime.time(18,47,0,0),(0,1,2,3,4),context=telegram.ext.CallbackContext)
        # j.run_repeating(self.callback_daily, interval=60, first=0)
        
        dp.add_handler(CommandHandler('start', self.start))
        dp.add_handler(MessageHandler((Filters.text & Filters.regex('Go to Menu') & (~Filters.command)),self.menu))
        dp.add_handler(MessageHandler((Filters.regex(r'...[1-2][0-9]U0[0-3][0-9]') | Filters.regex(r'...[1-2][0-9]u0[0-3][0-9]')) & (~Filters.command), self.rollno ))
        dp.add_handler(MessageHandler((Filters.text & Filters.regex("Today's Timetable") & (~Filters.command)),self.stdtdt))
        dp.add_handler(MessageHandler((Filters.text & Filters.regex("Daily Timetable") & (~Filters.command)),self.daykb))
        dp.add_handler(MessageHandler((Filters.text & (Filters.regex(r".*DAY") | Filters.regex(r".*day") ) & (~Filters.command)),self.stddtt))
        dp.add_handler(MessageHandler((Filters.text & Filters.regex("Get Attendance") & (~Filters.command)),self.getstdatd))
        dp.add_handler(MessageHandler((Filters.text & Filters.regex("Set Attendance") & (~Filters.command)),self.getsubkb))
        dp.add_handler(MessageHandler((Filters.text & (Filters.regex(r"[A-Za-z][A-Za-z][A-Za-z][A-Za-z][0-9][0-9]") | Filters.regex(r"[A-Ba-z][0-9]") | Filters.regex("T&P") ) & (~Filters.command)),self.selsubatd))
        dp.add_handler(MessageHandler((Filters.text & (Filters.regex(r"Present") | Filters.regex(r"Absent") | Filters.regex(r"..:..") ) & (~Filters.command)),self.setsubat))
        dp.add_handler(MessageHandler((Filters.text & Filters.text & (~Filters.command)),self.default))
        
        updater.start_polling()
        print("Getting Updates")
        updater.idle()
    

    def default(self, update, context):
        '''
            Default function, Executed when Bot get undesired input
        '''
        context.bot.send_message(chat_id=update.effective_chat.id, text='''Please Send a \n*Valid Message or Command* ''', parse_mode= 'Markdown')
        context.bot.send_message(chat_id=update.effective_chat.id, text='''Please prefer to using\n*CUSTOM KEYBOARD* ''', parse_mode= 'Markdown')
        # self.menu(update,context)

    def callback_daily(self,context: telegram.ext.CallbackContext):
        '''
            Jobqueue's callback_daily function
        '''
        for i in self.db.getusrlst():
            text = "*Today's Timetable*\n"+self.stdtt(i[0])
            context.bot.send_message(chat_id=i[0], text=text, parse_mode= 'Markdown')
            time.sleep(2)

    def start(self, update, context):
        '''
            Function to execute when /start is input and asks for user roll_no or id_no 
        '''

        context.bot.send_message(chat_id=update.effective_chat.id, text='''Welcome to your Personal\nTimetable amd attendance Manager - \n             " *CR ALT* "''', parse_mode= 'Markdown')
        context.bot.send_message(chat_id=update.effective_chat.id, text='''Please enter  *YOUR ROLL NO* ''', parse_mode= 'Markdown')

    def rollno(self, update, context):
        '''
            Function to link the roll number with chat id 
        '''
        rollno = self.db.usrsetup(update.effective_chat.id,(update.message.text).upper())
        if rollno:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Account created for\nuser : {}\nSuccessfully".format(rollno))
            update.message.text = rollno
            self.menu(update,context)
        else:
            self.default(update, context)

    def menu(self, update, context):
        '''
            Default Menu Function
        '''
        text = [["Today's Timetable","Daily Timetable"],["Get Attendance","Set Attendance"]]
        try:
            self.subdic.pop(update.effective_chat.id)
        except:
            pass
        bot.send_message(chat_id=update.effective_chat.id, text='''Select an option from the\ngiven menu''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    
    def stdtt(self,chat_id,day= datetime.datetime.now().strftime("%A")):
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
            return "No Classes on " + day
    
    def stdtdt(self, update, context):
        '''
            Sends today's Timetable tothe student
        '''
        text = self.stdtt(update.effective_chat.id)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def stddtt(self, update, context):
        '''
            Sends the Timetable of the given day
        '''
        if (update.message.text).capitalize() in self.daylst:
            text = self.stdtt(update.effective_chat.id,(update.message.text).capitalize())
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No Classes on {}".format((update.message.text).capitalize()))
    
    def daykb (self, update, context):
        '''
            Send Days as keyboard
        '''
        text = [[self.daylst[0],self.daylst[1]],[self.daylst[2],self.daylst[3]],[self.daylst[4],self.daylst[5]]]
        bot.send_message(chat_id=update.effective_chat.id, text='''Select a Day from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    
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
                    bnk = ((4/3)*int(i[1]))-int(i[2])
                    if float(int(bnk)) != bnk:
                        bnk = int(bnk)+1
                else:
                    bnk = (3*int(i[2])-4*int(i[1]))
            text = text + str(i[0]) + ' : ' + str(i[1]) + ' : ' + str(i[2]) + ' : ' + str(per) + " : " + str(bnk)+"\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        self.menu(update,context)
        
    def getsubkb(self, update, context):
        '''
            Send subjects as keyboard
        '''
        sublst=self.db.getsubgrd(self.db.getusrgrd(update.effective_chat.id))
        text = [["Go to Menu"]]
        for i in sublst:
            text.append([i[0]])
        bot.send_message(chat_id=update.effective_chat.id, text='''Select a Subject from the\ngiven list''', reply_markup=telegram.ReplyKeyboardMarkup(text))
    
    def selsubatd(self, update, context):
        '''
            Asks user for the status of the given subject 
        '''
        self.subdic[update.effective_chat.id] = (update.message.text).upper()
        text = [["Present","Absent"],["Go to Menu"]]
        context.bot.send_message(chat_id=update.effective_chat.id, text='''Select the status of {}\n '''.format((update.message.text).upper()), reply_markup=telegram.ReplyKeyboardMarkup(text))
        context.bot.send_message(chat_id=update.effective_chat.id, text='''If you want to enter \nthe pnt and ttl class \nseperatly then enter\nThem in this pattern - \n *pp:tt* \n(ex: 05:10)-\n5 out of 10 classes attended''', parse_mode= 'Markdown')

    def setsubat(self, update, context):
        '''
            Sets attendance for the given subjects
        '''
        try:
            subnm = self.subdic[update.effective_chat.id]
        except:
            subnm = None
        if subnm:
            resp = update.message.text
            if resp == 'Present':
                self.db.setstdatt(update.effective_chat.id,subnm)
            elif resp == 'Present':
                self.db.setstdatt(update.effective_chat.id,subnm,0,1)
            else:
                att = resp.split(':')
                try:
                    if (int(att[0]) > int(att[1])):
                        i = 5/0
                    self.db.setstdatt(update.effective_chat.id,subnm,att[0],att[1])
                except:
                    bot.send_message(chat_id=update.effective_chat.id, text="Invalid Input")
        try:
            self.subdic.pop(update.effective_chat.id)
        except:
            pass
        self.getstdatd(update,context)
        
if __name__ == '__main__':
    db = teleDb()
    hi = stdchat(db)
