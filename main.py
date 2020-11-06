import os, re, spotipy, lyricsgenius, tweepy
from random import choice
from time import sleep

##############################
#### Spotify API

tweet_frequency_mins = int(os.getenv("TWEET_FREQUENCY_MINS"))

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

  GENIUS_CLIENT_ID = os.getenv("GENIUS_CLIENT_ID")
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

  if len(tweet) >= 280:
    trimmed_tweet = tweet.strip().split("\n")[0:4]  # First 4 lines
    trimmed_tweet += tweet.strip().split("\n")[-1]  # Last Line
    tweet = trimmed_tweet

  ##############################
  #### Twitter API

  tw_consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
  tw_consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
  tw_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
  tw_access_secret = os.getenv("TWITTER_ACCESS_SECRET")

  auth = tweepy.OAuthHandler(tw_consumer_key, tw_consumer_secret)
  auth.set_access_token(tw_access_token, tw_access_secret)
  api = tweepy.API(auth)

  api.update_status(tweet)  # Tweet the verse

  last_tweeted = song_name

  sleep(60 * tweet_frequency_mins)
