#!/usr/bin/python3
 
import ts3
import webbrowser
import psutil
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Data
USER = "REPLACE_ME"
PASS = "REPLACE_ME"
HOST = "127.0.0.1"
PORT = 10011
# Bot config
CHANNEL = "REPLACE_WITH_CHANNEL_NAME"
SEQ = "ze:https://www.youtube.com/"
SEQ_SIZE = 27
# Get the actual time for later anti-spam system
timeh = time.time()
# Run the browser
browser = webdriver.Firefox()



# send message on teamspeak channel chat
def sendmsg(message):
    ts3conn.sendtextmessage(
        targetmode=2,
        target=channel_id,
        msg=message)

def youtube_opener(sender, event):
    global timeh

    try:
        # get the msg attr
        msg = event.parsed[0]['msg']
        channel_id = ts3conn.channelfind(pattern=CHANNEL)[0]['cid']

        # if the initial part matches the sequence
        if(msg[0:SEQ_SIZE] == SEQ):

            # Anti-spam System. The actual time has to be superior to timeh
            if(time.time()>timeh):
                sendmsg("[b]Loading... [/b]")

                # Load the browser
                browser.get(msg[3:])
                name=browser.title
                sendmsg("[color=red][b]Playing "+"[url="+msg[3:46]+"]"+name[:-10]+"[/url][/color][b] requested by [/b]"+event.parsed[0]['invokername']+"[b] ¸¸.•*¨*•♫♪[/b]")

                # Anti-spam delay set
                timeh = time.time()+20 
            else:
                sendmsg("[b]You going too fast![/b] Please wait "+str(int(timeh-time.time()))+" more seconds/s")

        # to stop the video from playing (will load blank page)
        elif(msg[0:11] == "ze: stop"):
            sendmsg("I'm sorry "+event.parsed[0]['invokername']+"...  ;_;")
            browser.get("about:blank")
            
        # if message after "ze:" wasnt recognized
        elif(msg[0:3] == "ze:"):
            sendmsg("Didn't recognize that... [b]To Play:[/b] ze:https://www.youtube.com/<some_video>  [b]To Stop:[/b] ze: stop")

    except Exception as e:
        print("Some strange message was received.")
        print(e)

with ts3.query.TS3Connection(HOST) as ts3conn:
    ts3conn.login(client_login_name=USER,
                  client_login_password=PASS)
    # Set use mode of connection
    ts3conn.use(sid=1)
    # KeepAlive to prevent closing the connection due to the max idle time from ts server (600s).
    ts3conn.keepalive()
    # Get own ID and channel ID
    me = ts3conn.whoami()[0]['client_id']
    ts3conn.clientupdate(CLIENT_NICKNAME="Zé Bot")
    channel_id = ts3conn.channelfind(pattern=CHANNEL)[0]['cid']
    # Move the bot to the channel
    ts3conn.clientmove(cid=channel_id, clid=me)

    # Register notifs and handle in new thread
    ts3conn.servernotifyregister(event="textchannel", id_=channel_id)
    ts3conn.on_event.connect(youtube_opener)
    ts3conn.recv_in_thread()

    # To finish the bot press Enter
    input("> Hit enter to finish.\n")
