from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.geos import Point

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

from .functions import get_shelters
from .models import MessageDetail, Location

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            profie = line_bot_api.get_profile(event.source.user_id)
            name = profie.display_name
            if event.message.type == 'location':
                address = event.message.address
                latitde = event.message.latitude
                longitude = event.message.longitude
                message = []
                message.append(TextSendMessage(text=f'{address}\n緯度：{latitde}\n經度：{longitude}'))
                message.append(get_shelters(latitde, longitude))
                line_bot_api.reply_message(event.reply_token,message)

                l = Location(
                    message_id=event.message.id,
                    user_id=event.source.user_id,
                    user_name=name,
                    message_latitude=latitde,
                    message_longitude=longitude,
                    message_address=address,
                    geometry=Point(longitude,latitde)
                )
                print(l)
                l.save()

            elif event.message.type == 'text':

                mtext=event.message.text
                message=[]
                message.append(TextSendMessage(text=mtext))
                line_bot_api.reply_message(event.reply_token,message)

                m = MessageDetail(
                    message_id=event.message.id,
                    user_id=event.source.user_id,
                    user_name=name,
                    message_text=mtext
                )
                print(m)
                m.save()

            elif event.message.type == 'sticker':
                message = []
                message.append(TextSendMessage(text=str(event.message.keywords)))
                line_bot_api.reply_message(event.reply_token, message)
                text = str(event.message.keywords)
                m = MessageDetail(
                    message_id=event.message.id,
                    user_id=event.source.user_id,
                    user_name=name,
                    message_text=f'sticker:{text}',
                    sticker_package_id=event.message.package_id,
                    sticker_id=event.message.sticker_id
                )
                print(m)
                m.save()

            

        return HttpResponse()

    else:
        return HttpResponseBadRequest()
