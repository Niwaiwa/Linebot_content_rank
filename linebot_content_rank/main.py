import traceback
from niconico import Niconico
from pixiv import Pixiv
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize, URIAction, MessageAction,
    FlexSendMessage, FlexComponent, FlexContainer, BubbleContainer, ImageComponent, BoxComponent, TextComponent, SeparatorComponent,
    ButtonComponent, CarouselContainer
)

from dotenv import load_dotenv
from os import environ


load_dotenv('.env')
ACCESS_TOKEN = environ.get('ACCESS_TOKEN', '')
CHANNEL_SECRET = environ.get('CHANNEL_SECRET', '')

app = Flask(__name__)

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    print(request.headers)
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        print(e)
        print(traceback.print_exception(e))

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text.lower() == "pixiv":
        p = Pixiv()
        rank_list = p.get_rank_data()
        bubble_item_list = []
        for rank_item in rank_list['contents']:
            bubble_container = get_pixiv_bubble_messages(rank_item)
            bubble_item_list.append(bubble_container)

        messages = []
        chunk_list = get_chunk_list(bubble_item_list)
        for item_list in chunk_list:
            message = FlexSendMessage(
                alt_text='hello',
                contents=CarouselContainer(
                    contents=item_list
                )
            )
            messages.append(message)

        line_bot_api.reply_message(
            event.reply_token,
            messages)
    elif text.lower() == "nico":
        p = Niconico()
        rank_list = p.get_rank_data()
        bubble_item_list = []
        for rank_item in rank_list['contents']:
            bubble_container = get_niconico_bubble_messages(rank_item)
            bubble_item_list.append(bubble_container)

        messages = []
        chunk_list = get_chunk_list(bubble_item_list)
        for item_list in chunk_list:
            message = FlexSendMessage(
                alt_text='hello',
                contents=CarouselContainer(
                    contents=item_list
                )
            )
            messages.append(message)

        # if len(messages) > 5:
        #     chunk_list = get_chunk_list(messages, 5)
        #     for messages in chunk_list:
        #         line_bot_api.reply_message(
        #             event.reply_token,
        #             messages)
        #         break
        # else:
        line_bot_api.reply_message(
            event.reply_token,
            messages)
    else:
        message = TextSendMessage(text=text)

        line_bot_api.reply_message(
            event.reply_token,
            message)


def delete_all_rich_menu():
    rich_menu_list = line_bot_api.get_rich_menu_list()
    print(rich_menu_list)
    for rich_menu in rich_menu_list:
        line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)
    rich_menu_list = line_bot_api.get_rich_menu_list()
    print(rich_menu_list)


def get_all_rich_menu():
    rich_menu_list = line_bot_api.get_rich_menu_list()
    print(rich_menu_list)
    

def create_rich_menu():
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=843),
        selected=False,
        name="Nice richmenu",
        chat_bar_text="Tap here",
        areas=[RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
            action=URIAction(label="Daily Rank", uri='https://line.me'))]
    )
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
    print(rich_menu_id)


def get_chunk_list(data=[], chunk_size=12):
    n = chunk_size
    return [data[i:i + n] for i in range(0, len(data), n)]


def get_pixiv_bubble_messages(rank_item):
    image_url = rank_item.get("url")
    rank = rank_item.get("rank")
    title = rank_item.get("title")
    user_name = rank_item.get("user_name")
    illust_url = rank_item.get("illust_url")
    user_url = rank_item.get("user_url")
    # height = rank_item.get("height")
    # width = rank_item.get("width")
    return BubbleContainer(
        direction='ltr',
        header=BoxComponent(
            contents=[
                TextComponent(text=f"{rank}位"),
            ],
            # background_color="transparent",
            layout="vertical",
        ),
        hero=ImageComponent(
            url=image_url,
            size='full',
            action=URIAction(uri=image_url, label='source'),
        ),
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text=f"{title}", size="xl", align="center", weight="bold"),
                TextComponent(text=f"{user_name}", align="center"),
                SeparatorComponent("md"),
                BoxComponent(
                    layout="vertical",
                    contents=[
                        ButtonComponent(
                            action=URIAction(uri=illust_url, label='visit illust'),
                            style="link",
                        ),
                        ButtonComponent(
                            action=URIAction(uri=user_url, label='visit user'),
                            style="link",
                        ),
                    ],
                    padding_top="10px",
                ),
            ],
            # align_items="center",
        ),
    )


def get_niconico_bubble_messages(rank_item):
    rank = rank_item.get("rank")
    title = rank_item.get("title")
    thumbnail_url = rank_item.get("thumbnail_url")
    video_url = rank_item.get("video_url")
    if not thumbnail_url:
        hero = None
    else:
        hero = ImageComponent(
            url=thumbnail_url,
            size='full',
            action=URIAction(uri=video_url, label='source'),
        )
    # print(rank_item)
    return BubbleContainer(
        direction='ltr',
        header=BoxComponent(
            contents=[
                TextComponent(text=f"{rank}位"),
            ],
            # background_color="transparent",
            layout="vertical",
        ),
        hero=hero,
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text=f"{title}", size="xl", align="center", weight="bold", wrap=True),
                SeparatorComponent("md"),
                BoxComponent(
                    layout="vertical",
                    contents=[
                        ButtonComponent(
                            action=URIAction(uri=video_url, label='visit video'),
                            style="link",
                        ),
                    ],
                    padding_top="10px",
                ),
            ],
            # align_items="center",
        ),
    )


if __name__ == "__main__":
    app.run('127.0.0.1', 8000, True)
    # create_rich_menu()
    # get_all_rich_menu()
    # delete_all_rich_menu()