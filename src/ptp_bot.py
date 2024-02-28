__fname = 'ptp_bot'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
cStrDivider_1 = '#----------------------------------------------------------------#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
# pip install python-telegram-bot
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackQueryHandler, CallbackContext
# from telegram import ChatAction
import time, threading
import random
from datetime import datetime
import json, time, os, traceback, sys
import webbrowser
import tweepy, requests, os # pip install tweepy
from openai import OpenAI # pip install openai
from _env import env

#------------------------------------------------------------#
#   GLOBALS                                                  #
#------------------------------------------------------------#
# Telegram Bot token obtained from BotFather
USE_GEN_IMG = False
USE_PROD = False
IMG_REQUEST_CNT = 0
IMG_REQUEST_SUCCESS_CNT = 0
TOKEN = 'nil_token'
CONSUMER_KEY = 'nil_key'
CONSUMER_SECRET = 'nil_key'
ACCESS_TOKEN = 'nil_key'
ACCESS_TOKEN_SECRET = 'nil_key'
PROMO_TWEET_TEXT = 'nil_text'
# LST_ADMINS = ['@housing37', '@AlbertoBundy', '@phatkow']
LST_ADMINS = ['@housing37', '@AlbertoBundy']
IDX_LAST_COOKIE = -1

OPENAI_KEY = 'nil_key'
USE_HD_GEN = False
RESP_RECEIVED = False

WHITELIST_TG_CHAT_IDS = [
    '-1002063595190', # PTP - bot testing
    '-1002101308549', # $PTP shillers
    ]
#------------------------------------------------------------#
#   FUNCTIONS                                                #
#------------------------------------------------------------#
def set_tg_token():
    global TOKEN
    TOKEN = env.TOKEN_prod if USE_PROD else env.TOKEN_dev

def init_openAI_client():
    global OPENAI_KEY
    OPENAI_KEY = env.OPENAI_KEY

def set_twitter_auth_keys():
    global CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    # @SolAudits
    CONSUMER_KEY = env.CONSUMER_KEY_0
    CONSUMER_SECRET = env.CONSUMER_SECRET_0
    ACCESS_TOKEN = env.ACCESS_TOKEN_0
    ACCESS_TOKEN_SECRET = env.ACCESS_TOKEN_SECRET_0
    if USE_PROD:
        # @BearSharesNFT
        CONSUMER_KEY = env.CONSUMER_KEY_1
        CONSUMER_SECRET = env.CONSUMER_SECRET_1
        ACCESS_TOKEN = env.ACCESS_TOKEN_1
        ACCESS_TOKEN_SECRET = env.ACCESS_TOKEN_SECRET_1

def set_twitter_promo_text():
    global PROMO_TWEET_TEXT
    PROMO_TWEET_TEXT = 'Test auto tweet w/ image\n\nFind this souce code @ t.me/SolAudits0\nOnly on #PulseChain'
    if USE_PROD:
        PROMO_TWEET_TEXT = 'New $BearShares NFT image created!\n\nGenerate your own @ t.me/BearShares\nOnly on #PulseChain'

async def test(update, context):
    funcname = 'test'
    print(f'\nENTER - {funcname}\n')
    await context.bot.send_message(chat_id=update.message.chat_id, text="test successful")

# Function to handle the /start command
async def start(update, context):
    funcname = 'start'
    print(f'\nENTER - {funcname}\n')
    # await context.bot.send_message(chat_id=update.message.chat_id, text="Hello! I'm your friendly Telegram bot.")
    user_id = update.message.from_user.id
    message = "Welcome to the Bot! Click the button below to start."

    # Create an inline keyboard with a "Start" button
    keyboard = [[InlineKeyboardButton("Start", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline keyboard to the user
    await update.message.reply_text(message, reply_markup=reply_markup)

# Function to handle all other messages
async def echo(update: Update, context):
    funcname = 'echo'
    print(f'\nENTER - {funcname}\n')
    print(f'\nEXIT - {funcname}\n')

async def bad_command(update: Update, context):
    funcname = 'bad_command'
    print(f'\nENTER - {funcname}\n')

    user = update.message.from_user
    uid = user.id
    str_handle = user.first_name
    str_uname = user.username
    inp = update.message.text
    str_conf = f'@{str_uname} (aka. {str_handle}) -> invalid command: /{inp}'
    await context.bot.send_message(chat_id=update.message.chat_id, text=str_conf)
    print(f'\nEXIT - {funcname}\n')

def validate_input(str_input):
    return len(str_input) >= 5

def validate_admin_user(str_uname):
    global LST_ADMINS
    return '@'+str_uname in LST_ADMINS

def get_img_from_url(img_url):
    funcname = 'get_img_from_url'
    print(cStrDivider_1, f'ENTER - {funcname}', sep='\n')
    img_file = 'image.jpg'
    success = False
    response = requests.get(img_url)
    if response.status_code == 200:
        with open(img_file, 'wb') as image_file:
            image_file.write(response.content)
        success = True
    else:
        print("Failed to download image.")
    print('', f'EXIT - {funcname} _ status: {success}', cStrDivider_1, sep='\n')
    return img_file, success # success / fail

def delete_img_file(img_file):
    funcname = 'delete_img_file'
    print(cStrDivider_1, f'ENTER - {funcname}', sep='\n')
    os.remove(img_file)
    print("Image file deleted.")
    print('', f'EXIT - {funcname}', cStrDivider_1, sep='\n')
    
def tweet_promo(str_tweet, img_url):
    funcname = 'tweet_promo'
    print(cStrDivider_1, f'ENTER - {funcname}', sep='\n')

    # Authenticate to Twitter
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    auth = tweepy.OAuth1UserHandler(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET,
    )

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # download image
    img_file, success = get_img_from_url(img_url)
    if not success:
        print("FAILED - Tweeted promo with image!")
        print('', f'EXIT - {funcname}', cStrDivider_1, sep='\n')
        return None, False

    # Upload image and tweet
    media = api.media_upload(img_file)
    response = client.create_tweet(text=str_tweet, media_ids=[media.media_id])
    print("Tweeted promo with image!")

    # clean up
    delete_img_file(img_file)

    print('', f'EXIT - {funcname}', cStrDivider_1, sep='\n')
    return response, True

async def button_click(update: Update, context: CallbackContext) -> None:
    funcname = 'button_click'
    print(cStrDivider_1, f'ENTER - {funcname} _ {get_time_now()}', sep='\n')
    # group_name = update.callback_query.message.chat.title if update.message.chat.type == 'supergroup' else None
    # if group_name:
    #     print("Group name:", group_name)
    # else:
    #     print("*NOTE* This message was not sent from a group.")
    str_uname = update.callback_query.from_user.username
    str_handle = update.callback_query.from_user.first_name
    print(f'from user: @{str_uname} (aka. {str_handle})')
    if not validate_admin_user(str_uname):
        str_resp = f'@housing37 or @WhiteRabbit0x0 tweet requested (from: @{str_uname}): '
        message_id = update.callback_query.message.message_id
        chat_id = update.effective_chat.id
        # post_link = f"t.me/BearShares/{chat_id}?message_id={message_id}"
        post_link = f"t.me/BearShares/{message_id}" # ex: https://t.me/BearShares/3284
        str_resp = str_resp + post_link
        
        await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=str_resp)
        print(str_resp)
        print('', f'EXIT - {funcname}', cStrDivider_1, sep='\n')
        return
    
    # original message data & specified 'InlineKeyboardButton' callback_data
    og_msg_data = update.callback_query.message.text
    callback_data = update.callback_query.data
    img_url = og_msg_data[og_msg_data.find('http')::]

    # Perform your desired actions here
    print(f'og_msg_data: {og_msg_data}')
    print(f'callback_data: {callback_data}') # callback_data = '@username (aka. handle)'
    print(f'img_url: {img_url}')
    
    # tweet promo (note: callback_data[1:] = remove '@' from user name )
    str_tweet = PROMO_TWEET_TEXT + f'\n\nauthor: t.me/{callback_data[1:]}' # should we use 't.me/username' ?
    response, success = tweet_promo(str_tweet, img_url) # callback_data = TG author
    tweet_data = response.data
    tweet_text = tweet_data['text']
    idx_start = tweet_text.rfind('http')
    url = tweet_text[idx_start::]
    # print(f'response: {response}')
    # print(f'tweet_data: {tweet_data}')
    print(f'tweet_text:\n{tweet_text}')
    # print(f'idx_start: {idx_start}')
    print(f'\nurl: {url}')

    str_resp = f'\ntweet: {url}\nauthor: {callback_data}\nplease like & rt'
    if not success:
        str_resp = f'@{str_uname} (aka. {str_handle}) -> Promo Tweet FAILED to send : /'
    print(f'\nstr_resp: {str_resp}')
    await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=str_resp)

    print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')
    
async def gen_ai_img_1(update: Update, context):
    funcname = 'gen_ai_img_1'
    print(cStrDivider_1, f'ENTER - {funcname} _ {get_time_now()}', sep='\n')
    group_name = update.message.chat.title if update.message.chat.type == 'supergroup' else None
    _chat_id = update.message.chat_id
    print("chat_id:", _chat_id)
    if group_name:
        print("Group name:", group_name)
    else:
        print("*NOTE* This message was not sent from a group.")
    user = update.message.from_user
    uid = user.id
    str_handle = user.first_name
    str_uname = user.username
    inp = update.message.text

    # check if TG group is allowed to use the bot
    if str(_chat_id) not in WHITELIST_TG_CHAT_IDS:
        print("*** WARNING ***: non-whitelist TG group trying to use the bot; sending deny message...")
        str_conf = f"@{str_uname} (aka. {str_handle}) -> you do not have permission to use this bot : /"
        print(str_conf)
        await context.bot.send_message(chat_id=update.message.chat_id, text=str_conf)    
        print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')
        return
    
    str_prompt = inp[inp.find(' ')+1::] # slicing out /<command>
    str_conf = f'@{str_uname} (aka. {str_handle}) -> please wait, generating image ...\n    "{str_prompt}"'
    print(str_conf)

    await context.bot.send_message(chat_id=update.message.chat_id, text=str_conf)

    # lst_imgs, err = gen_ai_image(str_prompt)
    lst_imgs, err = gen_ai_image_openAI(str_prompt)

    if err > 0:
        str_err = f"@{str_uname} (aka. {str_handle}) -> something went wrong!\n   change it up & try again : /"
        if err == 1:
            str_err = f"@{str_uname} (aka. {str_handle}) -> description TOO SHORT, need at least 5 chars"
        str_err = str_err + f'\n    "{str_prompt}"'
        await context.bot.send_message(chat_id=update.message.chat_id, text=str_err)
        print(str_err)
        print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')
        return

    print('SENDING IMAGE to TG ...')
    # pick one random image from lst_imgs
    r_idx = -1
    url = 'nil_url'
    while True:
        r_idx = random.randint(0, len(lst_imgs)-1)
        is_img = 'r.bing.com' not in lst_imgs[r_idx]
        no_end_dot = lst_imgs[r_idx][-1] != '.'
        # if 'r.bing.com' not in lst_imgs[r_idx]:
        if is_img and no_end_dot:
            url = lst_imgs[r_idx]
            break

    # Create an inline keyboard markup with a button
    inline_keyboard = [
        [InlineKeyboardButton("Request Tweet", callback_data=f'@{str_uname} (aka. {str_handle})')]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    try:
        await context.bot.send_message(
            chat_id=update.message.chat_id, 
            text=f'@{str_uname} (aka. {str_handle}) -> here is your image\n  "{str_prompt}" ...\n {url}',
            # reply_markup = ReplyKeyboardMarkup([['Your Button Text']])
            reply_markup = reply_markup
            )
    except Exception as e:
        # note_021724: exception added for TG: @enriquebambo (aka. 🍊 👾 𝐄η𝐑𝕚ⓀẸⓑᗩｍ𝕓ㄖ 👾🍊 {I DM First, I'm Impostor})
        #   sending response with TG button was causing a crash (but images were indeed successfully received from BING)
        print_except(e, debugLvl=1)
        print('Sending to TG w/o tweet button... ')
        await context.bot.send_message(
            chat_id=update.message.chat_id, 
            text=f'@{str_uname} (aka. {str_handle}) -> here is your image\n  "{str_prompt}" ...\n {url}')
    print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')

def gen_ai_image_openAI(str_prompt):
    global IMG_REQUEST_CNT, IMG_REQUEST_SUCCESS_CNT, USE_HD_GEN
    funcname = 'gen_ai_image_openAI'
    IMG_REQUEST_CNT += 1
    print(f'\nENTER - {funcname} _ IMG_REQUEST_CNT: {IMG_REQUEST_CNT}')
    print(f'str_prompt: {str_prompt}')

    lst_imgs = []
    err = 0

    if not validate_input(str_prompt):
        err = 1
        return lst_imgs, err

    try:
        lst_imgs = exe_request_openAI(str_prompt, USE_HD_GEN) # True = HD (False = standard)
        IMG_REQUEST_SUCCESS_CNT += 1

    except Exception as e:
        print_except(e, debugLvl=1)
        print(f'img request cnt: {IMG_REQUEST_CNT}')
        print(f'img request success ratio: {IMG_REQUEST_SUCCESS_CNT}/{IMG_REQUEST_CNT}')
        # print("Exception caught:", e)
        err = 2
        time.sleep(2) # force user to wait for next attempt
        return lst_imgs, err
        
    print(f'img request cnt: {IMG_REQUEST_CNT}')
    print(f'img request success ratio: {IMG_REQUEST_SUCCESS_CNT}/{IMG_REQUEST_CNT}')
    print('', f'EXIT - {funcname} _ IMG_REQUEST_CNT: {IMG_REQUEST_CNT}', sep='\n')
    return lst_imgs, err

def exe_request_openAI(descr, use_hd=False):
    global OPENAI_KEY, RESP_RECEIVED
    print(f'ENTER - test_gen_image_openAI')
    
    quality = 'hd' if use_hd else 'standard'
    print(f'Sending request... openAI (quality: {quality}) _ {get_time_now()}')
    print('waiting for results... openAI')

    try:
        # start 'print_wait_dots' waiting thread
        RESP_RECEIVED = False
        dot_thread = threading.Thread(target=print_wait_dots)
        dot_thread.start()

        # execute request to openAI
        client = OpenAI(api_key=OPENAI_KEY)
        response = client.images.generate(
            model="dall-e-3",
            prompt=descr,
            size="1024x1024",
            quality=quality,
            n=1,
        )

    except Exception as e:
        print_except(e, debugLvl=1)
        raise
    finally:
        # end/join print 'dot' thread for waiting
        RESP_RECEIVED = True
        dot_thread.join()
    
    print(f'\nresponse recieved _ {get_time_now()}')
    # print(response.data)
    revised_prompt = response.data[0].revised_prompt
    image_url = response.data[0].url
    print(f'revised_prompt...\n {revised_prompt}')
    print(f'image_url...\n {image_url}')

    print(f'\nEXIT - test_gen_image_openAI _ {get_time_now()}')
    return [image_url]

def main():
    # global TOKEN
    dp = Application.builder().token(TOKEN).build()
    # Create the Update and pass in the bot's token
    # update = Update(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    # dp = update.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("test", test))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("gen_image", gen_ai_img_1))
    dp.add_handler(CommandHandler("tweet_promo", tweet_promo))
    # Add the button click handler
    dp.add_handler(CallbackQueryHandler(button_click))

    # Register message handler for all other messages
    # dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo)) # ~ = negate (ie. AND NOT)
    dp.add_handler(MessageHandler(filters.Command, bad_command))
    # Start the Bot
    dp.run_polling()
    # Update.start_polling()

    # Run the bot until you press Ctrl-C
    # Update.idle()

#------------------------------------------------------------#
#   DEFAULT SUPPORT                                          #
#------------------------------------------------------------#
READ_ME = f'''
    *DESCRIPTION*
        choose blockchain
        get latest tx pool
            OR
        search for 'from' address 
         and loop get tx pool

    *NOTE* INPUT PARAMS...
        nil
        
    *EXAMPLE EXECUTION*
        $ python3 {__filename} -<nil> <nil>
        $ python3 {__filename}
'''

#ref: https://stackoverflow.com/a/1278740/2298002
def print_except(e, debugLvl=0):
    #print(type(e), e.args, e)
    if debugLvl >= 0:
        print('', cStrDivider, f' Exception Caught _ e: {e}', cStrDivider, sep='\n')
    if debugLvl >= 1:
        print('', cStrDivider, f' Exception Caught _ type(e): {type(e)}', cStrDivider, sep='\n')
    if debugLvl >= 2:
        print('', cStrDivider, f' Exception Caught _ e.args: {e.args}', cStrDivider, sep='\n')
    if debugLvl >= 3:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        strTrace = traceback.format_exc()
        print('', cStrDivider, f' type: {exc_type}', f' file: {fname}', f' line_no: {exc_tb.tb_lineno}', f' traceback: {strTrace}', cStrDivider, sep='\n')

def print_wait_dots():
    global RESP_RECEIVED
    while not RESP_RECEIVED:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)  # Adjust sleep duration as needed

def wait_sleep(wait_sec : int, b_print=True, bp_one_line=True): # sleep 'wait_sec'
    print(f'waiting... {wait_sec} sec')
    for s in range(wait_sec, 0, -1):
        if b_print and bp_one_line: print(wait_sec-s+1, end=' ', flush=True)
        if b_print and not bp_one_line: print('wait ', s, sep='', end='\n')
        time.sleep(1)
    if bp_one_line and b_print: print() # line break if needed
    print(f'waiting... {wait_sec} sec _ DONE')

def get_time_now(dt=True):
    if dt: return '['+datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[0:-4]+']'
    return '['+datetime.now().strftime("%H:%M:%S.%f")[0:-4]+']'

def read_cli_args():
    print(f'\nread_cli_args...\n # of args: {len(sys.argv)}\n argv lst: {str(sys.argv)}')
    for idx, val in enumerate(sys.argv): print(f' argv[{idx}]: {val}')
    print('read_cli_args _ DONE\n')
    return sys.argv, len(sys.argv)

if __name__ == "__main__":
    ## start ##
    RUN_TIME_START = get_time_now()
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\n'+READ_ME)
    lst_argv_OG, argv_cnt = read_cli_args()
    
    ## exe ##
    try:
        # select to use prod bot or dev bot
        inp = input('Select token type to use:\n  0 = prod (@nil)\n  1 = dev (@ptp_test_bot)\n  > ')
        USE_PROD = True if inp == '0' else False
        print(f'  input = {inp} _ USE_PROD = {USE_PROD}')
        
        ans = input('\nUse HD image generating? [y/n]:\n  > ')
        USE_HD_GEN = True if ans == 'y' or ans == '1' else False
        print(f'  input = {ans} _ USE_HD_GEN = {USE_HD_GEN}')
        
        set_tg_token()
        init_openAI_client()
        set_twitter_auth_keys()
        set_twitter_promo_text()
        print(f'\nTelegram TOKEN: {TOKEN}')
        print(f'OpenAI OPENAI_KEY: {OPENAI_KEY}')
        print(f'Twitter CONSUMER_KEY: {CONSUMER_KEY}')
        print(f'Twitter PROMO_TWEET_TEXT:\n{PROMO_TWEET_TEXT}\n') 
        main()
    except Exception as e:
        print_except(e, debugLvl=0)
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')