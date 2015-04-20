#!/usr/bin/python3
 
import ts3
import webbrowser
import psutil
import os
import time
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from random import randint

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
# Will make sense i promise
insults=["REPLACE_WITH_INSULT_1","REPLACE_WITH_INSULT_2","REPLACE_WITH_INSULT_3","REPLACE_WITH_INSULT_4","REPLACE_WITH_INSULT_5"]


# send message on teamspeak channel chat
def sendmsg(message):
    ts3conn.sendtextmessage(
        targetmode=2,
        target=channel_id,
        msg=message)

# send message in private to invoker
def priv_msg(message, c_id):
    ts3conn.sendtextmessage(
        targetmode=1,
        target=c_id,
        msg=message)

# just a little filter... be free to add up
def filt(browser_title, client):
    jb = "Bieber"
    if(jb in name):
        browser.get("about:blank")
        sendmsg("[b][color=red]Justin Bieber? Not on my server!!")
        ts3conn.clientkick(reasonid=5, reasonmsg="Nice try... :)", clid=client)
        return

def priv_def(sender, event):
    global timeh
    global insults
    try:
        # get the msg attr
        msg = event.parsed[0]['msg']
        channel_id = ts3conn.channelfind(pattern=CHANNEL)[0]['cid']

        # Cleaning up the message for easy read
        msg = msg.replace(" ","")
        msg = msg.replace("[URL]","")
        msg = msg.replace("[/URL]","")

        # if the initial part matches the sequence
        if(msg[0:SEQ_SIZE] == SEQ):

            # Anti-spam System. The actual time has to be superior to timeh
            if(time.time()>timeh):
                priv_msg("[b]Loading... [/b]",event.parsed[0]['invokerid'])

                # Load the browser
                browser.get(msg[3:])
                name=browser.title
                sendmsg("[color=red][b]Playing "+"[url="+msg[3:46]+"]"+name[:-10]+"[/url][/color][b] requested by [/b]"+event.parsed[0]['invokername']+"[b] ¸¸.•*¨*•♫♪[/b]")

                # Anti-spam delay set
                timeh = time.time()+20 
            else:
                priv_msg("[b]You going too fast![/b] Please wait "+str(int(timeh-time.time()))+" more seconds/s",event.parsed[0]['invokerid'])

        # to stop the video from playing (will load blank page)
        elif(msg[0:7] == "ze:stop"):
            if(browser.title!=""):
                sendmsg("I'm sorry "+event.parsed[0]['invokername']+"...  ;_;")
                browser.get("about:blank")
            # because nobody likes to be shut up'd when saying nothing
            else:
                novoins = randint(0,4)
                priv_msg("[color=brown][b]You shut up "+insults[novoins]+"!!", event.parsed[0]['invokerid'])
        
        # Request song name
        elif(msg[0:7] == "ze:song"):
            # because darude.
            if(msg[7:12] == "name?"):
                priv_msg("[color=red][b]Playing [url=https://www.youtube.com/watch?v=y6120QOlsfU]▶ Darude - Sandstorm[/url][/color]",event.parsed[0]['invokerid'])
            else:
                name=browser.title
                # if the name == "" it means he is on about:blank page / he is not playing any song
                if(name!=""):
                    priv_msg("[color=red][b]Playing "+"[url="+browser.current_url+"]"+name[:-10]+"[/url][/color]",event.parsed[0]['invokerid'])
                else:
                    priv_msg("[color=red][b]I'm not playing anything at the moment... ;-;",event.parsed[0]['invokerid'])
        
        # Add music playing to my playlist
        elif(msg[0:14] == "ze:addplaylist"):
            name=browser.title   
            # i forgot to check if the file exist here. will add later
            if(name!=""):
                # the file with the user playlist is saved with his unique id
                playlist = open(os.path.join("playlists", event.parsed[0]['invokeruid'].replace("/","")+".txt"),'a')
                playlist.write(browser.current_url+" "+name[:-10]+'\n')
                playlist.close()
                priv_msg("[b]Added to your playlist!", event.parsed[0]['invokerid'])
                        
            else:
                priv_msg("[color=red][b]I'm not playing anything that you can add to your playlist... sorry ;_;",event.parsed[0]['invokerid'])
            playlist.close()
        
        # Check my playlist / print it in private chat
        elif(msg[0:11] == "ze:playlist"):
            if(os.path.isfile(os.path.join("playlists", event.parsed[0]['invokeruid'].replace("/","")+".txt"))):
                plist = []
                playlist = open(os.path.join("playlists", event.parsed[0]['invokeruid'].replace("/","")+".txt"),'r')
                priv_msg("[b]"+event.parsed[0]['invokername']+"'s [color=red]Playlist:", event.parsed[0]['invokerid'])
                for line in playlist:
                    plist.append(line.split(' ', 1 ))
                for i in range(0, len(plist)):
                    priv_msg("[b]"+str((i+1))+" - [URL="+plist[i][0]+"]"+plist[i][1].rstrip('\n')+"[/URL]", event.parsed[0]['invokerid'])
                playlist.close()
            else:
                priv_msg("[color=red][b]You have no playlist!", event.parsed[0]['invokerid'])

        # Play a song from playlist giving the id
        elif(msg[0:7] == "ze:play"):
            # checking if file exists
            if(os.path.isfile(os.path.join("playlists", event.parsed[0]['invokeruid'].replace("/","")+".txt"))):
                # anti-spam
                if(time.time()>timeh):
                    # list set up
                    plist = []
                    playlist = open(os.path.join("playlists", event.parsed[0]['invokeruid'].replace("/","")+".txt"),'r')
                    for line in playlist:
                        plist.append(line.split(' ', 1 ))
                    # picking id of song
                    pick = int(msg[7:10])-1
                    # checking if id is valid
                    if(pick<len(plist) and pick>-1):
                        priv_msg("[b]Loading... [/b]",event.parsed[0]['invokerid'])
                        browser.get(plist[pick][0])
                        sendmsg("[color=red][b]Playing "+"[url="+plist[pick][0]+"]"+plist[pick][1].rstrip('\n')+"[/url][/color][b] requested by [/b]"+event.parsed[0]['invokername']+"[b] ¸¸.•*¨*•♫♪[/b]")
                        timeh = time.time()+20
                    else:
                        sendmsg("[color=red][b]Invalid playlist ID!")
                    playlist.close()
                else:
                    priv_msg("[b]You going too fast![/b] Please wait "+str(int(timeh-time.time()))+" more seconds/s",event.parsed[0]['invokerid'])
            else:
                priv_msg("[color=red][b]You have no playlist!",event.parsed[0]['invokerid'])

        # if message after "ze:" wasnt recognized
        elif(msg[0:3] == "ze:"):
            sendmsg("Didn't recognize that... [b]To Play:[/b] ze:https://www.youtube.com/<some_video>  [b]To Stop:[/b] ze: stop")

    except Exception as e:
        print("Some strange message was received.")
        print(e)

# here he was iniciated my a user and send him an "hi" message and is ready to receive commands
def pub_def(sender, event):
    msg = event.parsed[0]['msg']
    msg = msg.replace(" ","")
    msg = msg.replace("[URL]","")
    msg = msg.replace("[/URL]","")
    if(msg[0:5] == "ze:hi"):
        priv_msg("Hi, "+event.parsed[0]['invokername'],event.parsed[0]['invokerid'])
    elif(msg[0:3] == "ze:"):
            print(msg)
            sendmsg("Didn't recognize that... Check the channel description to read the guide")

# With the bot growing the spam on channel chat was growing too... so now everyone has to send commands on private chat to the bot...
# in order to iniciate it the user has to send "ze:hi" on channel chat.
# Checking if message was private or public:
def priv_or_pub(sender, event):
    if(event.parsed[0]['targetmode'] == '2'):
        pub_def(sender,event) 
    else:
        # here i improvised a bit... since the commands were thro private chat now, people were sending commands outside the channel... 
        # in order to stop that i made the following... the bot trys to move the user to his channel... if he gets a error it means the user is
        # already on channel and that way he can read the command. If not... he will move the user and send a sad face =(
        try:
            ts3conn.clientmove(cid=channel_id, clid=event.parsed[0]['invokerid'])
            priv_msg("You not on my channel =(", event.parsed[0]['invokerid'])
        except Exception:
            priv_def(sender,event)   

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
    ts3conn.servernotifyregister(event="textprivate", id_=channel_id)
    ts3conn.on_event.connect(priv_or_pub)
    ts3conn.recv_in_thread()

    # To finish the bot press Enter
    input("> Hit enter to finish.\n")
