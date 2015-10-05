#!/usr/bin/python3
 
import ts3
import psutil
import os
import time
import urllib.request
from bs4 import BeautifulSoup
from random import randint
import subprocess
import pafy




# Server config
USER = "REPLACE_WITH_USER"
PASS = "REPLACE_WITH_PASS"
HOST = "127.0.0.1"
PORT = 10011
# Bot config
CHANNEL = "REPLACE_WITH_CHANNEL_NAME"
SEQ = "https://www.youtube.com/" # Valid sequence for requesting
# Get the actual time for later anti-spam system
timeh = time.time()
insults = ["REPLACE_WITH_INSULT_1",
           "REPLACE_WITH_INSULT_2",
           "REPLACE_WITH_INSULT_3",
           "REPLACE_WITH_INSULT_4",
           "REPLACE_WITH_INSULT_5"]


# send message on teamspeak channel chat
def sendmsg(message):
    ts3conn.sendtextmessage(
        targetmode=2,
        target=channel_id,
        msg=message)

# send private message 
def priv_msg(message, c_id):
    ts3conn.sendtextmessage(
        targetmode=1,
        target=c_id,
        msg=message)

# just a little filter... feel free to add up
def filt(client):
    global process
    global name
    jb = "Bieber"
    if(jb in name):
        process.kill()
        process = 0
        name = ""
        sendmsg("[b][color=red]Justin Bieber? Not on my server!!")
        ts3conn.clientkick(reasonid=5, reasonmsg="No Justin Bieber here pls.", clid=client)
        return

def play(client_id, client_name, url):
    global process
    global link
    global name
    link = url
    priv_msg("[b]Loading... [/b]",client_id)
    video = pafy.new(url)
    name= video.title
    duration = video.duration
    if(len(video.m4astreams)!=1):
        audiostreams = video.m4astreams[1]
    else:
        audiostreams = video.m4astreams[0]
    try:
        process.kill()
    except:
        pass  
    process = subprocess.Popen(["cvlc",audiostreams.url])
    sendmsg("[color=red][b]Playing "+"[url="+url[:43]+"]"+name+"[/url] [color=blue]["+duration+"][/color][/color][b] requested by [/b]"+client_name+"[b] ¸¸.•*¨*•♫♪[/b]")
    filt(client_id)

def priv_def(sender, event, client_id, client_name):
    global timeh
    global process
    global link
    global name
    client_playlist = event.parsed[0]['invokeruid'].replace("/","") + ".txt"
    try:
        # get the msg attr
        msg = event.parsed[0]['msg']
        channel_id = ts3conn.channelfind(pattern=CHANNEL)[0]['cid']
        # if the initial part matches the sequence
        search_msg = msg
        msg = msg.replace(" ","")
        msg = msg.replace("[URL]","")
        msg = msg.replace("[/URL]","")

        if(msg[0:24] == SEQ):
            # Anti-spam System. The actual time has to be superior to timeh
            if(time.time() > timeh):
                play(client_id, client_name, msg)
                # Anti-spam delay set
                timeh = time.time() + 20 
            else:
                priv_msg("[b]You going too fast![/b] Please wait "
                         + str(int(timeh-time.time()))
                         + " more seconds/s",client_id)

        # to stop the music
        elif(msg[0:4] == "stop"):
            try:
                process.kill()
                process = 0
                name = ""
                sendmsg("I'm sorry " + client_name+"...  ;_;")
            except:
                novoins = randint(0,4)
                priv_msg("[color=brown][b]You shut up " + insults[novoins]+"!!", client_id)
        
        # Request song name
        elif(msg[0:4] == "song"):
            if(msg[4:9] == "name?"):
                priv_msg("[color=red][b]Playing [url=https://www.youtube.com/watch?v=y6120QOlsfU]▶ Darude - Sandstorm[/url][/color]",client_id)
            else:
                if(name!=""):
                    priv_msg("[color=red][b]Playing "+"[url="+link+"]"+name+"[/url][/color]", client_id)
                else:
                    priv_msg("[color=red][b]I'm not playing anything at the moment... ;-;",client_id)
            
        # Add music playing to my playlist
        elif(msg[0:11] == "addplaylist"):   
            if(name!=""):
                playlist = open(os.path.join("playlists", client_playlist),'a')
                playlist.write(link)
                playlist.close()
                priv_msg("[b]Added to your playlist!", client_id)
                        
            else:
                priv_msg("[color=red][b]I'm not playing anything that you can add to your playlist... sorry ;_;",client_id)
            playlist.close()

        # Check my playlist
        elif(msg[0:8] == "playlist"):
            if(os.path.isfile(os.path.join("playlists", client_playlist))):
                plist = []
                playlist = open(os.path.join("playlists", client_playlist),'r')
                priv_msg("[b]"+client_name+"'s [color=red]Playlist:", client_id)
                for line in playlist:
                    plist.append(line)
                for i in range(0, len(plist)):
                    video = pafy.new(plist[i])
                    title= video.title
                    priv_msg("[b]"+str((i+1))+" - [URL="+plist[i].rstrip('\n')+"]"+title+"[/URL]", client_id)
                playlist.close()
            else:
                priv_msg("[color=red][b]You have no playlist!", client_ids)
   
        # Play from playlist
        elif(msg[0:4] == "play"):
            if(os.path.isfile(os.path.join("playlists", client_playlist))):
                if(time.time()>timeh):
                    plist = []
                    playlist = open(os.path.join("playlists", client_playlist),'r')
                    for line in playlist:
                        plist.append(line.split(' ', 1 ))
                    pick = int(msg[4:7])-1
                    if(pick<len(plist) and pick>-1):
                        play(client_id, client_name, plist[pick])
                        timeh = time.time()+20
                    else:
                        sendmsg("[color=red][b]Invalid playlist ID!")
                    playlist.close()
                else:
                    priv_msg("[b]You going too fast![/b] Please wait "+str(int(timeh-time.time()))+" more seconds/s",client_id)
            else:
                priv_msg("[color=red][b]You have no playlist!",client_id)
    
        # Search
        elif(msg[0:6] == "search"):
            try:
                msg = search_msg.replace("search","")
                key = msg.replace(" ","+")
                url = "https://www.youtube.com/results?search_query="+key
                h = urllib.request.urlopen(url)
                html = h.read()
                soup = BeautifulSoup(html)
                url = "https://www.youtube.com"+soup.find_all('a')[41].get('href')
                play(client_id, client_name, url)
            except Exception:
                priv_msg("[b]No results....",client_id)
            
        # if message after "ze:" wasnt recognized
        else:
            priv_msg("Didn't recognize that... Check the channel description to read the guide" ,client_id)

    except Exception as e:
        print("Some strange message was received.")
        print(e)


def pub_def(sender, event, client_id, client_name):
    msg = event.parsed[0]['msg']
    msg = msg.replace(" ","")	
    if(msg[0:5] == "ze:hi"):
        priv_msg("Hi, "+client_name, client_id )
    elif(msg[0:3] == "ze:"):
            sendmsg("Didn't recognize that... ze:hi to start")

# Check if message was private or public
def priv_or_pub(sender, event):
    me = ts3conn.whoami()[0]['client_id']
    client_id = event.parsed[0]['invokerid']
    # if it was a message sent by the bot he just ignores it
    if(me == client_id):
        return
    client_name = event.parsed[0]['invokername']
    if(event.parsed[0]['targetmode'] == '2'):
        pub_def(sender,event, client_id, client_name) 
    else:
        try:
            ts3conn.clientmove(cid=channel_id, clid=client_id)
            priv_msg("You not on my channel =(", client_id )
        except Exception:
            priv_def(sender,event, client_id, client_name)   

with ts3.query.TS3Connection(HOST) as ts3conn:
    ts3conn.login(client_login_name=USER,
                  client_login_password=PASS)
    # Set use mode of connection
    ts3conn.use(sid=1)
    # KeepAlive to prevent closing the connection due to the max idle time from ts server (600s).
    ts3conn.keepalive()
    # Get own ID and channel ID
    me = ts3conn.whoami()[0]['client_id']
    ts3conn.clientupdate(CLIENT_NICKNAME="Music Bot")
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
