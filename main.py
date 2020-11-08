import os, re, spotipy, lyricsgenius, tweepy
from random import choice
from time import sleep

def follow_back():

  for follower in tweepy.Cursor(api.followers).items():

    try:
      follower.follow()
      print('Followed', follower.screen_name, 'back :)')
    except TwitterError:
      continue    

#  followers=[api.followers()]
#  following=[api.friends()]
#  for follower in followers:
#      if not follower in following:            
#          api.create_friendship(follower)
#          print('Followed ' + follower.screen_name + ' back.')

TWEET_FREQUENCY_MINS = int(os.getenv("TWEET_FREQUENCY_MINS"))

SPOTIFY_USERNAME = os.getenv("USERNAME")

GENIUS_CLIENT_ID = os.getenv("GENIUS_CLIENT_ID")

TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

#### Get current listening data from Spotify

scope = 'user-read-currently-playing'

token = spotipy.util.prompt_for_user_token( SPOTIFY_USERNAME, scope)

last_tweeted = ""

while True: # Iterates every 2 minutes checks for a song

  sp = spotipy.Spotify(auth=token)
  current_song = sp.currently_playing()

  if current_song == None:
    print("\nNot listening anything.\n")
    sleep(60 * TWEET_FREQUENCY_MINS)
    continue

  artist_name = current_song['item']['artists'][0]['name']

  song_name = current_song['item']['name']

  if song_name == last_tweeted:
    print("\nSong already tweeted.\n")
    sleep(60 * TWEET_FREQUENCY_MINS)
    continue
    
  print("\n", "   Artist name:", artist_name, end="\n\n")
  print(     "    Song name:", song_name, end="\n\n")

  #### Get song's lyrics from Genius

  genius = lyricsgenius.Genius(GENIUS_CLIENT_ID)

  song = genius.search_song(song_name, artist_name)

  try:
    lyrics = song.lyrics
  except ( AttributeError): #if return None
    print("\nCouldn't get lyrics.\n")
    sleep(60 * TWEET_FREQUENCY_MINS)
    continue

  #### Create tweet's text

  lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)  # Remove lyric identifiers
  lyrics = lyrics.replace('[','').replace(']','')

  lyrics = re.sub(r'[\n]{2,}', '\n\n', lyrics)  # Standardize paragraph spacing

  lyrics = lyrics.split("\n\n")  # Split lyrics into paragraphs

  for paragraph in lyrics:
    print(paragraph, "\n\n","*"*25)

  tweet = choice(lyrics) + "\n\n({} - {})".format(artist_name, song_name)

  if len(tweet) >= 280:
    trimmed_tweet = trimmed_tweet = "\n".join(tweet.strip().split("\n")[0:4])  # First 4 lines
    trimmed_tweet += "\n\n" + tweet.strip().split("\n")[-1]  # Last Line
    tweet = trimmed_tweet

  #### Send the tweet with Twitter API

  auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
  auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
  api = tweepy.API(auth)

  api.update_status(tweet)  # Tweet the verse

  last_tweeted = song_name


  follow_back()

  sleep(60 * TWEET_FREQUENCY_MINS)