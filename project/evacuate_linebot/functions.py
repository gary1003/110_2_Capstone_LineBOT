from audioop import add
from pathlib import Path
from django.conf import settings
from linebot.models import FlexSendMessage, TextSendMessage
from requests.utils import quote
import sqlite3
import pandas as pd

with open(Path(Path(__file__).parent.parent.parent, 'KEYS')) as f:
    GOOGLE_API_KEY = f.readlines()[4]

def get_shelters(latitude, longtitude)->FlexSendMessage:
    """
    Get the shelters near the user's location
    """
    # import googlemaps
    import googlemaps
    # create return message
    contents = {}
    contents['type'] = 'carousel'
    bubbles = []

    origin = (latitude, longtitude)

    df = sql_query(latitude, longtitude)

    # use sqlite to get 10 nearest shelters
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    for shelter in df.itertuples():
        name = shelter.name
        destination = (shelter.latitude, shelter.longtitude)
        result = gmaps.distance_matrix(origin, destination, mode='driving')
        distance = result['rows'][0]['elements'][0]['distance']['text']
        duration = result['rows'][0]['elements'][0]['duration']['text']
        capacity = shelter.capacity
        address = shelter.address
        telephone = '0903609931'
        name_in_charge = shelter.name_in_charge

        # if shelter is within 20 minutes, add to list
        # if int(duration.split(' ')[0]) <= 20:
        #     bubbles.append(create_bubble('shelter', name, capacity, distance, duration))
        bubbles.append(create_bubble('shelter', name, address, name_in_charge, telephone, capacity, distance, duration, origin, destination))
    if len(bubbles)!=0:
        # sort bubbles by distance
        bubbles.sort(key=lambda x: float(x['body']['contents'][2]['contents'][1]['text'].split(' ')[0]))
        contents['contents']=bubbles[:10]
        message = FlexSendMessage(alt_text='避難處所資訊',contents=contents)
    elif len(bubbles)==0:
        message = TextSendMessage(text='附近未搜尋到避難處所資訊相關資訊')
    return message

def sql_query(latitude, longtitude):
    con = sqlite3.connect(Path(Path(__file__).parent.parent, 'db.sqlite3'))
    con.enable_load_extension(True)
    con.load_extension(settings.SPATIALITE_LIBRARY_PATH)
    q = f"""SELECT k.pos as rank, b.ogc_fid, b.避難收容處所地址 as address, 
            b.避難收容處所名稱 as name, b.預計收容人數 as capacity, b.管理人電話 as telephone,
            b.管理人姓名 as name_in_charge, k.distance as raw_distance, 
            b.經度 as longtitude, b.緯度 as latitude
            FROM KNN k
            JOIN shelters as b ON (b.ogc_fid = k.fid)
            WHERE f_table_name = 'shelters' 
            AND ref_geometry = MakePoint({longtitude}, {latitude})
            AND max_items = 7"""
    df = pd.read_sql(q, con)
    con.close()
    return df

def create_bubble(type, name, address, name_in_charge, telephone, capacity, distance, duration, origin, destination):
    if type == 'shelter':
        base_url = 'https://www.google.com/maps/dir/?'
        api_request = f'api=1&origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&travelmode=driving'
        url = f'{base_url}{api_request}'
        image_url = f'https://maps.googleapis.com/maps/api/staticmap?center=&{destination[0]},{destination[1]}&size=600x390&maptype=roadmap&markers=color:red%7Clabel:O%7C{destination[0]},{destination[1]}&key={GOOGLE_API_KEY}'
        search_uri = f'https://www.google.com/search?q={quote(name.replace(" ", "+"))}'
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": image_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                "type": "uri",
                "uri": f"https://www.google.com/maps/search/?api=1&query={quote(name)}"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": name,
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "地址",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": address,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "容納人數",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": str(capacity),
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "距離",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": distance,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "預估時間",
                        "color": "#aaaaaa",
                        "size": "sm",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": duration,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 5
                    }
                    ]
                }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                    "type": "uri",
                    "label": "GoogleMap 導航",
                    "uri": url
                    },
                    "color": "#1E90FF"
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                    "type": "uri",
                    "label": "詳細資訊",
                    "uri": search_uri
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
                ],
                "flex": 0
            }
            }
    return bubble