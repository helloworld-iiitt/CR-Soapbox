from functools import wraps
from telegram import ParseMode,ChatAction
from telegram.utils.helpers import mention_html
from telegram.ext.dispatcher import run_async
import sys,json,time
import logging
import traceback
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler

## logger Debug data
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

## Passdown data (Constants,Variables)
END = ConversationHandler.END
STOP = -10

## Default constants
DEV_MENU_KEY, DEV_MSG_MENU_KEY, DEV_MSG_KEY, DEV_RMV_ACC_KEY= range(100,104)

#Json file access
datajson = json.loads(open('json/clgdetails.json').read()) #access json file
devjson = json.loads(open('json/devlst.json').read()) #access json file
serverjson = json.loads(open('json/serverdetails.json').read())
timetbljson = json.loads(open('json/timetable.json').read()) #access json file
clgdtlsjson = json.loads(open('json/clgdetails.json').read())#access json file
sublstjson = json.loads(open('json/subjectlst.json').read())#access json file 
# developers list
devs = devjson['devChat_id']
tchEmaillist = list (datajson['teacher'].keys())
## Code snippets
def jsonupd():
    global datajson 
    datajson = json.loads(open('json/clgdetails.json').read())
    global devjson 
    devjson = json.loads(open('json/devlst.json').read())
    global serverjson 
    serverjson = json.loads(open('json/serverdetails.json').read())
    global timetbljson
    timetbljson = json.loads(open('json/timetable.json').read() )
    global clgdtlsjson
    clgdtlsjson = json.loads(open('json/clgdetails.json').read())
    global sublstjson
    sublstjson = json.loads(open('json/subjectlst.json').read())
    global devs
    devs = devjson['devChat_id']
    global tchEmaillist
    tchEmaillist = list (datajson['teacher'].keys())

# Build Menu
def build_menu(buttons, n_cols=2,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

# Send Action 
def send_action(action=ChatAction.TYPING):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

# Error Handler
def error(update, context):

    if update.effective_message:
        text = "Hey. I'm sorry to inform you that an error happened while I tried to handle your message. " \
               "My developer(s) will be notified." \
               "Try restarting the bot. If the problem presists Contact developer about it with a screenshot "
        update.effective_message.reply_text( text = text)
    
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    
    payload = ""

    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'

    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'

    if update.poll:
        payload += f' with the poll id {update.poll.id}.'

    text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
           f"</code>"

    for dev_id in devs:
        context.bot.send_message(dev_id, text)
    raise

##Restricted decorator

## User authorised decorator
def userauthorized(userlst):
    """ User authorised decorator """
    def decorator(func):
        @wraps(func)
        def wrapped(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id not in userlst:
                print("Unauthorized access denied for {}.".format(user_id))
                update.message.reply_text(text="Unauthorized access denied for {}.".format(update.message.from_user.first_name))
                return
            return func(update, context, *args, **kwargs)
        return wrapped
    return decorator

@run_async
def FwdMsgTolst(update, context, usrlst, is_dev = False,is_teacher = False,is_CR = False):
    '''
        Forward the message to all users in the given list
    '''
    usrnm = ''
    if update.effective_chat.username:
        usrnm = '(@{})'.format(update.effective_chat.username)
    for i in usrlst:
        if is_dev:
            context.bot.send_message(chat_id = i,text = "A Message from Developer: 👇")
        elif is_teacher:
            context.bot.send_message(chat_id = i,text = "A Message from Professor {}: 👇".format((update.message.from_user.first_name) + usrnm))
        elif is_CR:
            context.bot.send_message(chat_id =i,text = "A Message from CR {}: 👇".format((update.message.from_user.first_name) + usrnm))
        else:
            context.bot.send_message(chat_id = i,text = "A Message from User {}: 👇".format((update.message.from_user.first_name) + usrnm + '(' + str(update.effective_chat.id) + ")"))
        update.message.forward(i)
        time.sleep(.2)   

@run_async
def SndMsgTolst(update,context, usrlst , msg):
    '''
        Send the message to all users in the given list
    '''
    for i in usrlst:
        context.bot.send_message(chat_id = i , text = msg)
        time.sleep(.2)    

@run_async
def KnowAbtDev(update,context):
    '''
        Send the details of the Developer(s) to user
    '''
    if len(devjson['devDetails']) == 1:
        update.message.reply_text(text="This is My Cool Creator")
    else:
        update.message.reply_text(text="These are My Cool Creators")
    for i in devjson['devDetails']:
        text = '<b>Name : {},\n</b><b>Email : </b>\n'.format(i['Name'])
        for j in i['Email']:
            text = text + '''          <i>{}</i>\n'''.format(j)
        text = text + '''<b>Profiles :</b>\n'''
        for j in i['Profiles']:
            text = text + '''          <i><a href="{}">{}</a></i>\n'''.format(i['Profiles'][j],j)
        update.message.reply_text(text = text,parse_mode = ParseMode.HTML)
        time.sleep(1)


    
print('CodeSnippets Updated Successfully')

## visit https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#send-action-while-handling-command-decorator
## for some of these snippets
