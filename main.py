import requests
import json
import subprocess
import yt_dlp
import discord
import re 
import os
import shutil
import eyed3
from eyed3.id3.frames import ImageFrame
from requests import post
import base64
import urllib.request
import asyncio
import musicbrainzngs
from pydub import AudioSegment

#### Client Token Spotify API ####################
client_id = ' PASTE IN YOUR SPOTIFY CLIENT ID HERE'
client_secret = 'SPOTIFY CLIENT SECRET KEY HERE'
##################################################
# DISCORD BOT TOKEN AND CONFIGURATIONS ###########
TOKEN = " PASTE IN YOUR DISCORD BOT TOKEN HERE "

intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
channel_id1 = # PASTE IN YOUR DISCORD CHANNEL ID HERE AS A INT NOT STRING


##################################################





@client.event
async def on_ready():


    print('Bot is ready.')


@client.event
async def on_message(message):
    if message.author == client.user:


        return
    

    if message.channel.id == # PASTE IN YOUR DISCORD CHANNEL ID HERE AS A INT NOT STRING:
        global download_complete
        print(message.content)

        content = message.content
        


        

        await message.channel.send("processing request")
        await youtube_download(content)


async def send_message(channel_id, message):
    channel = client.get_channel(channel_id)
    await channel.send(message)

async def get_token():

    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
        }
    
    data = {"grant_type": "client_credentials"}
    result = post(url,headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


async def youtube_download(content):



    ###### YOUTUBE DATA V3 API KEY ###########
    api_key = # PASTE YOUR YOUTUBE DATA V3 API KEY HERE 
    keyword = content + " audio"


    url = f'https://www.googleapis.com/youtube/v3/search?part=id&maxResults=1&q={keyword}&key={api_key}'
    response = requests.get(url)


    ########### GET VIDEO ID VIA YOUTUBE API KEY#####
    json_data = json.loads(response.text)
    video_id = json_data['items'][0]['id']['videoId']

    ################################################



    #################### Downloads File ############
    video_url_download = "https://www.youtube.com/watch?v=" + video_id
    command = ['yt-dlp', '-f', 'bestaudio', '--extract-audio', '--audio-format','mp3','--output', '%(title)s.%(ext)s',video_url_download]
    subprocess.call(command)
    ################################################

    print("running regex function")
    await regex_file_rename()


async def regex_file_rename(): 
    global name_change
    global artist_name
    global song_name
    
    files = os.listdir()



    for x in files:

        if '.mp3' in x: #find if there is .mp3 in current directory

            file_name = x
            name_change = re.sub("[\(\[].*?[\)\]]", "",re.sub(r"\Soundtrack\b", "", file_name)) # formats the file name to be cleaner


            pattern = r"^(.*?)-(.*)$" # creates two variables based on regex patterns
            match = re.match(pattern, name_change.replace("｜", "-")) # applies changes 
            

            if match is None:

                musicbrainzngs.set_useragent("apps", "2.0","12341234")
                returned = musicbrainzngs.search_release_groups(query=file_name, limit=1)
                song_name = (returned["release-group-list"][0]["title"])
                artist_name = (returned["release-group-list"][0]["artist-credit"][0]["name"])
                conversion = artist_name + " - " + song_name
                conversion_mp3 = conversion + " .mp3"
                name_change = conversion
                os.rename(file_name, conversion_mp3)
                await Spotify_cover_art()
   
            else:
                        
                artist_name = match.group(1).strip()
                song_name = match.group(2).rstrip(".mp3").strip()
                await Spotify_cover_art()


            #####################################################
                       
        

async def Spotify_cover_art():
    print("i am spotify cover")
    print(name_change)
    token = await get_token()

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json ',
        'Authorization': 'Bearer ' + token
              }

    params = {
        'q': f'{artist_name}',
        'type': 'album',
        'market': 'ES',
        'limit': '1',
        'offset': '5',
             }

                        
    response = requests.get('https://api.spotify.com/v1/search', params=params, headers=headers)

    image_url = response.json()["albums"]["items"][0]["images"][1]["url"] # 300x300 image url link
                        
    ##### SPOTIFY DOWNLOAD IMAGE URL
    filename = "album_cover.jpg"

    urllib.request.urlretrieve(image_url, filename)


    print("Album cover downloaded successfully.")
    await metatag()




async def metatag():
    global file_location


    print("at metatag function")
    print(artist_name)
    files = os.listdir()

    for frmt in files:
        if ".mp3" in frmt:
            
            file_location = frmt
            

            audiofile = eyed3.load(file_location)

            audiofile.tag.artist = artist_name

            audiofile.tag.album_artist = artist_name

            audiofile.tag.title = song_name

            audiofile.tag.images.set(3, open("album_cover.jpg", 'rb').read(), 'image/jpeg')

            audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
            await ArtistFolderCreate()

#############################################################################



async def ArtistFolderCreate():
    print("inside artists folder method")
    if os.path.isdir("/srv/dev-disk-by-uuid-b629cc39-f88f-4413-b4e4-da0ad4d954f8/Music/" + str(artist_name) + "/" + "01"):  ##### CHANGE /SRV TO YOUR OPENMEDIAVAULT PATH
        shutil.move(file_location, '/srv/dev-disk-by-uuid-b629cc39-f88f-4413-b4e4-da0ad4d954f8/Music/' + artist_name + "/" + "01" + "/" + file_location) ##### CHANGE /SRV TO YOUR OPENMEDIAVAULT PATH
        print("folder exists and moved song")
        channel = client.get_channel(channel_id1)
        await channel.send("Download completed! :)")
        




    else: 
        make_artist_folder = os.mkdir("/srv/dev-disk-by-uuid-b629cc39-f88f-4413-b4e4-da0ad4d954f8/Music/" + str(artist_name))  ##### CHANGE /SRV TO YOUR OPENMEDIAVAULT PATH
        make_artist_albumid = os.mkdir("/srv/dev-disk-by-uuid-b629cc39-f88f-4413-b4e4-da0ad4d954f8/Music/" + str(artist_name) + "/" + "01") ##### CHANGE /SRV TO YOUR OPENMEDIAVAULT PATH
        shutil.move(file_location, '/srv/dev-disk-by-uuid-b629cc39-f88f-4413-b4e4-da0ad4d954f8/Music/' + artist_name + "/" + "01" + "/" + file_location) ##### CHANGE /SRV TO YOUR OPENMEDIAVAULT PATH
        print("folder created and song moved")
        channel = client.get_channel(channel_id1)
        await channel.send("Download completed! :)")




        








client.run(TOKEN)