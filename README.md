<h1 align="center">films-from-the-big-picture</h1>

## Creating Letterboxd lists for the Big Picture podcast archive.

This repository contains a python pipeline that maintains an up-to-date [catalogue of "The Big Picture" podcast episodes as Letterboxd lists](https://letterboxd.com/kevdawg_test/lists/by/newest/). I love movies - I’m an avid [Big Picture](https://www.theringer.com/the-big-picture) podcast listener and longtime Letterboxd user. The creation of this catalogue is an effort to share a valuable resource with other members of both communities.

This repo outlines the project design and codebase - for more information you can read my medium writeup of the project. The article includes additional reflections, learnings, and roadmap. 

## Reason to Build

I have listened to [The Big Picture](https://www.theringer.com/the-big-picture) podcast since 2018 - the knowledge and opinions I’ve absorbed have helped me grow my knowledge and appreciation for cinema as an adult. The podcast format is engaging but has limitations for absorbing and referencing the dense information shared. The hosts and guest often discuss dozens of films each episode, of which I typically remember a few and miss out on the rest. In short - I have often wished the Ringer would publish these lists themselves, so I decided to do it myself.

Because many of the discussions in this podcast revolve around list-making, GAI was well-suited to capture film references and help synthesize and format the discussions and list-making into a structured output that can be used in an automated uploaded to Letterboxd.

[**Letterboxd**](https://letterboxd.com/) is where film nerds share reviews, lists, and connect with one another. Letterboxd is where I save a watch list, and can filter for movies I want to watch that are available on the services I subscribe to. When it comes time to watch a movie, I want to easily access the recommendations on Letterboxd from the Big Picture pod I listened to last week without having to listen to the podcast again. In summary, Letterboxd is the app that facilitates a social exploration into cinema.

Bringing the Big Picture to Letterboxd: While there are no official representations of the Big Picture on Letterboxd, I noticed an appetite for these lists from the Big Picture audience. Some community members have intermittently created Letterboxd lists for this podcast by hand. Each episode requiring hours to manually note films from the audio, select them from the Letterboxd UI, and add any individual analysis or commentary into each list. These dedicated listeners quickly became too busy to continue the practice and have only completed a handful of episodes out of the 700+ episode catalogue.


## List Design
Letterboxd lists are a great way to structure and share film catalogues. In addition to the film identification, this project leverage the list description to add value for listeners.

<img width="715" alt="Screenshot 2024-11-12 at 2 37 51 PM" src="https://github.com/user-attachments/assets/2f2fb9fe-ec3f-4578-8e39-a9eaf6d024f3">

1. **Timestamp Links**: Timestamp links for each film mentioned are included facilitate a frictionless interface between the audio version of the podcast and the Letterboxd list. I hope this will continue to drive list-viewers to revisit the podcast itself.

   <img width="696" alt="image" src="https://github.com/user-attachments/assets/b8f1a3a3-af79-4e71-a665-5bc8a05025e4">

3. **Reference Context**: The reason for the reference to the film is included in a single sentence summary that includes the speaker name. 

4. **Ranking and Drafting**: When list-making or "drafting" occurs in the podcast, the final results are appended to the bottom of the description.
   
   <img width="542" alt="image" src="https://github.com/user-attachments/assets/05c51f1c-923f-4794-bacc-c6f6e3374b6b">


## Data Pipeline

All steps are executed in a single [Google Colab ipython notebook](https://github.com/kevdawg94/films-from-the-big-picture/blob/main/scheduled_letterboxd_upload.ipynb) that is set to run daily to keep the catalogue up to date. Colab was leveraged in order to access the A100 GPU, which is required to transcribe and diarize the audio file.

Most of this pipeline is adaptable to another podcast with modifications to the RSS feed ingestion. The most interesting contribution is a generic solution for naming speakers in a diarized transcript, applying LLM to identify speaker names using conversational context, given a list of hosts and guests. More info in step 5 [speaker_naming.py](https://github.com/kevdawg94/films-from-the-big-picture/blob/main/python_functions/speaker_naming.py).

1. **Download podcasts from the RSS feed** using [podcast-downloader](https://github.com/dplocki/podcast-downloader). This repo creates a catalogue of files to transcribe from an RSS feed. Relatively plug and play - only [the config file](https://github.com/kevdawg94/films-from-the-big-picture/blob/main/podcast_downloader/the_big_picture_downloader_config.json) requires user input. Able to save the files in .WAV format, required for whisperX.

2. **Transcribe and diarize the podcast audio** using [WhisperX](https://github.com/m-bain/whisperX). There are many options but as of October 2024 WhisperX proved the most popular / fastest. The community support on github was essential for quick learning and debugging. I was happy with the accuracy of the resulting diarization but occasional, sometimes glaring errors persist. The transcripts are usually accurate, but sometimes miss-transcribe movie names, especially new or niche movies. The diarization also struggles occasionally when multiple speakers have similar voice pitch or talk over one another. The step is handled by [transcription.py](https://github.com/kevdawg94/films-from-the-big-picture/blob/main/python_functions/transcription.py).

5. **Name the speakers in the diarized transcript** using OpenAI gpt-4o. Using a list of hosts and guests from the podcast, I ask got-4o to identify one speaker at a time using the context of the transcript. This is handled by [speaker_naming.py](https://github.com/kevdawg94/films-from-the-big-picture/blob/main/python_functions/speaker_naming.py).

6. **Summarize the podcast transcript using OpenAI gpt-4o**. Create a 4-5 sentence summary for the subjects discussed in this podcast episode to provide basic context for the Letterboxd list. This is saved in a CSV for upload to Letterboxd. This is handled by [list_creation.py](https://github.com/kevdawg94/films-from-the-big-picture/blob/main/python_functions/list_creation.py).

7. **Create table of films mentioned in the podcast using OpenAI gpt-4o**. Letterboxd allows for list creation from a CSV of film names and release years. I use gpt-4o + Langchain to return this information in a structure JSON format, which includes a one-sentence summary of the reference and a timestamp link so that viewers can go directly to that moment in the podcast. This is handled by [list_creation.py](https://github.com/kevdawg94/films-from-the-big-picture/blob/main/python_functions/list_creation.py).

8. **Upload the summary & film list to Letterboxd** using [Selenium](https://github.com/SeleniumHQ). Selenium loops through the summary and film table CSVs, executing the Letterboxd create list flow. This is handled by [selenium_list_upload.py](https://github.com/kevdawg94/films-from-the-big-picture/blob/main/python_functions/selenium_list_upload.py).

## Data Requirements & File Management

**Diarization vs. Transcription:** Transcripts of the audio are publically available from Apple Podcasts, a diarized transcript (including speaker names) of the episodes increases the usefulness of the descriptions and the saliance of the inferences and lists.

**File structure for Letterboxd Upload Compatability**: 
1. CSV containing movie tiles & year released - titled "json_<episode_title>"
2. String containing List 'Title' - saved as column 1 in "summary_<episode_title>" CSV
3. String containing List 'Description' - saved as column 2 in "summary_<episode_title>" CSV

This pipeline preserves each intermediate .csv & .txt file prior to the final requirements. Diarized transcripts may be used in future steps for GAI applications including RAG. 
The pipeline requires these folders to organize the intermediate files: 

```
.
├── csv (CSV files ready for Selenium upload)
├── csv_uploaded (CSV files after Selenium upload) 
├── podcast_downloader (git clone of podcast-downloader repo with custom .config) 
├── python_functions (python files containing functions for each step of pipeline) 
└── transcripts (.wav, .csv, & .txt version of each episode) 
```

<h2 align="left" id="coming-soon">TODO 🗓</h2>

* [x] Transcription pipeline
* [x] Letterboxd upload pipeline
* [x] Backfill archive
* [x] Automate pipeline execution
* [ ] More efficient change data capture to reduce cost of daily executions
* [ ] Automate reddit posting for audience growth
* [ ] Collaborations with the Ringer?
