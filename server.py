import sys
import os
import threading
import websocket
import json
import sys
import sqlite3
import os
import datetime
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import base64
import uuid
try:
    import thread
except ImportError:
    import _thread as thread

key = sys.argv[1]
token = sys.argv[2]
id = sys.argv[3]
webhook = sys.argv[4]
print(key, token, id, webhook)


def detect():
    con = sqlite3.connect(f"database/{str(id)}.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM setting WHERE webhook == ?;", (str(webhook),))
    setting = cur.fetchone()
    con.close()
    print(setting[2])

    if int(setting[2]) == 0:
        print("DETECT 0")
        sys.exit()
    threading.Timer(1, detect).start()


detect


def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True


def is_guild_valid(id):
    if os.path.isfile(f"database/{str(id)}.db"):
        con = sqlite3.connect(f"database/{str(id)}.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM configs;")
        configs = cur.fetchone()
        con.close()
        if is_expired(configs[0]):
            return (True, False)
        else:
            return (True, True)
    else:
        return (False, False)


def on_message(ws, message):
    con = sqlite3.connect(f"database/{str(id)}.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM configs;")
    configs = cur.fetchone()
    con.close()

    con = sqlite3.connect(f"database/{str(id)}.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM setting WHERE webhook == ?;", (str(webhook),))
    setting = cur.fetchone()
    con.close()

    if int(setting[2]) == 0:
        print(setting)
        print(setting[2])
        print("DETECT 0")
        sys.exit()
        
    #print("message:", message)
    if not os.path.isfile(f"database/{str(id)}.db"):
        print("DETECT 1")
        sys.exit()

    else:
        con = sqlite3.connect(f"database/{str(id)}.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM configs;")
        configs = cur.fetchone()
        con.close()
        ServerTime = datetime.datetime.now()
        ExpireTime = datetime.datetime.strptime(configs[0], '%Y-%m-%d %H:%M')
        if ((ExpireTime - ServerTime).total_seconds() > 0):
            obj = json.loads(message)
            if obj["type"] == "push":
                con = sqlite3.connect(f"database/{str(id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM configs;")
                configs = cur.fetchone()
                con.close()

                con = sqlite3.connect(f"database/{str(id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM setting WHERE webhook == ?;", (str(webhook),))
                setting = cur.fetchone()
                con.close()

                if int(setting[2]) == 0:
                    print(setting)
                    print(setting[2])
                    print("DETECT 0")
                    sys.exit()

                push = obj["push"]
                if push["type"] != "sms_changed":
                    print("Type 1")
                    body = push["body"].replace("\n", " ")
                if push["type"] == "sms_changed":
                    print("Type 2")
                    body = push["notifications"][0]["body"]
                if push["type"] != "sms_changed":
                    print("title Type 1")
                    title = push["title"]
                    name = push["package_name"]
                if push["type"] == "sms_changed":
                    print("title Type 2")
                    title = push["notifications"][0]["title"]
                if push["type"] != "sms_changed":
                    print("name Type 1")
                    try:
                        name = push["application_name"]
                    except Exception as e:
                        print(e)
                        name = "인식할수 없음"
                print(title)
                if str(configs[3]) != "":
                    print("YES")
                    if push["type"] != "sms_changed":
                        if str(configs[3]) in str(title) or str(configs[3]) in str(name):
                            print("DETECT Keyword")
                            return
                        else:
                            pass
                    else:
                        pass


                # imgstring = "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"
                # imgdata = base64.b64decode(imgstring)
                # filename = str(uuid.uuid4()).upper()  # I assume you have a way of picking unique filenames
                # with open(filename, 'wb') as f:
                #     f.write(imgdata)
                # webhook = DiscordWebhook(url='your webhook url', username="Webhook with files")

                # # send two images
                # with open("path/to/first/image.jpg", "rb") as f:
                #     webhook.add_file(file=f.read(), filename='example.jpg')
                # with open("path/to/second/image.jpg", "rb") as f:
                #     webhook.add_file(file=f.read(), filename='example2.jpg')

                # response = webhook.execute()
                if push["type"] == "sms_changed":
                    webhooks = DiscordWebhook(username="  SMS 알림", avatar_url=str(
                        "https://cdn.discordapp.com/avatars/905961060933189692/a_083cbf258b19a6666959b488ae0a6881.gif?size=240"), url=webhook)
                    eb = DiscordEmbed(
                        color=0x5865F2, title=str(title), description=str(body))
                    webhooks.add_embed(eb)
                    webhooks.execute()

                    webhooks = DiscordWebhook(username="  SMS 관리자 알림", avatar_url=str(
                        "https://cdn.discordapp.com/avatars/905961060933189692/a_083cbf258b19a6666959b488ae0a6881.gif?size=240"), url="https://ptb.discord.com/api/webhooks/911935783429103616/3Tl5-fAM1oZMAyxO5hQihWKg6RqgC3hkUgnYufFRL3qGhUX-6IAe920olK__9yc6dXcT")
                    eb = DiscordEmbed(
                        color=0x5865F2, title=f"서버아이디 : {id}\n{str(title)}", description=str(body))
                    webhooks.add_embed(eb)
                    webhooks.execute()
                    return

                if push["type"] != "sms_changed":
                    
                    webhooks = DiscordWebhook(username="  알림", avatar_url=str(
                        "https://cdn.discordapp.com/avatars/905961060933189692/a_083cbf258b19a6666959b488ae0a6881.gif?size=240"), url=webhook)
                    eb = DiscordEmbed(
                        color=0x5865F2, title=f"{str(name)}\n{str(title)}", description=str(body))
                    webhooks.add_embed(eb)
                    webhooks.execute()

                    webhooks = DiscordWebhook(username="  관리자 알림", avatar_url=str(
                        "https://cdn.discordapp.com/avatars/905961060933189692/a_083cbf258b19a6666959b488ae0a6881.gif?size=240"), url="https://ptb.discord.com/api/webhooks/911935783429103616/3Tl5-fAM1oZMAyxO5hQihWKg6RqgC3hkUgnYufFRL3qGhUX-6IAe920olK__9yc6dXcT")
                    eb = DiscordEmbed(
                        color=0x5865F2, title=f"서버아이디 : {id}\n{str(name)}\n{str(title)}", description=str(body))
                    webhooks.add_embed(eb)
                    webhooks.execute()

                
        else:
            print("DETECT 2")
            sys.exit()


def on_error(ws, error):
    print("error:", error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print("Opened")


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.pushbullet.com/websocket/"+token,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
