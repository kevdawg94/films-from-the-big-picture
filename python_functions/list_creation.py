# This python file contains a function create_movie_list thatexecutes a loop through .txt files that contain diarized transcripts of podcast episodes
# During the loop, a summary of the podcast is generated along with a list of films mentioned. 
# Both of these files are saved in CSV format under a folder titled .../CSV/
# These pairs of files (summary_ and json_ are uploaded to Letterboxd in the next step)

# Input: directory_path
# Output: Saved json_ and summary_ CSV files to directory_path/CSV/

def create_movie_lists(directory_path):
    """
    Generates movie lists from podcast transcripts.
    """

    # Chunking imports
    from langchain.prompts import PromptTemplate, ChatPromptTemplate

    # OpenAI imports
    from langchain_openai.embeddings import OpenAIEmbeddings
    from langchain_openai import ChatOpenAI
    import openai

    # Langchain imports
    from langchain.docstore.document import Document
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.output_parsers import CommaSeparatedListOutputParser
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.pydantic_v1 import BaseModel, Field

    import re
    import pandas as pd
    import csv
    import fnmatch
    import numpy
    import os
    from typing_extensions import Annotated, TypedDict, List
    import sys
    import time

    # Import python functions
    sys.path.append('/content/drive/MyDrive/python_functions/')
    
    # Read The Big Picture RSS & Letterboxd RSS feed to identify podcast list
    from file_upload_df_from_rss import create_upload_file_df, create_files_to_process
    files_to_process = create_files_to_process(directory_path, '.txt')
    rss_df = create_upload_file_df(directory_path, '.txt')

    print('count of files to process is: ', len(files_to_process))

    # Open Directory Path
    transcripts_path = "/content/drive/MyDrive/TBP_Project/Transcripts/"
    csv_path = csv_path = "/content/drive/MyDrive/TBP_Project/CSV/"
    directory_files = files_to_process
    summary_files = {os.path.splitext(f)[0] for f in os.listdir(csv_path) if f.startswith('summary_')}

    # Set model to OpenAI
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=0
    )

    # Summarization
    summarization_template = """

    Here is a transcript of a podcast hosted by Sean Fennessey and Amanda Dobbins. Each episode has several segments.

    Segments categories are:
        - Introduction: The host describes the segments that are coming up in the current episode.
        - Advertisement: A short section of sponsored content used to advertise products, events, etc. Advertisements have distinct beginnings and endings announced by the hosts.
        - Discussion: Discussion between hosts and guest(s).
        - Drafting: Selecting films to create lists.

    For all output ignore Advertisement segments and pretend they do not exist.

    Provide a brief summary of the transcript provided. The total summary should be 5-10 sentences and be in paragraph form.
    Make sure to mention the hosts and guests present in this episode and what parts of the episode they join for.

    Return the summary in plaintext with newlines between each sentence.

    Documentation:
    {context}

    """

    # List Making
    list_making_template = """
    Here is a transcript of a podcast about movies. In some episodes the guests and hosts make lists of movies.
    
    Check the whole transcript and look for lists where movies are ranked, ordered, or listed. Look for mentions of list types including: drafts, 
    top 5 lists, top 10 lists, rankings, power-rankings, best movies lists, hall of fames, favorite lists, or lists of predictions.

    Here is more information about each type of list-making:
    - "Drafting": Participants competatively select films building individual lists.
    - "Top Lists": Participants take turns selecting their favorite films from a genre, year, or topic.
    - "Top 5 or Top 10 movies": Participants make lists of movies on a particular topic. 
    - "Ranking movies" or "Power Rankings": Participants make ranked lists on a particular topic.
    - "Best movies of <topic>": Participants share their ranked list of movies for a topic, genre, or time period.
    - "Hall of fame for <topic>": Participants decide on the best movies to represent a person, genre, or topic.
    - "Our favorite <topic> movies": Participants share their favorie movies from a genre, topic, or time period.
    - "5 or 10 predictions about <topic>": Participants make a list of predictions for a future outcome.

    Anytime movies are discussed in a ranked or ordered fashion, that is a list. Don't miss any.
    We only care about lists of movies. Ignore other types of lists.
    Double check the transcript - don't miss any type of ranking, power-ranking, listing, or drafting. 

    If there was no 'list-making' in this episode, respond with an empty string: ''
    If there was list making in this episode, determine whether the participants are creating individual lists or collaborative lists and return all lists in the formatting described below.

    Rules:
    1. Each participant has the same number of items on their list.
    2. When "drafting" participants always make their own list.
    3. List items are always specific movie names. 
    4. Do not return generic lists.
    5. For list order, rank movie lists in the order that they were shared.
    6. Some transcripts may contain multiple types of lists.

    Here is a formatting example for a collaborative Top 10 list: 
    List(s) from this podcast episode:

    <List Title>, <List Author(s)>
        1. Movie Title
        2. Movie Title
        3. Movie Title
        4. Movie Title
        5. Movie Title
        6. Movie Title
        7. Movie Title
        8. Movie Title
        9. Movie Title
        10. Movie Title

    Here is a formatting example for individual Top 5 lists: 
    List(s) from this podcast episode:

    <List Title>, <List Author(s)>
        1. Movie Title
        2. Movie Title
        3. Movie Title
        4. Movie Title
        5. Movie Title
    
    <List Title>, <List Author(s)>
        1. Movie Title
        2. Movie Title
        3. Movie Title
        4. Movie Title
        5. Movie Title
    
    <List Title>, <List Author(s)>
        1. Movie Title
        2. Movie Title
        3. Movie Title
        4. Movie Title
        5. Movie Title


    Here is a formatting example for a competative movie draft with three participants: 
    List(s) from this podcast episode:

    <List Title>, <List Author(s)>
        1. Movie Title (Category)
        2. Movie Title (Category)
        3. Movie Title (Category)
        4. Movie Title (Category)
        5. Movie Title (Category)
        6. Movie Title (Category)

    <List Title>, <List Author(s)>
        1. Movie Title (Category)
        2. Movie Title (Category)
        3. Movie Title (Category)
        4. Movie Title (Category)
        5. Movie Title (Category)
        6. Movie Title (Category)

    <List Title>, <List Author(s)>
        1. Movie Title (Category)
        2. Movie Title (Category)
        3. Movie Title (Category)
        4. Movie Title (Category)
        5. Movie Title (Category)
        6. Movie Title (Category)

    Documentation:
    {context}

    """

    film_list_structured_template = """

    Here is a transcript of a podcast. This podcast is about movies. Extract information about every movie mentioned in this transcript.
    First, identify all films mentioned in the transcript. Read each and every line of the transcript to identify every movie mentioned. Don't miss any films.

    Return a list of dictionaries containing the following keys:
    - Title: The title of the movie
    - Year: The year this Film was released
    - Timestamp: The timestamp this movie was first mentioned in the episode in number of seconds (s)
    - URL: concatenate the URL (provided by the user) with the timestamp integer, ending in '#t=<timestamp integer>'
    - Mentioned_by: Who mentioned this movie in the podcast
    - Reason: A sentence describing who mentioned this film and why in the context of the conversation. Do not quote directly from the transcript.

    Double check the transcript to make sure you didn't miss any movies mentioned, even if they were only mentioned briefly.

    """

    """# Helper Functions"""

    # JSON chain
    class movie(BaseModel):
        title: str = Field(..., description="The title of the movie")
        year: int = Field(..., description="The year this film was released")
        timestamp: str = Field(..., description="The timestamp this movie was first mentioned in the episode in seconds (s)")
        url: str = Field(..., description="The URL related to this episode concatenated with the timestamp")
        mentioned_by: str = Field(..., description="Who mentioned this movie in the podcast")
        reason: str = Field(..., description="A sentence describing why the host mentioned this film in the context of the conversation")
            
    class movie_list(BaseModel):
        movie_list: List[movie]

    # configure output parser in chain or call parse()
    json_parser = JsonOutputParser(pydantic_object = movie_list)

    # Prompt
    json_film_prompt = PromptTemplate(
        template=""""
        Answer the user query.
        \n Format Instructions: {format_instructions}
        \n Query: {query}
        \n Transcript: {transcript}
        \n URL: {url}
        """,
        input_variables=[
            "query",
            "transcript",
            "url"
            ],  
        partial_variables={"format_instructions": json_parser.get_format_instructions()}
    )

    json_film_chain = json_film_prompt | model | json_parser

    # Summarization chain
    summarize_prompt = ChatPromptTemplate.from_template(summarization_template)
    summarize_chain = summarize_prompt | model | StrOutputParser()

    # List chain
    list_prompt = ChatPromptTemplate.from_template(list_making_template)
    list_chain = list_prompt | model | StrOutputParser()

    # Check length of transcript. If longer than X, create movie lists in loops.
    from langchain_text_splitters import CharacterTextSplitter
    set_chunk_size = 10000
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=set_chunk_size,
        chunk_overlap=500,
        length_function=len
    )

    def get_rss_df(rss_df, file):
        """
        This function checks for multiple podcasts published on the same day.
        If there are multiple podcasts, the user is prompted to select the desired podcast.
        """

        len_df = rss_df[rss_df['date'].astype(str)==file[1:9]]
        podcasts_per_date = len(len_df) # Number of podcasts released on date.
        if podcasts_per_date == 1:
            return len_df

        if podcasts_per_date > 1:
            # Display the 'URL' column with index numbers
            print("Multiple rows detected. Please select a row by entering the index number.")
            for index, rows in len_df.iterrows():
                print(f"Index: {index}, URL: {rows['URL']}")

            # Ask the user to select a row
            selected_index = int(input("Enter the index number of the row you want to use: "))

            # Ensure the input is valid
            if selected_index in len_df.index:
                return len_df.loc[selected_index]

    # Use the episode title in the transcript file_name to identify the corresponding mp3 link
    def get_rss_link(file_name, rss_df):
        global episode_beginning_link
        global episode_timestamp_link
        speaker_df = get_rss_df(rss_df, file_name) # identify correct line of mapping in case where two podcasts on one day

        if isinstance(speaker_df['URL'], str): # When podcast_per_date > 1, type is str already.
            episode_beginning_link = speaker_df['URL']

        else:
            episode_beginning_link = speaker_df['URL'].values.item()

        episode_timestamp_link = episode_beginning_link + '#t='

    # Extract podcast information
    def pod_info(podcast_transcript, podcast_title, rss_df):
        global episode_release_date
        global episode_title
        global episode_number
        global doc_heading
        global list_title

        # Date
        episode_release_date_numeric = re.search(r'[0-9]{8}', podcast_title).group()
        episode_release_date_dt = pd.to_datetime(episode_release_date_numeric, format='%Y%m%d')
        episode_release_date = episode_release_date_dt.strftime('%m/%d/%Y')

        # Title
        episode_title = re.search(r'(] )(.*?)(   | I |.txt)', podcast_title).group(2)

        # Episode Number
        if 'Ep. ' in podcast_title:
            episode_number = re.search(r'(Ep. )([0-9]+)', podcast_title).group(2)
        else:
            speaker_df = get_rss_df(rss_df, file_name)
            if isinstance(speaker_df['episode_number'], numpy.int64):
                episode_number = str(speaker_df['episode_number'])
            else:
                episode_number = str(speaker_df['episode_number'].values.item())

        # Document Heading
        doc_heading = 'This list is generated in reference to <a href="https://www.theringer.com/the-big-picture">The Big Picture Podcast</a> Episode ' + episode_number + ': <a href="' + episode_beginning_link + '">' + episode_title + '</a>' + '. Released on ' + episode_release_date + '.'
        list_title = 'Films from the Big Picture Podcast: ' + episode_title + '. Episode number ' + episode_number + '. Release date: ' + episode_release_date


    def get_episode_movie_list(film_list_structured_template, transcript, url):
        global episode_movie_list

        if len(transcript) <= set_chunk_size:
            episode_movie_list_short = json_film_chain.invoke({"query": film_list_structured_template,  "transcript": transcript, "url": url})
            episode_movie_list_complete = episode_movie_list_short['movie_list']
        else:
            episode_movie_list_complete = []
            for i in range(len(text_splitter.split_text(transcript))):
                split = text_splitter.split_text(transcript)[i]

                episode_movie_list_part = json_film_chain.invoke({"query": film_list_structured_template, "transcript": split, "url": url})
                for x in range(len(episode_movie_list_part['movie_list'])):
                    # Catch error in output JSON where the list is double nested)
                    if len(episode_movie_list_part['movie_list']) == 1:
                        episode_movie_list_complete.append(episode_movie_list_part['movie_list'][0])
                    else:
                       episode_movie_list_complete.append(episode_movie_list_part['movie_list'][x])

        # Dedupe list

        # Sort the list by 'timestamp' in ascending order
        sorted_episode_movie_list = sorted(episode_movie_list_complete, key=lambda x: float(x.get('timestamp', 0)), reverse=True)

        # Use a dictionary to remove duplicates, keeping the first occurrence
        deduped_episode_movie_dict = {item['title']: item for item in sorted_episode_movie_list}

        # Convert back to a list
        episode_movie_list_unsorted = list(deduped_episode_movie_dict.values())
        episode_movie_list = sorted(episode_movie_list_unsorted, key=lambda x: float(x.get('timestamp', 0)))
        return episode_movie_list

    def create_movie_link_sentence(episode_movie_dict):
        global movie_link_sentence
        movie_link_list = []

        # Translate dict into list
        for dict in episode_movie_dict:
            line = '<a href="' + dict["url"] + '">' + dict["title"] + '</a> - ' + dict["reason"] + '\n\n'
            movie_link_list.extend(line)

        # Translate list to string
        movie_links_intro = 'The films mentioned in this episode include:'
        movie_link_sentence = '\n\n\n\n <b>' + movie_links_intro + '<b> \n\n' + ''.join(movie_link_list)


    # Loop through transcripts
    def process_transcripts(file_name, directory_files, directory_path):
        # episode_transcript = open(transcripts_path + file_name).read()
        """
        Processes individual transcript files, extracting movie titles and other information.
        """
        # Open the file using 'utf-8' encoding
        with open(transcripts_path + file_name, 'r', encoding='utf-8') as f:
            episode_transcript = f.read()

        transcript_title = file_name
        base_name = os.path.splitext(file_name)[0]

        # if os.path.isfile(csv_path + 'summary_'f"{base_name}.csv") is True:
        #     return

        print('CSV summary file does not exist. Beginning processing of ' + file_name)

        get_rss_link(file_name, rss_df)
        pod_info(episode_transcript, transcript_title, rss_df)

        # Summarization
        summarized_episode = summarize_chain.invoke({"context": episode_transcript})

        # List Making
        episode_lists = list_chain.invoke({"context": episode_transcript})

        # JSON generation
        episode_movie_list = get_episode_movie_list(film_list_structured_template, episode_transcript, episode_timestamp_link)
        # Create movie link sentence
        create_movie_link_sentence(episode_movie_list)

        # Write JSON output to CSV
        json_field_names = ["title", "year", "timestamp", "url", "mentioned_by", "reason"]
        base_name = os.path.splitext(file_name)[0]
        film_json_export_name = csv_path + 'json_'f"{base_name}.csv"

        with open(film_json_export_name, 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=json_field_names)
            writer.writeheader()
            writer.writerows(episode_movie_list)

        print('JSON CSV generation completed')

        # Write summarization output to CSV
        episode_summary = '<strong>' + doc_heading + '<strong>' '\n\n\n' + summarized_episode + movie_link_sentence + episode_lists
        summary_list = [(list_title, episode_summary)]

        summary_export_name = csv_path + 'summary_'f"{base_name}.csv"
        with open(summary_export_name, 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Episode_Title', 'Summary'])
            for row in summary_list:
                writer.writerow(row)

        print('Summary CSV generation completed')
        time.sleep(2)

    csv_files_set = {os.path.splitext(f)[0] for f in os.listdir(csv_path) if f.startswith('summary_')}
    for file_name in directory_files:
        base_name = os.path.splitext(file_name)[0]
        print('checking ', 'summary_'f"{base_name}")
        if 'summary_'f"{base_name}" in csv_files_set:
            continue
        process_transcripts(file_name, directory_files, directory_path)

