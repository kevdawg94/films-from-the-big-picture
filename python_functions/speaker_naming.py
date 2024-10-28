
# process_speaker01_file.py
directory_path = "/content/drive/MyDrive/TBP_Project/Transcripts/"

def process_speaker01_file(directory_path):
    import os
    import time
    import pandas as pd
    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.pydantic_v1 import BaseModel, Field
    from typing_extensions import Annotated
    from operator import itemgetter

    import sys
    sys.path.append('/content/drive/MyDrive/python_functions/')

    #Create files to process df
    from file_upload_df_from_rss import create_files_to_process, create_upload_file_df  
    tpb_rss_df = create_upload_file_df(directory_path, 'speaker01.csv')
    speaker01_files_to_process = create_files_to_process(directory_path, 'speaker01.csv')

    # Define the structured template for speaker identification
    speaker_identification_query = """
    You are an expert speaker identification system. You are extremely accurate and precise.
    I will provide you with a speaker. Read the podcast transcript and identify the speaker's first and last name.
    I will provide a list of host and guest names. Always choose a name from the "guests" lists or "hosts" list provided.

    If you are unsure about the speaker's name, take your time and review the full transcript using these strategies: 

    1. Speakers will introduce themselves.
    i.e. "I'm John Doe, welcome to the show." This speaker that introduced themselves and is John Doe.

    2. Hosts will introduce guests by name when they join. They will often describe them or their work for context.
    i.e. "I'm so excited to be speaking with John Doe today. John, welcome to the show." The Speaker that responds to this introduction is John.
    
    3. Look for the most common names mentioned right before or after this speaker appears in the podcast.
    i.e. if the name 'John Doe' is mentioned frequently before and after response by Speaker_01, speaker 01 is likely John.

    4. Speakers will respond when another participant asks them a question directly by name. Check for this.
    i.e. "So John, what did you think of the movie?" The next speaker is John.
  
    Using the outcome of each of these methods, identify the requested speaker. 
    Respond with the speaker's first and last name only. 
    
    """

    # Define the speaker model for the JSON output parser
    class Speaker(BaseModel):
        Name: str = Field(description="The first name and last name of the speaker")
        # Name: Annotated[str, ..., "The first name and last name of the speaker"]

    # Configure the output parser
    json_parser = JsonOutputParser(pydantic_object=Speaker)

    # Setting up the LLM model
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    json_speaker_identification_prompt = PromptTemplate(
        template=""""
        Answer the user query.
        \n {format_instructions}
        \n\n {query}
        \n\n The speaker to identify is: {speaker}.
        \n\n Hosts: {hosts} & Guests: {guests}. Choose a name from these lists.
        \n\n Transcript: {transcript}.
        """,
        input_variables=[
            "query", 
            "speaker", 
            "transcript",  
            "hosts", 
            "guests"
            ],
        partial_variables={"format_instructions": json_parser.get_format_instructions()},
    )

    # Combine the prompt template and the model with the JSON parser
    json_speaker_identification_chain = json_speaker_identification_prompt | model | json_parser

    # Function to identify speaker using LLM
    def get_speaker_name(speaker_identification_query, speaker, unique_speakers, speaker_mapping, 
        transcript, updated_hosts, updated_guests):
        
        speaker_name = json_speaker_identification_chain.invoke({
            "query": speaker_identification_query,
            "speaker": speaker,
            "transcript": transcript,
            "hosts": updated_hosts,
            "guests": updated_guests
        })
        return speaker_name

    # Main function logic for processing speaker01 files
    def name_speakers(directory_path, speaker01_file):    
        file_path = directory_path + speaker01_file
        # Check if .txt file was created
        base_name = file_path[:-14]
        txt_name = f"{base_name}.txt"
        if os.path.isfile(txt_name) is True:
            return

        # Wait to avoid RAM overload
        time.sleep(7)

        print('.txt file does not exist. Beginning processing of ' + speaker01_file)
        diarization = pd.read_csv(file_path)
        # Create set of unique speakers
        unique_speakers = sorted(set(diarization['speaker'].unique()))
        print('unique speakers: ' + str(unique_speakers))
        # Gather info from RSS Feed
        episode_rss_info = tpb_rss_df[tpb_rss_df['date'] == speaker01_file[1:9]]
        if len(episode_rss_info) > 1:
            print('multiple episodes this day - skipping')
            return

        print(episode_rss_info[['guests', 'hosts']])
        summary = episode_rss_info['summary'].values.item()
        
        def split_list_string_into_list(input_list):
            # Function to convert strings to list format from RSS feed
            if input_list and isinstance(input_list[0], str):
                # Split the first element of the list by commas and strip extra spaces
                return [item.strip() for item in input_list[0].split(',')]
            else:
                return input_list  # Return the original list if it's empty or not a string

        # Check RSS imports and apply conversion to list format when needed
        if len(episode_rss_info['hosts'].values.item()) == 1:
            hosts = split_list_string_into_list(episode_rss_info['hosts'].values.item())
        else:
            hosts = episode_rss_info['hosts'].values.item()

        if len(episode_rss_info['guests'].values.item()) == 1:
            guests = split_list_string_into_list(episode_rss_info['guests'].values.item())
        else:
            guests = episode_rss_info['guests'].values.item()

        # Skip feed episodes without Sean and Amanda (guest series etc.)
        if 'sean fennessey' not in [host.lower() for host in hosts] and 'amanda dobbins' not in [host.lower() for host in hosts]:
            print('Non Sean & Amanda episode, skipping')
            return

        speaker_mapping = {} # Dictionary is added to with each loop 
        print('beginning rule-based identification of speaker')
        for speaker in unique_speakers:
            line_count = 0
            full_text = ''
            for index, row in diarization.iterrows():
                if speaker == row['speaker']:
                    line_count += 1
                    full_text += ' ' + row['text'].lower()

                    if line_count >= 50:
                        break

            # Using literal text matching that occur in many episodes, make quick assingments
            if 'i\'m sean fennessey' in full_text or 'i\'m sean f' in full_text:
                speaker_mapping[speaker] = 'Sean Fennessey'
                print('Found Sean')
                continue

            if 'i\'m amanda dobbins' in full_text or 'i\'m amanda d' in full_text:
                speaker_mapping[speaker] = 'Amanda Dobbins'
                print('Found Amanda')
                continue

            if ('the ringer podcast network' in full_text
                or 'bill simmons from the ringer' in full_text
                or 'liz kelley' in full_text
                or 'it\'s bill simmons' in full_text):
                speaker_mapping[speaker] = 'Advertisement'
                print('Advertisement')
                continue

            if line_count <= 20:
                speaker_mapping[speaker] = 'Unknown'
                # print('Unimportant Part')
                continue

        print('Completed rule-based mapping. Current speaker_mapping:')
        print()
        
        # Perform LLM-based speaker identification for remaining speakers   
        transcript = ""
        for _, row in diarization.iterrows():
            # Format each line as "Speaker [timestamp]: text"
            transcript += f"{row['speaker']} [{row['start']}]: {row['text']} "

        # Flag for when assigned roles have been depleted to reset the list
        # Can set this flag to false to keep all hosts/guests selectable for looping
        reset_list = False
        updated_guests = []
        updated_hosts = []        

        for speaker in unique_speakers:
            if speaker in list(speaker_mapping.keys()):
                continue
            else:
                print('LLM-based identification of ' + speaker)

                if reset_list is False: 
                    # Update hosts and guests to exclude already identified speakers unless list is empty
                    updated_hosts = [name for name in hosts if name not in list(speaker_mapping.values())]
                    updated_guests = [name for name in guests if name not in list(speaker_mapping.values())]

                # If there are more speakers than there are options, reset host/guest lists with all participants
                if len(updated_guests)+len(updated_hosts)==0:
                    updated_guests = guests
                    updated_hosts = hosts
                    updated_hosts.append('Bobby Wagner')  # Append 'Bobby Wagner' to the list
                    reset_list = True
                    print('Reset hosts & guests')

                print("Hosts: ", updated_hosts)
                print("Guests: ", updated_guests)

                speaker_name = get_speaker_name(
                    speaker_identification_query, 
                    speaker, unique_speakers, 
                    speaker_mapping,
                    transcript, 
                    updated_hosts, 
                    updated_guests
                )

                # Check for compliance with JSON format and add key/value to speaker_mapping dict
                if 'Name' in speaker_name:
                    print('identified ' + speaker + ' as: ' + speaker_name['Name'])
                    speaker_mapping[speaker] = speaker_name['Name']
                else:
                    print('speaker name: ', speaker_name)
                    print('Identification error, speaker set to Unknown')
                    speaker_mapping[speaker] = 'Unknown'

        # Export resulting diarized transcript to .txt
        with open(txt_name, "w", encoding="utf-8") as txt:
            for index, row in diarization.iterrows():
                speaker = speaker_mapping.get(row['speaker'], row['speaker'])
                txt.write(f"{round(row['start'], 0)} {speaker}: {row['text']}\n")

        # Check for successful .txt file writing
        if os.path.isfile(txt_name):
            print(f"{txt_name} has been created.")
            print('Moving to next audio file.')
            print()
            print()

    for speaker01_file in speaker01_files_to_process:
        name_speakers(directory_path, speaker01_file)