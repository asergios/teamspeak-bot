#!/usr/bin/python3
import ts3Beta
import time
import json
import urllib.request
from random import randint
import pafy
import vlc
import sqlite3

"""
Configs & Settings

    API_KEY     - API key from ClientQuery, you can find it on TeamSpeak Client (Tools>Options>Addons).
    HOST        - IP address (or DNS) of HOST that telnet will connect to. Use 127.0.0.1 if you are using ClientQuery.
    PORT        - PORT for telnet, default 25639 for ClientQuery.
    YT_API_KEY  - API key for YouTube, this is used for youtube search request. You can generate a key at https://console.developers.google.com
    YT_API_LINK - GET request for YouTube search API.
    YT_LINK     - YouTube link.
    CHANNEL     - channel you want the bot to connect to.

    """

API_KEY = "INSERT_API_KEY"
HOST = "127.0.0.1"
PORT = 25639
YT_API_KEY = "INSERT_YOUTUBE_API_KEY"
YT_API_LINK = "https://www.googleapis.com/youtube/v3/search?part=snippet&regionCode=PT&type=video&"
YT_LINK = "https://www.youtube.com/"
CHANNEL = "INSERT_CHANNEL_NAME"


"""
Global Variables

    whoami          - stores information about the bot client (id, nickname, ...).
    invoker_name    - stores nickname of last event invoker.
    invoker_id      - stores id of last event invoker.
    invoker_uid     - stores unique id of last event invoker
    current_link    - stores link of current video playing.
    current_name    - stores name of current video playing.
    vlc_player      - stores de VLC MediaPlayer object.
    target          - nickname of user for bot to target (spam "Shut Up" on public chat everytime he turns mic on).
    spam_timer      - timestamp for spam control.
    insults         - list of insults used to when the bot gets angry at annoying invokers.
    search          - stores the search results from last "search" call.
    help            - message

    """
whoami = {}
invoker_name = ""
invoker_id = ""
invoker_uid = ""
current_link = ""
current_name = ""
vlc_player = vlc.MediaPlayer()
target = ""
spam_timer = time.time()
insults = ["INSULT1",
           "INSULT2",
           "INSULT3",
           "INSULT4",
           "INSULT5"]
search = ["", "", "", "", ""]
help = ["[color=royalblue][b]Welcome to ZeBot! These are the commands available:",
        "[color=darkslateblue][b]Text me: [https://www.youtube.com/watch?v=...] to play a video from YouTube.",
        "[color=darkslateblue][b]Text me: [stop] to stop the video I am currently playing.",
        "[color=darkslateblue][b]Text me: [song] to get the name of the video that I am playing.",
        "[color=darkslateblue][b]Text me: [search 'SOMETHING_TO_SEARCH'] to search YouTube, I will return you the first five results.",
        "[color=darkslateblue][b]Text me: [pick NUMBER] to pick one of the search results.",
        "[color=darkslateblue][b]Text me: [playlist] to show your playlist.",
        "[color=darkslateblue][b]Text me: [addplaylist] to add the current video playing on your playlist.",
        "[color=darkslateblue][b]Text me: [delete NUMBER] to delete a video from your playlist",
        "[color=darkslateblue][b]Text me: [play NUMBER] to play a video from your playlist"]


# Sends a message to the current channel
def channel_msg(message):
    ts3conn.sendtextmessage(
        targetmode=2,
        target=channel_id,
        msg=message)


# Sends a private message to user of id {c_id}
def priv_msg(message):
    ts3conn.sendtextmessage(
        targetmode=1,
        target=invoker_id,
        msg=message)


# Anti-spam System. The actual time has to be superior to spam_timer
# Return True if bot is allowed to answer the call
def check_timer():
    global spam_timer
    if(time.time() > spam_timer):
        spam_timer = time.time() + 20
        return True
    else:
        priv_msg("[b]You going too fast![/b] Please wait "
                 + str(int(spam_timer-time.time()))
                 + " more seconds/s")
        return False


# Filter, in this case for Youtube Videos that contain "Bieber" on title, it also kicks the user from the server
def filt():
    if("Bieber" in current_name):
        stop()
        channel_msg("[b][color=red]Justin Bieber? Not on my server!!")
        ts3conn.clientkick(reasonid=5, reasonmsg="No Justin Bieber here pls.", clid=invoker_id)


# Stops the VLC MediaPlayer
def stop():
    global current_name
    global current_link
    try:
        vlc_player.stop()
        current_name = ""
        current_link = ""
        return True
    except:
        return False


def play(url):
    global current_link
    global current_name
    priv_msg("[b]Loading... [/b]")

    video = pafy.new(url)
    current_link = url
    current_name = video.title
    duration = video.duration

    if(len(video.m4astreams) != 1):
        audiostreams = video.m4astreams[1]
    else:
        audiostreams = video.m4astreams[0]

    try:
        ts3conn.clientupdate(CLIENT_NICKNAME="ZeBot ♫ " + current_name[:22])
    except:
        pass

    media = vlc_player.get_instance().media_new(audiostreams.url)
    vlc_player.set_media(media)
    vlc_player.play()
    channel_msg("[color=red][b]Playing " + "[url=" + url[:43] + "]" + current_name + "[/url] [color=blue][" + duration + "][/color][/color][b] requested by [/b]" + invoker_name + "[b] ¸¸.•*¨*•♫♪[/b]")
    filt()


# Adding current video to the invoker's playlist
def addToPlaylist():
    sql = sqlite3.connect("playlist.db")
    sql_cursor = sql.cursor()

    sql_command = """
        INSERT INTO playlists ( link, name, owner )
            VALUES ('%s', '%s', '%s') ;
    """

    sql_cursor.execute(sql_command % (current_link, current_name, invoker_uid))
    sql.commit()
    sql.close()
    priv_msg("[b]Added to your playlist!")


# Delete "deleted" from invoker's playlist
def deleteFromPlaylist(deleted):
    sql = sqlite3.connect("playlist.db")
    sql_cursor = sql.cursor()

    sql_command = """
        DELETE FROM playlists WHERE
            link = '%s' AND name = '%s'AND owner = '%s';
    """

    sql_cursor.execute(sql_command % (deleted[0], deleted[1], deleted[2]))
    sql.commit()
    sql.close()
    priv_msg("[b]Successfully deleted from your playlist!")


# Get whole playlist from invoker's
def getFromPlaylist():
    sql = sqlite3.connect("playlist.db")
    sql_cursor = sql.cursor()

    sql_command = """
        SELECT * FROM playlists WHERE owner = '%s';
    """

    sql_cursor.execute(sql_command % invoker_uid)
    result = sql_cursor.fetchall()

    sql.commit()
    sql.close()
    return result


def commands():
    try:
        # get the msg attr
        msg = event.parsed[0]['msg'].replace("[URL]", "").replace("[/URL]", "")
        msg = msg.split(" ", 1)
        key = msg[0]
        secondary = ""
        if(len(msg) > 1):
            secondary = msg[1]

        # Request by YouTube link
        if(YT_LINK in key):
            if(check_timer() and len(key) == 43):
                play(key)

        # Request to stop the song
        elif(key == "stop"):
            if(stop()):
                channel_msg("I'm sorry " + invoker_name + "...  ;_;")
            else:
                novoins = randint(0, 4)
                priv_msg("[color=brown][b]You shut up " + insults[novoins] + "!!")

        # Request song name
        elif(key == "song"):
            if(current_name != ""):
                priv_msg("[color=red][b]Playing " + "[url=" + current_link + "]" + current_name + "[/url][/color]")
            else:
                priv_msg("[color=red][b]I'm not playing anything at the moment... ")

        # Request to search
        elif(key == "search"):
            try:
                q = secondary.replace(" ", "+")
                url = YT_API_LINK + "q=" + q + "&key=" + YT_API_KEY
                h = urllib.request.urlopen(url)
                html = h.read()
                results = json.loads(html.decode('utf-8'))
                priv_msg("[color=red][b] Search Results for " + secondary + " :")
                for i in range(len(results['items'])):
                    priv_msg("[color=blue][b]" + str((i+1)) + " - " + results['items'][i]["snippet"]["title"])
                    search[i] = results['items'][i]['id']['videoId']
                priv_msg("[color=red][b] Type : pick [number] to play one song from the list.")
            except Exception as e:
                print(e)
                priv_msg("[b]No results....")

        # Add music playing to my playlist
        elif(key == "addplaylist"):
            if(current_name != ""):
                addToPlaylist()
            else:
                priv_msg("[color=red][b]I'm not playing anything that you can add to your playlist... sorry ;_;")

        # Check my playlist
        elif(key == "playlist"):
            playlist = getFromPlaylist()

            if(len(playlist) == 0):
                priv_msg("[color=red][b]You have no playlist!")
                return

            priv_msg("[b]" + invoker_name + "'s [color=red] Playlist: ")
            for i in range(len(playlist)):
                link = playlist[i][0]
                title = playlist[i][1]
                priv_msg("[b]" + str((i + 1)) + " - [URL=" + link + "]" + title + "[/URL]")

        # Play from playlist
        elif(key == "play"):
            try:
                pick = int(secondary) - 1
                playlist = getFromPlaylist()
                if(len(playlist) == 0):
                    priv_msg("[color=red][b]You have no playlist!")
                    return
                play(playlist[pick][0])
            except ValueError:
                priv_msg("[b]I expected a number.")
            except IndexError:
                priv_msg("[b]You have no such index on your playlist.")

        # Delete from playlist
        elif(key == "delete"):
            try:
                pick = int(secondary) - 1
                playlist = getFromPlaylist()
                if(len(playlist) == 0):
                    priv_msg("[color=red][b]You have no playlist!")
                    return
                deleteFromPlaylist(playlist[pick])
            except ValueError:
                priv_msg("[b]I expected a number.")

        # Pick one of the searched values
        elif(key == "pick"):
            try:
                pick = int(secondary) - 1
                url = "https://www.youtube.com/watch?v=" + search[pick]
                play(url)
            except ValueError:
                priv_msg("[b]I expected a number.")
            except IndexError:
                priv_msg("[b]Search results go from 1 to 5 results.")

        # Pick one of the searched values
        elif(key == "target"):
            global target
            target = secondary

        # Pick one of the searched values
        elif(key == "volume"):
            vlc_player.audio_set_volume(int(secondary))

        # Pick one of the searched values
        elif(key == "help"):
            for line in help:
                priv_msg(line)

        # If the message was not recognized
        else:
            priv_msg("Didn't recognize that... Please type help for more information")

    except Exception as e:
        print("Something went wrong:")
        print(e)


# Checking event details to decide what to do with it
def eventHandler():
    global invoker_name
    global invoker_id
    global invoker_uid
    if(eventIs('notifytextmessage') and event.parsed[0]['targetmode'] == "1"):
        invoker_name = event.parsed[0]['invokername']
        invoker_id = event.parsed[0]['invokerid']
        invoker_uid = event.parsed[0]['invokeruid']
        # if it was a message sent by the bot he just ignores it
        if(me == invoker_id):
            return
        try:
            ts3conn.clientmove(cid=channel_id, clid=invoker_id)
            priv_msg("You not on my channel =(")
        except Exception:
            commands()
    elif(eventIs('notifyclientmoved') and event.parsed[0]['ctid'] == channel_id):
        invoker_id = event.parsed[0]['clid']
        priv_msg("[b][color=blue]Welcome to my channel! Wish to play something? Send me an YouTube link! ")
    elif(eventIs('notifytalkstatuschange') and event.parsed[0]['status'] == "1"):
        for client in ts3conn.clientlist().parsed:
            if(client['clid'] == event.parsed[0]['clid']):
                if(client['client_nickname'] == target):
                    ts3conn.clientpoke(clid=event.parsed[0]['clid'], msg="Cala-te " + target + "!")
                    channel_msg("Cala-te " + target + "!")


def eventIs(eventName):
    return event.data_bytestr.decode().startswith(eventName)


with ts3Beta.query.TS3Connection(HOST, PORT) as ts3conn:
    ts3conn.auth(apikey=API_KEY)

    # Get own ID and channel ID
    whoami = ts3conn.whoami()[0]
    me = whoami['clid']
    channel_id = whoami['cid']

    ts3conn.clientupdate(client_is_channel_commander=1)

    # Notify Events the bot wants to answer
    ts3conn.clientnotifyregister(event="notifytextmessage")
    ts3conn.clientnotifyregister(event="notifytalkstatuschange")
    ts3conn.clientnotifyregister(event="notifyclientmoved")

    # Wait for event
    while(1):
        ts3conn.send_keepalive()
        try:
            event = ts3conn.wait_for_event(timeout=550)
        except ts3Beta.query.TS3TimeoutError:
            pass
        else:
            eventHandler()
