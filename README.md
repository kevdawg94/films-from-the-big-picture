<h1 align="center">Films from The Big Picture</h1>

<p align="center">
    <img src="https://github.com/user-attachments/assets/bf038b6c-da05-42a6-b72f-5ead25b03da7" width="400">
</p>


## Creating Letterboxd lists for the Big Picture podcast archive.

This repository contains a python pipeline that maintains an up-to-date [catalogue of "The Big Picture" podcast episodes as Letterboxd lists](https://letterboxd.com/kevdawg_test/lists/by/newest/). I love movies - I’m an avid [Big Picture](https://www.theringer.com/the-big-picture) podcast listener and longtime Letterboxd user. The creation of this catalogue is an effort to share a valuable resource with other members of both communities.

This repo contains the project design and codebase - for more information on my learnings from this side project you can read my [Medium writeup](https://medium.com/@kevin.celustka/films-from-the-big-picture-creating-a-letterboxd-archive-for-my-favorite-movie-podcast-17242f62a1e6). 

## Background

I have listened to [The Big Picture](https://www.theringer.com/the-big-picture) podcast since 2018 - the knowledge and opinions I’ve absorbed have helped me grow my knowledge and appreciation for cinema as an adult. The podcast format is engaging but has limitations for absorbing and referencing the dense information shared. The hosts and guest often discuss dozens of films each episode, of which I typically remember a few and miss out on the rest. This project aims to solve that problem, leveraging Langchain's LLM structured output to create [**Letterboxd**](https://letterboxd.com/) lists to accompany each episode of the Big Picture podcast.

## List Design
Letterboxd lists are a great way to structure and share film catalogues. In addition to the film identification, this project leverage the list description to add value for listeners.

<p align="center">
    <img width="715" alt="Screenshot 2024-11-12 at 2 37 51 PM" src="https://github.com/user-attachments/assets/2f2fb9fe-ec3f-4578-8e39-a9eaf6d024f3">
</p>

1. **Timestamp Links**: Timestamp links for each film mentioned are included facilitate a frictionless interface between the audio version of the podcast and the Letterboxd list. I hope this will continue to drive list-viewers to revisit the podcast itself.
<p align="center">
   <img width="696" alt="image" src="https://github.com/user-attachments/assets/b8f1a3a3-af79-4e71-a665-5bc8a05025e4">
</p>

3. **Reference Context**: The reason for the reference to the film is included in a single sentence summary that includes the speaker name. 

4. **Ranking and Drafting**: When list-making or "drafting" occurs in the podcast, the final results are appended to the bottom of the description.
<p align="center">
   <img width="542" alt="image" src="https://github.com/user-attachments/assets/05c51f1c-923f-4794-bacc-c6f6e3374b6b">
</p>

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
* [ ] Simplify podcast info collection in list_creation.py using rss feed info. 
* [ ] Collaborations with the Ringer?
