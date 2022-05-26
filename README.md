# LineBOT for Evacuate Information

## Create Line Provider

- go [here](https://developers.line.biz/zh-hant/) and follow the instruction
- Create a Messaging API Channel

## Push Message

- see `push.py`
- useage: `python push.py [message]`

## Use DJANGO

### install
- `pip install django`, `pip install line-bot-sdk`

### new project
- Create project with `django-admin startproject mylinebot`
- Create app with `cd mylinebot`,  `manage.py startapp evacuate_linebot`
- `md templates` and `md static`

### setting
- Add `LINE_CHANNEL_ACCESS_TOKEN = ` and `LINE_CHANNEL_SECRET = ` to `settings.py`
- Add `evacuate_linebot.apps.EvacuateLinebotConfig` into `INSTALLED_APPS`
- Add `Path(BASE_DIR, 'templates')` into `TEMPLATES.DIR`
- Add `Path(BASE_DIR, 'static')` into `STATICFILES_DIRS`
- Add `ALLOWED_HOSTS = ['*']` into `settings.py`

### coding the bot

- in `evacuate_linebot/views.py`

```python
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
 
 
@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text=event.message.text)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
```

- Create `evacuate_linebot/urls.py`

```python
from django.urls import path
import views
 
urlpatterns = [
    path('callback', views.callback)
]
```

- Add urls `path('evacuate_linebot/', include('evacuate_linebot.urls'))` to `urlpatterns` in `mylinebot/urls.py`
    
### Migration

- `python manage.py makemigrations`
- `python manage.py migrate`

### test and run

- First create a superuser `python manage.py createsuperuser`
- `python manage.py runserver`
- open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Deploy with ngrok

- `choco install ngrok`
- login with `ngrok config add-authtoken `
- `python manage.py runserver`
- get webhook url with `ngrok http 8000`
- paste the url into [line backend](https://manager.line.biz/account/@482cailh/setting/messaging-api)