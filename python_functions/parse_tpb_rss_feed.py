
# Create Desired Dataframe
def create_tpb_rss_dataframe():

  # Imports
  import re
  import feedparser
  import pandas as pd

  # Read Big Picture
  d = feedparser.parse('https://feeds.megaphone.fm/the-big-picture')
  rss_df = pd.DataFrame(d.entries)

  # Helper Functions
  def find_host(content):
      # Regex pattern to match content between 'Host:' or 'Hosts:' and the next colon
      pattern = r'(?:Host|Hosts):\s*([^\n]+)'

      # Search for the pattern in the content
      match = re.search(pattern, content)

      # Return the found content if a match is found, otherwise None
      return match.group(1).strip() if match else 'None'

  def find_guest(content):
      # Regex pattern to match content between 'Host:' or 'Hosts:' and the next colon
      pattern = r'(?:Guest|Guests):\s*([^\n]+)'

      # Search for the pattern in the content
      match = re.search(pattern, content)

      # Return the found content if a match is found, otherwise None
      return match.group(1).strip() if match else 'None'

  def split_names(text):
      # Check if the text is 'None'
      if text == 'None':
          return []
      # First, split by 'and', then further split each part by commas
      names = []
      for part in text.split(' and '):
          # Split by commas and strip whitespace
          names.extend([name.strip() for name in part.split(',') if name.strip()])
    
      return names

  def extract_href(value):
    # Check if the value is a list and has at least one item
    if isinstance(value, list) and len(value) > 0:
        # Check if the first item is a dictionary and has the 'href' key
        if isinstance(value[0], dict) and 'href' in value[0]:
            return value[0]['href']
    
    # Return None if the expected structure is not met
    return None

  rss_df_extracted = rss_df[['title', 'summary', 'published']]
  rss_df_extracted['URL'] = rss_df['links'].apply(extract_href)
  rss_df_extracted['published'] = pd.to_datetime(rss_df['published'])
  rss_df_extracted['date'] = pd.to_datetime(rss_df['published']).dt.strftime('%Y%m%d')
  rss_df_extracted['hosts'] = rss_df['summary'].apply(find_host).apply(split_names)
  rss_df_extracted['guests'] = rss_df['summary'].apply(find_guest).apply(split_names)

  sorted_rss_df = rss_df_extracted.sort_values('published', ascending=True)
  sorted_rss_df['episode_number'] = range(1, len(sorted_rss_df) + 1)

  return sorted_rss_df

  