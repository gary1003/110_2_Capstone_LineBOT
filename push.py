from linebot import LineBotApi
from linebot.models import TextSendMessage
import sys

with open('KEYS') as f:
    LINE_CHANNEL_SECRET = f.readline().strip()
    LINE_CHANNEL_ACCESS_TOKEN = f.readline().strip()
    LINE_ID = f.readline().strip()
    LINE_ID = f.readline().strip()

def push(message=None):
    if message is None:
        message = '大漢溪上游石門水庫有潰壩風險，下游三峽地區為高風險區域，請盡速撤離\n\n傳送位置訊息獲取建議避難地點'
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    line_bot_api.push_message(LINE_ID, TextSendMessage(text=message))

if __name__ == '__main__':
    try:
        message = sys.argv[1]
    except IndexError:
        message = None
    push(message)