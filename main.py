import datetime
import random
import re
from pytz import timezone
import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import logging
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler, Filters, MessageHandler

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO)

# Stages
MENU = 1
QRDRYER = 0
QRWASHER = 0
COINDRYER = 0
COINWASHER = 0

QR_WASHER_JOB_INDEX, QR_DRYER_JOB_INDEX, COIN_DRYER_JOB_INDEX, COIN_WASHER_JOB_INDEX = range(
  4)

# Status
QR_DRYER = 'AVAILABLE'
QR_WASHER = 'AVAILABLE'
COIN_DRYER = 'AVAILABLE'
COIN_WASHER = 'AVAILABLE'

# Count for how many times someone has called out laundry done in groupchat
TIMES_CALLED_OUT = 0

# URL of GIFs to use as angry reaction
GIFS = [
  "https://j.gifs.com/W6Pp6n.gif",
  "https://64.media.tumblr.com/65e95a7bc5a6a0f9a8846279eb0701c9/d4080bdfd802cbaf-b7/s400x600/60fc5c80d5c3021b316e82ef256ae89bb6422f98.gif",
  "https://c.tenor.com/I22QVUPxEGkAAAAd/icebear-webarebears.gif",
  "https://i.imgur.com/Zkic2sk.gif",
  "https://media1.giphy.com/media/11tTNkNy1SdXGg/giphy.gif",
  "https://media0.giphy.com/media/CJxXHfRAYvtqU/giphy.gif",
  "https://media3.giphy.com/media/11VW2xPAb4OFPO/giphy.gif",
  "https://media2.giphy.com/media/OOezqqxPB8aJ2/giphy.gif",
  "https://media.giphy.com/media/l396QehilGkfZzsQw/giphy.gif",
  "https://media.giphy.com/media/CcmdEYnRGAtNe/giphy.gif",
]

# Last Used
QR_DRYER_LAST_USED = ''
QR_WASHER_LAST_USED = ''
COIN_DRYER_LAST_USED = ''
COIN_WASHER_LAST_USED = ''

# /Start Parameters
START_QR_WASHER = "qr_washer"
START_QR_DRYER = "qr_dryer"
START_COIN_WASHER = "coin_washer"
START_COIN_DRYER = "coin_dryer"
VALID_START_PARAMS = [
  START_QR_DRYER, START_QR_WASHER, START_COIN_DRYER, START_COIN_WASHER
]

# List of Jobs
JOB = [0, 0, 0, 0]

# Singapore timezone to convert the timings
LOCAL_TIMEZONE = timezone('Asia/Singapore')

# Initialise TelegramBot
# Actual laundry bot
Tbot = telegram.Bot("1643260816:AAFh7atOxVaQuTQzCzNj-dQi_0iRzcJb9HY")
# Test Laundry Bot
# Tbot = telegram.Bot("5480884899:AAH5QJV9TL4Ls9DxJzFZwCEvJcfqWxiAwpc")


def qr_washer_alarm(context: CallbackContext) -> None:
  """Send the alarm message."""
  job = context.job
  context.bot.send_message(
    job.context,
    text=
    'Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it'
  )
  global QR_WASHER
  QR_WASHER = 'AVAILABLE'


def qr_dryer_alarm(context: CallbackContext) -> None:
  """Send the alarm message."""
  job = context.job
  context.bot.send_message(
    job.context,
    text=
    'Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it'
  )
  global QR_DRYER
  QR_DRYER = 'AVAILABLE'


def coin_washer_alarm(context: CallbackContext) -> None:
  """Send the alarm message."""
  job = context.job
  context.bot.send_message(
    job.context,
    text=
    'Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it'
  )
  global COIN_WASHER
  COIN_WASHER = 'AVAILABLE'


def coin_dryer_alarm(context: CallbackContext) -> None:
  """Send the alarm message."""
  job = context.job
  context.bot.send_message(
    job.context,
    text=
    'Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it'
  )
  global COIN_DRYER
  COIN_DRYER = 'AVAILABLE'


def start(update: Update, context: CallbackContext) -> None:
  # Don't allow users to use /start command in group chats
  if update.message.chat.type != 'private':
    Tbot.send_message(
      chat_id=update.message.from_user.id,
      text=
      f"""Hi @{update.message.from_user.username},\n\nThanks for calling me in the groupchat. To prevent spamming in the group, please type /start to me privately in this chat instead!"""
    )
    return MENU

  keyboard = [[InlineKeyboardButton('Exit', callback_data='exit')]]
  if len(context.args) > 0:
    return start_with_args(update, context)

  reply_markup = InlineKeyboardMarkup(keyboard)
  update.message.reply_text(
    'Welcome to Dragon Laundry Bot!\U0001f600\U0001F606\U0001F923\n\nUse the following commands to use this bot:\n/select: Select the washer/dryer that you want to use\n/status: Check the status of Washers and Dryers\n\nThank you for using the bot and do drop me any feedback to make this bot more efficient! @Kaijudo',
    reply_markup=reply_markup)
  return MENU


def start_with_args(update: Update, context: CallbackContext) -> int:
  # Parse the argument and check if it are a valid laundry machine
  laundry_machine = context.args[0]
  # If argument is not valid, return to default start function
  if laundry_machine not in VALID_START_PARAMS:
    context.args = []
    return start(update, context)
  keyboard = [[
    InlineKeyboardButton('Yes', callback_data=f"yes_{laundry_machine}")
  ], [InlineKeyboardButton('No', callback_data=f"no_{laundry_machine}")]]
  printed_laundry_name = laundry_machine.replace("_", " ").title()
  reply_markup = InlineKeyboardMarkup(keyboard)
  update.message.reply_text(
    text=
    f"Welcome to Dragon Laundry Bot!\U0001f600\U0001F606\U0001F923\n\nThanks for scanning the QR Code in the laundry room!\n\nYou have scanned the {printed_laundry_name}'s QR Code. Would you like to start the timer? \U0001f600\U0001F606\U0001F923",
    reply_markup=reply_markup)
  return MENU


def status(update: Update, context: CallbackContext) -> None:
  global JOB
  global QR_WASHER_JOB_INDEX, QR_DRYER_JOB_INDEX, COIN_WASHER_JOB_INDEX, COIN_WASHER_JOB_INDEX
  global QR_DRYER_LAST_USED, QR_WASHER_LAST_USED, COIN_DRYER_LAST_USED, COIN_WASHER_LAST_USED

  QR_WASHER_TIMER = ''
  if QR_WASHER == 'UNAVAILABLE':
    qr_washer_time = datetime.datetime.now() - JOB[QR_WASHER_JOB_INDEX]
    qr_washer_min = round((1920 - qr_washer_time.total_seconds()) // 60)
    qr_washer_sec = round((1920 - qr_washer_time.total_seconds()) % 60)
    QR_WASHER_TIMER = f'{QR_WASHER} for {qr_washer_min}mins and {qr_washer_sec}s by @{QR_WASHER_LAST_USED}'
  if QR_WASHER == 'AVAILABLE':
    QR_WASHER_TIMER = f'{QR_WASHER}. Last used by @{QR_WASHER_LAST_USED}'

  QR_DRYER_TIMER = ''
  if QR_DRYER == 'UNAVAILABLE':
    qr_dryer_time = datetime.datetime.now() - JOB[QR_DRYER_JOB_INDEX]
    qr_dryer_min = round((2400 - qr_dryer_time.total_seconds()) // 60)
    qr_dryer_sec = round((2400 - qr_dryer_time.total_seconds()) % 60)
    QR_DRYER_TIMER = f'{QR_DRYER} for {qr_dryer_min}mins and {qr_dryer_sec}s by @{QR_DRYER_LAST_USED}'
  if QR_DRYER == 'AVAILABLE':
    QR_DRYER_TIMER = f'{QR_DRYER}. Last used by @{QR_DRYER_LAST_USED}'

  COIN_DRYER_TIMER = ''
  if COIN_DRYER == 'UNAVAILABLE':
    coin_dryer_time = datetime.datetime.now() - JOB[COIN_DRYER_JOB_INDEX]
    coin_dryer_min = round((2400 - coin_dryer_time.total_seconds()) // 60)
    coin_dryer_sec = round((2400 - coin_dryer_time.total_seconds()) % 60)
    COIN_DRYER_TIMER = f'{COIN_DRYER} for {coin_dryer_min}mins and {coin_dryer_sec}s by @{COIN_DRYER_LAST_USED}'
  if COIN_DRYER == 'AVAILABLE':
    COIN_DRYER_TIMER = f'{COIN_DRYER}. Last used by @{COIN_DRYER_LAST_USED}'

  COIN_WASHER_TIMER = ''
  if COIN_WASHER == 'UNAVAILABLE':
    coin_washer_time = datetime.datetime.now() - JOB[COIN_WASHER_JOB_INDEX]
    coin_washer_min = round((1920 - coin_washer_time.total_seconds()) // 60)
    coin_washer_sec = round((1920 - coin_washer_time.total_seconds()) % 60)
    COIN_WASHER_TIMER = f'{COIN_WASHER} for {coin_washer_min}mins and {coin_washer_sec}s by @{COIN_WASHER_LAST_USED}'
  if COIN_WASHER == 'AVAILABLE':
    COIN_WASHER_TIMER = f'{COIN_WASHER}. Last used by @{COIN_WASHER_LAST_USED}'

  reply_text = f'Status of Laundry Machines L8:\n\nQR Washer: {QR_WASHER_TIMER}\n\nQR Dryer: {QR_DRYER_TIMER}\n\nCoin Washer: {COIN_WASHER_TIMER}\n\nCoin Dryer: {COIN_DRYER_TIMER}'

  # Don't allow users to use /status command in group chats
  if update.message.chat.type != 'private':
    Tbot.send_message(
      chat_id=update.message.from_user.id,
      text=
      f"""Hi @{update.message.from_user.username} ,thanks for calling me in the groupchat. \n\nTo prevent spamming in the group, I have sent you a private message instead!\n\n{reply_text}"""
    )
    return MENU
  update.message.reply_text(reply_text)


def backtomenu(update: Update, context: CallbackContext) -> None:
  query = update.callback_query
  query.answer()
  keyboard = [[InlineKeyboardButton('Exit', callback_data='exits')]]

  reply_markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(
    'Welcome to Dragon Laundry Bot!\n\nUse the following commands to use this bot:\n/select: Select the washer/dryer that you want to use\n/status: Check the status of Washers and Dryers\n\nThank you for using the bot and do drop me any feedback to make this bot more efficient! @Kaijudo',
    reply_markup=reply_markup)


def select(update: Update, context: CallbackContext) -> None:
  # Don't allow users to use /select command in group chats
  if update.message.chat.type != 'private':
    return MENU
  keyboard = [[
    InlineKeyboardButton('QR Washer', callback_data='qr_washer'),
    InlineKeyboardButton('QR Dryer', callback_data='qr_dryer'),
  ],
              [
                InlineKeyboardButton('Coin Washer',
                                     callback_data='coin_washer'),
                InlineKeyboardButton('Coin Dryer', callback_data='coin_dryer')
              ], [InlineKeyboardButton('Exit', callback_data='exit')]]

  reply_markup = InlineKeyboardMarkup(keyboard)

  update.message.reply_text(
    '\U0001f600\U0001F606\U0001F923 Please choose a service: \U0001f600\U0001F606\U0001F923',
    reply_markup=reply_markup)
  return MENU


def cancel(update: Update, context: CallbackContext) -> int:
  """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
  query = update.callback_query
  query.answer()
  query.edit_message_text(
    text="Haiyaaa then you call me for what\n\nUse /start again to call me")
  return ConversationHandler.END


def double_confirm(update: Update, context: CallbackContext) -> int:
  """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
  query = update.callback_query
  query.answer()
  #query.edit_message_text(text="See you next time!")


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
  """Remove job with given name. Returns whether job was removed."""
  current_jobs = context.job_queue.get_jobs_by_name(name)
  if not current_jobs:
    return False
  for job in current_jobs:
    job.schedule_removal()
  return True


def cancel_job(update: Update, context: CallbackContext) -> None:
  """Remove the job if the user changed their mind."""
  chat_id = update.effective_message.chat_id
  job_removed = remove_job_if_exists(str(chat_id), context)
  text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
  update.effective_message.reply_text(text)


def double_confirm_qr_dryer_callback(update: Update,
                                     _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  keyboard = [[
    InlineKeyboardButton('Yes', callback_data='yes_qr_dryer'),
  ], [InlineKeyboardButton('No', callback_data='no_qr_dryer')]]
  markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(text="Timer for QR DRYER will begin?",
                          reply_markup=markup)
  return MENU


def double_confirm_qr_washer_callback(update: Update,
                                      _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  keyboard = [[
    InlineKeyboardButton('Yes', callback_data='yes_qr_washer'),
  ], [InlineKeyboardButton('No', callback_data='no_qr_washer')]]
  markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(text="Timer for QR WASHER will begin?",
                          reply_markup=markup)
  return MENU


def double_confirm_coin_dryer_callback(update: Update,
                                       _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  keyboard = [[
    InlineKeyboardButton('Yes', callback_data='yes_coin_dryer'),
  ], [InlineKeyboardButton('No', callback_data='no_coin_dryer')]]
  markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(text="Timer for COIN DRYER will begin?",
                          reply_markup=markup)
  return MENU


def double_confirm_coin_washer_callback(update: Update,
                                        _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  keyboard = [[
    InlineKeyboardButton('Yes', callback_data='yes_coin_washer'),
  ], [InlineKeyboardButton('No', callback_data='no_coin_washer')]]
  markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(text="Timer for COIN WASHER will begin?",
                          reply_markup=markup)
  return MENU


def set_timer_qr_dryer(update: Update, context: CallbackContext) -> None:
  """Add a job to the queue."""
  chat_id = update.effective_message.chat_id
  query = update.callback_query
  query.answer()

  washerdue = int(1920)
  dryerdue = int(2400)

  job_removed = remove_job_if_exists(str(chat_id), context)
  global QR_DRYER
  if QR_DRYER == 'UNAVAILABLE':
    text = "QR DRYER is currently in use. Please come back again later!"
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
  if QR_DRYER == 'AVAILABLE':
    QRDRYER = context.job_queue.run_once(qr_dryer_alarm,
                                         dryerdue,
                                         context=chat_id,
                                         name='qr_dryer')
    QRDRYER
    QR_DRYER = 'UNAVAILABLE'
    ##        QR_DRYER_TIME = context.args.index(context.args[-1])
    global QR_DRYER_JOB_INDEX
    global QR_DRYER_LAST_USED
    global JOB
    global LOCAL_TIMEZONE
    JOB[QR_DRYER_JOB_INDEX] = datetime.datetime.now()
    QR_DRYER_LAST_USED = update.effective_message.chat.username + \
        ' (started at ' + \
        datetime.datetime.now(LOCAL_TIMEZONE).strftime("%I:%M%p") + ")"
    text = "Timer Set for 40mins for QR DRYER. Please come back again!"
    # if job_removed:
    #    text = 'Status Update: QR DRYER is available'
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
  return MENU


def set_timer_qr_washer(update: Update, context: CallbackContext) -> None:
  """Add a job to the queue."""
  chat_id = update.effective_message.chat_id
  query = update.callback_query
  query.answer()

  washerdue = int(1920)
  dryerdue = int(2400)

  job_removed = remove_job_if_exists(str(chat_id), context)
  global QR_WASHER
  if QR_WASHER == 'UNAVAILABLE':
    text = "QR WASHER is currently in use. Please come back again later!"
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
  if QR_WASHER == 'AVAILABLE':
    QRWASHER = context.job_queue.run_once(qr_washer_alarm,
                                          washerdue,
                                          context=chat_id,
                                          name='qr_washer')
    QRWASHER
    global QR_WASHER_JOB_INDEX
    global JOB
    global QR_WASHER_LAST_USED
    global LOCAL_TIMEZONE
    JOB[QR_WASHER_JOB_INDEX] = datetime.datetime.now()
    QR_WASHER_LAST_USED = update.effective_message.chat.username + \
        ' (started at ' + \
        datetime.datetime.now(LOCAL_TIMEZONE).strftime("%I:%M%p") + ")"
    QR_WASHER = 'UNAVAILABLE'
    text = "Timer Set for 32mins for QR WASHER. Please come back again!"
    # if job_removed:
    #    text = 'Status Update: QR DRYER is available'
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
  return MENU


def set_timer_coin_dryer(update: Update, context: CallbackContext) -> None:
  """Add a job to the queue."""
  chat_id = update.effective_message.chat_id
  query = update.callback_query
  query.answer()

  washerdue = int(1920)
  dryerdue = int(2400)

  job_removed = remove_job_if_exists(str(chat_id), context)
  global COIN_DRYER
  if COIN_DRYER == 'UNAVAILABLE':
    text = "COIN DRYER is currently in use. Please come back again later!"
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
  if COIN_DRYER == 'AVAILABLE':
    COINDRYER = context.job_queue.run_once(coin_dryer_alarm,
                                           dryerdue,
                                           context=chat_id,
                                           name='coin_dryer')
    COINDRYER
    global COIN_DRYER_JOB_INDEX
    global JOB
    global COIN_DRYER_LAST_USED
    global LOCAL_TIMEZONE
    JOB[COIN_DRYER_JOB_INDEX] = datetime.datetime.now()
    COIN_DRYER_LAST_USED = update.effective_message.chat.username + \
        ' (started at ' + \
       datetime.datetime.now(LOCAL_TIMEZONE).strftime("%I:%M%p") + ")"
    COIN_DRYER = 'UNAVAILABLE'
    text = "Timer Set for 40mins for COIN DRYER. Please come back again!"
    # if job_removed:
    #    text = 'Status Update: QR DRYER is available'
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
  return MENU


def set_timer_coin_washer(update: Update, context: CallbackContext) -> None:
  """Add a job to the queue."""
  chat_id = update.effective_message.chat_id  # use .effective_message to receive a message or edited message. .message only receives message
  query = update.callback_query
  query.answer()

  washerdue = int(1920)
  dryerdue = int(2400)

  job_removed = remove_job_if_exists(str(chat_id), context)
  global COIN_WASHER
  if COIN_WASHER == 'UNAVAILABLE':
    text = "COIN WASHER is currently in use. Please come back again later!"
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
  if COIN_WASHER == 'AVAILABLE':
    COINWASHER = context.job_queue.run_once(coin_washer_alarm,
                                            washerdue,
                                            context=chat_id,
                                            name='coin_washer')
    COINWASHER
    global COIN_WASHER_JOB_INDEX
    global JOB
    global COIN_WASHER_LAST_USED
    global LOCAL_TIMEZONE
    JOB[COIN_WASHER_JOB_INDEX] = datetime.datetime.now()
    COIN_WASHER = 'UNAVAILABLE'
    COIN_WASHER_LAST_USED = update.effective_message.chat.username + \
        ' (started at ' + \
        datetime.datetime.now(LOCAL_TIMEZONE).strftime("%I:%M%p") + ")"
    text = "Timer Set for 32mins for COIN WASHER. Please come back again!"
    # if job_removed:
    #    text = 'Status Update: QR DRYER is available'
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
  return MENU


def handle_message(update: Update, context: CallbackContext) -> None:
  text = update.message.text
  chat_id = update.effective_message.chat_id

  # Don't allow users to spam the bot in private chat
  if update.message.chat.type == "private":
    return

  should_reply = False
  laundry_machine = ""
  laundry_last_used_by = ""
  laundry_machine_status = ""
  # We can't realistically handle every situation for laundry being called out,
  # but we can reasonably handle the most common ones. ie. "qr dryer done"
  if 'qr washer' in text.lower():
    should_reply = True
    laundry_machine = "QR WASHER"
    laundry_last_used_by = QR_WASHER_LAST_USED
    laundry_machine_status = QR_WASHER
  elif 'qr dryer' in text.lower():
    should_reply = True
    laundry_machine = "QR DRYER"
    laundry_last_used_by = QR_DRYER_LAST_USED
    laundry_machine_status = QR_DRYER
  elif 'coin washer' in text.lower():
    should_reply = True
    laundry_machine = "COIN WASHER"
    laundry_last_used_by = COIN_WASHER_LAST_USED
    laundry_machine_status = COIN_WASHER
  elif 'coin dryer' in text.lower():
    should_reply = True
    laundry_machine = "COIN DRYER"
    laundry_last_used_by = COIN_DRYER_LAST_USED
    laundry_machine_status = COIN_DRYER

  if not should_reply:
    return

  reply_message = f"Beep Boop, Did someone say {laundry_machine} is done?\n\nHere's my recorded status: \n{laundry_machine} is {laundry_machine_status}: Last used by @{laundry_last_used_by}"

  update.message.reply_text(reply_message)

  if laundry_machine_status == 'UNAVAILABLE':
    return

  # If the laundry machine is available, we treat it as someone being irresponsible, so we increment count by 1
  global TIMES_CALLED_OUT
  global Tbot
  TIMES_CALLED_OUT += 1
  if TIMES_CALLED_OUT == 5:
    # Randomly choose one of the GIFs to send
    gif = random.choice(GIFS)
    Tbot.send_animation(
      chat_id=chat_id,
      animation=gif,
      caption=
      "GRRRRR, This is the <b>5th time in a row</b> someone has indicated that the laundry machine is hogged/blocked from being used🤬🤬🤬!\n\nPlease use @dragon_laundry_bot to keep track of the laundry machine usage and be ON TIME for your laundry.\n\n/status: View the status of all laundry machines.\n\nI am resetting the counter.",
      parse_mode=telegram.ParseMode.HTML)
    TIMES_CALLED_OUT = 0
  return


def main() -> None:
  """Run bot."""
  # Create the Updater and pass it your bot's token.
  # Actual Laundry Bot
  updater = Updater("1643260816:AAFh7atOxVaQuTQzCzNj-dQi_0iRzcJb9HY")
  # Test Laundry Bot
  # updater = Updater("5480884899:AAH5QJV9TL4Ls9DxJzFZwCEvJcfqWxiAwpc")

  # Get the dispatcher to register handlers
  dispatcher = updater.dispatcher

  # Use the pattern parameter to pass CallbackQueries with specific
  # data pattern to the corresponding handlers.
  # ^ means "start of line/string"
  # $ means "end of line/string"
  # So ^ABC$ will only allow 'ABC'
  conv_handler = ConversationHandler(
    entry_points=[
      CommandHandler('start', start),
      CommandHandler("select", select),
      CommandHandler("status", status),
      MessageHandler(
        ~Filters.command & Filters.regex(re.compile(r"done", re.IGNORECASE)),
        handle_message)
    ],
    states={
      MENU: [
        CallbackQueryHandler(cancel, pattern='^' + 'exit' + '$'),
        CallbackQueryHandler(cancel, pattern='^' + 'exits' + '$'),

        # whhich callback_data does start get call
        CallbackQueryHandler(double_confirm_qr_dryer_callback,
                             pattern='^' + 'qr_dryer' + '$'),
        CallbackQueryHandler(double_confirm_qr_washer_callback,
                             pattern='^' + 'qr_washer' + '$'),
        CallbackQueryHandler(double_confirm_coin_dryer_callback,
                             pattern='^' + 'coin_dryer' + '$'),
        CallbackQueryHandler(double_confirm_coin_washer_callback,
                             pattern='^' + 'coin_washer' + '$'),
        CallbackQueryHandler(backtomenu, pattern='^' + 'no_qr_dryer' + '$'),
        CallbackQueryHandler(backtomenu, pattern='^' + 'no_qr_washer' + '$'),
        CallbackQueryHandler(backtomenu, pattern='^' + 'no_coin_dryer' + '$'),
        CallbackQueryHandler(backtomenu, pattern='^' + 'no_coin_washer' + '$'),
        CallbackQueryHandler(set_timer_qr_dryer,
                             pattern='^' + 'yes_qr_dryer' + '$'),
        CallbackQueryHandler(set_timer_qr_washer,
                             pattern='^' + 'yes_qr_washer' + '$'),
        CallbackQueryHandler(set_timer_coin_dryer,
                             pattern='^' + 'yes_coin_dryer' + '$'),
        CallbackQueryHandler(set_timer_coin_washer,
                             pattern='^' + 'yes_coin_washer' + '$'),
      ]
    },
    fallbacks=[
      CommandHandler('start', start),
      CommandHandler("select", select),
      CommandHandler("status", status),
      MessageHandler(
        ~Filters.command & Filters.regex(re.compile(r"done", re.IGNORECASE)),
        handle_message)
    ],
  )

  # Add ConversationHandler to dispatcher that will be used for handling updates
  dispatcher.add_handler(conv_handler)

  # Start the Bot
  updater.start_polling()

  # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
  # SIGABRT. This should be used most of the time, since start_polling() is
  # non-blocking and will stop the bot gracefully.
  updater.idle()


# except (IndexError, ValueError):
##        update.message.reply_text('Oh no, this is not one of the commands I recognise, use /start to check out the list')

if __name__ == '__main__':
  main()
