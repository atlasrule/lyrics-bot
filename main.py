import os, datetime, re, spotipy, lyricsgenius, tweepy, string
from ytmusicapi import YTMusic
from random import uniform
from random import choice
from time import sleep
from mastodon import Mastodon


def follow_back():
  for follower in tweepy.Cursor(api.followers).items():
    try:
      follower.follow()
      print('Followed', follower.screen_name, 'back :)')
    except:
      continue


# Create non-repetitive fairy lights
def create_fairy_lights(length):
  coloredLights = "🔴🟠🟡🟢🔵🟣"
  fairyLights = ""
  lastOne = "x"

  for i in range(length):
    while True:
      picked = choice(coloredLights)      
      if (picked != lastOne):
        break

    fairyLights += picked
    lastOne = picked

  return fairyLights


def is_it_new_year_time():
  today = datetime.datetime.today()
  if today.month == 12 and today.day > 28:
    return True
  if today.month == 1 and today.day == 1:
    return True  
  else:
    return False

first_run = True

MAX_TWEET_LENGTH = 280
FAIRY_LENGTH = 11

TWEET_FREQUENCY_MINS = int(os.getenv("TWEET_FREQUENCY_MINS"))
SPOTIFY_USERNAME = os.getenv("USERNAME")
GENIUS_CLIENT_ID = os.getenv("GENIUS_CLIENT_ID")
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")

#### Get current listening data from Spotify

scope = 'user-read-currently-playing'

token = spotipy.util.prompt_for_user_token( SPOTIFY_USERNAME, scope)

last_tweeted = ""


while True: # Iterates every x minutes

  if not first_run:
    sleep(60 * uniform(5, 2*TWEET_FREQUENCY_MINS - 5))
      
  first_run = False
  listening = False


  # Get current listening data from Youtube Music
  ytmusic = YTMusic('headers_auth.json')

  #if ytmusic.get_history().played:
  print( ytmusic.get_history().played )
  artist_name = ytmusic.get_history()[0]['artists'][0]['name']
  song_name = ytmusic.get_history()[0]['title']
  listening = True


  
  # Get current listening data from Spotify
  sp = spotipy.Spotify(auth=token)
  current_song = sp.currently_playing()

  if current_song != None:
    artist_name = current_song['item']['artists'][0]['name']
    song_name = current_song['item']['name']



  if not listening:
    print("Not listening anything.\n")
    continue

  song_name = song_name.split(' (', 1)[0] # Delete paranthesis

  if song_name == last_tweeted:
    print("\nThe song already tweeted.\n")
    continue

  print("\n", "   Artist name:", artist_name, end="\n\n")
  print(     "    Song name:", song_name, end="\n\n")

  song_name = song_name.split(" - ")[0] # Remove dash identifers


  #### Get song's lyrics from Genius

  genius = lyricsgenius.Genius(GENIUS_CLIENT_ID)

  song = genius.search_song(song_name, artist_name)

  try:
    lyrics = song.lyrics
  except ( AttributeError): #if return None
    print("\nCouldn't get lyrics.\n")
    continue


  #### Create tweet's text

  lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)  # Remove lyric identifiers
  lyrics = lyrics.replace('[','').replace(']','')

  stopwords = ['Embed', 'Share Url', ':', 'Copy', 'Share URL']

  for stopword in stopwords:
    lyrics = lyrics.replace(stopword, '')

  
  lyrics = lyrics.rstrip(string.digits) # Remove genius' number shit

  lyrics = re.sub(r'^.*?Lyrics', '', lyrics) # Remove genius' "xyz Lyrics" shit

  lyrics = re.sub(r'[\n]{2,}', '\n\n', lyrics)  # Standardize paragraph spacing

  lyrics = lyrics.split("\n\n")  # Split lyrics into paragraphs

  for paragraph in lyrics:
    print(paragraph, "\n\n","*"*25)

    # Remove empty paragraphs
    if len(paragraph) < 3: lyrics.remove(paragraph)

  # Don't post if lyrics only includes 'instrumental'
  if len(lyrics) <= 1 and 'Instrumental' in lyrics[0].split(' ')[0]:
    print("\nTrack is Instrumental.\n")
    continue

  tweet = choice(lyrics) + "\n\n{} - {}".format(artist_name, song_name)

  if is_it_new_year_time():
    MAX_TWEET_LENGTH -= FAIRY_LENGTH*2 + 2

  if len(tweet) >= MAX_TWEET_LENGTH:
    # First 4 lines
    trimmed_tweet = "\n".join(tweet.strip().split("\n")[0:4])  
    trimmed_tweet += "\n\n" + tweet.strip().split("\n")[-1]  # Last Line
    tweet = trimmed_tweet

  if is_it_new_year_time():
    tweet = create_fairy_lights(FAIRY_LENGTH)+'\n'+tweet+'\n'+create_fairy_lights(FAIRY_LENGTH)


  #### Send the tweet with Twitter API

  auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
  auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
  api = tweepy.API(auth)

  api.update_status(tweet)  # Tweet the verse


  #### Send the tweet with Mastodon API
  
  mastodon = Mastodon(
      access_token = MASTODON_ACCESS_TOKEN,
      api_base_url = 'https://botsin.space/'
  )

  mastodon.status_post(tweet)

  #TODO: Follow back for Mastodon. 


  last_tweeted = song_name

  follow_back()

# Love