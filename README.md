# films-from-the-big-picture
## Creating Letterboxd lists for the Big Picture podcast archive.

This project aims to create an up-to-date catalogue of Big Picture podcast episodes as Letterboxd lists. I love movies - I’m an avid Big Picture listener and longtime Letterboxd user. The creation of this catalogue is an effort to share a valuable resource with other members of both communities.

I have listened to the Big Picture podcast since 2018 - the knowledge and opinions I’ve absorbed have helped me grow my knowledge and appreciation for cinema as an adult. The podcast format is engaging, but has limitations for absorbing and referencing the dense information shared. The hosts and guest often discuss dozens of films each episode, of which I can typically only note down a few and miss out on the rest.

Because many of the discussions in this podcast revolve around list-making, this was low-hanging fruit for an LLM to help synthesize and format the discussions into a structured output. The LLM was also well suited to identify the films mentioned with an output that can be used in an automated uploaded to Letterboxd.

## Reason to Build

Letterboxd is where film nerds share reviews, lists, and connect with one another. Letterboxd is where I save a watch list, and can filter for movies I want to watch that are available on the services I subscribe to. When it comes time to watch a movie, I want to easily access the recommendations on Letterboxd from the Big Picture pod I listened to last week without having to listen to the podcast again.

There are no official representations of the Big Picture podcast on Letterboxd, but the appetite was there from the audience. Some community members have intermittently manually created Letterboxd lists for this podcast. They manually wrote down the films mentioned, and manually selected them from the Letterboxd UI, requiring hours of time for each one. These dedicated listeners have been too busy to continue the practice and have only completed a handful of episodes from the 700+ episode catalogue.

## Design

Letterboxd lists are a great way to structure and share this catalogue. All that was left for me to add is the list title and description.

Timestamp Links: Timestamp links for each film mentioned to facilitate a frictionless interface between the audio version of the podcast and list. I hope this will continue to drive list-viewers to revisit the podcast itself.

## Framework

All steps are executed in a single Google Colab notebook that is set to execute weekly to keep the catalogue up to date.

1. Download podcasts from the RSS feed using Podcast downloader. This repo creates a catalogue of files to transcribe from an RSS feed. Relatively plug and play. Able to save the files in .WAV format, required for whisperX. Each week I’ll run the script to download the most recent episodes and execute the remaining steps.

2. Transcribe and diarize the podcast audio using WhisperX. There are many options but this seems like the most popular / fastest. I was happy with the accuracy. The transcripts are usually spot on but the diarization struggles occasionally when two speakers have a similar voice pitch or talk over one another.   

3. Name the speakers in the diarized transcript using OpenAI gpt-4o. Using a list of hosts and guests from the podcast, I ask got-4o to identify one speaker at a time using the context of the transcript.

4. Summarize the podcast transcript using OpenAI gpt-4o. Create a 4-5 sentence summary for the subjects discussed in this podcast episode to provide basic context for the Letterboxd list. This is saved in a CSV for upload to Letterboxd.

5. Create table of films mentioned in the podcast using OpenAI gpt-4o. Letterboxd allows for list creation from a CSV of film names and release years.t-4o + Langchain to return this 5.  information in a structure JSON format, which includes a one-sentence summary of the reference and a timestamp link so that viewers can go directly to that moment in the podcast. 

6. Upload the summary & film list to Letterboxd using Selenium. Selenium loops through the summary and film table CSVs, executing the Letterboxd create list flow. 
