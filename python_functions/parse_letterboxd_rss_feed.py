
# Create Desired Dataframe Containing df of episode numbers already uploaded to Letterboxd

def create_letterboxd_episode_dataframe():

  # Imports
  import re
  import feedparser
  import pandas as pd

  # Read KevDawg_test RSS Feed for created lists
  d = feedparser.parse('https://letterboxd.com/kevdawg_test/rss/')
  rss_df = pd.DataFrame(d.entries)

  # Helper Functions
  def extract_episode_number(text):
      pattern = r"Episode number\s*(\d+)"
      match = re.search(pattern, text)
      if match:
          return int(match.group(1))
      else:
          return None

  letterboxd_episode_df = pd.DataFrame()
  letterboxd_episode_df['episode_number'] = rss_df['title'].apply(extract_episode_number)
  letterboxd_episode_df['title'] = rss_df['title']

  return letterboxd_episode_df

  