import os, re, spotipy, lyricsgenius, tweepy
from random import choice
from time import sleep

##############################
#### Spotify API

tweet_frequency_mins = os.getenv("TWEET_FREQUENCY_MINS")

os.environ["SPOTIPY_CLIENT_ID"] = "b341c59fe4b7404d80f3a9b104c63822"
os.environ["SPOTIPY_CLIENT_SECRET"] = "dc4c2c461d824042b199ae430b2ef8cd"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8888/callback/"

username = "bekoo757"

scope = 'user-read-currently-playing'

token = spotipy.util.prompt_for_user_token( username, scope)

last_tweeted = ""

while True: # Iterates every 2 minutes checks for a song

  sp = spotipy.Spotify(auth=token)
  current_song = sp.currently_playing()

  if current_song == None:
    print("\nNot listening anything.\n")
    sleep(60 * tweet_frequency_mins)
    continue

  artist_name = current_song['item']['artists'][0]['name']

  song_name = current_song['item']['name']

  if song_name == last_tweeted:
    print("\nSong already tweeted.\n")
    sleep(60 * tweet_frequency_mins)
    continue
    
  print("\n", "   Artist name:", artist_name, end="\n\n")
  print(     "    Song name:", song_name, end="\n\n")

  ##############################
  #### Genius API

  GENIUS_CLIENT_ID = "MM9djKni9Mquv0klm0peaYuGvH3r2wT13KxaF1rSX3N9hNA-6DYWU90PhqkBaLgh"
  genius = lyricsgenius.Genius(GENIUS_CLIENT_ID)

  song = genius.search_song(song_name, artist_name)

  try:
    lyrics = song.lyrics
  except ( AttributeError):
    print("\nCouldn't get lyrics.\n")
    sleep(60 * tweet_frequency_mins)
    continue

  ##############################
  #### Create tweet's text

  lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)  # Remove lyric identifiers
  lyrics = lyrics.replace('[','').replace(']','')

  lyrics = re.sub(r'[\n]{2,}', '\n\n', lyrics)  # Standardize paragraph spacing

  lyrics = lyrics.split("\n\n")  # Split lyrics into paragraphs

  for paragraph in lyrics:
    print(paragraph, "\n\n","*"*25)

  tweet = choice(lyrics) + "\n\n({} - {})".format(artist_name, song_name)

  ##############################
  #### Twitter API

  consumer_key =    'nsObgpOuFpytQDX6YQdXgTzLB'
  consumer_secret = '48A68WvbO7YTOBoXZ566CCJE0RBzRuMuucS5K2V4jGW3t0LeOY'
  access_token =    '1324426316695932928-M42ziiKmoThiEkS1C401eKcv2CVz6M'
  access_secret =   'qKN5hl9bQq4ret79uwpz6Cq7jBNzt87h4ulYf0w7KChSk'

  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_secret)
  api = tweepy.API(auth)

  api.update_status(tweet)  # Tweet the verse

  last_tweeted = song_name

  sleep(60 * tweet_frequency_mins)