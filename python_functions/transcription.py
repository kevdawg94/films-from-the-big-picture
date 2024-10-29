
def process_diarization(transcripts_path):
    import os
    import re
    import pandas as pd
    import whisperx
    import warnings
    import string
    import csv
    import time

    # Parameters:
    device = "cuda"
    compute_type = "float16"
    batch_size = 16
    chunk_size = 30
    min_speakers = 3
    max_speakers = 15

    directory_files = sorted(os.listdir(transcripts_path))
    wav_files = list(filter(lambda x: x.endswith('.WAV'), directory_files))
    spaker01_files = list(filter(lambda x: x.endswith('speaker01.csv'), directory_files))

    def get_speaker_names(unique_speakers):
        speaker_mapping = {}
        for speaker in unique_speakers:
            name = input(f"Enter the name for {speaker}: ")
            speaker_mapping[speaker] = name
        return speaker_mapping

    # Function to check if .txt or .csv files exist
    def check_files_exist(audio_file, transcripts_path):
        audio_file_path = transcripts_path + audio_file
        base_name = os.path.splitext(audio_file_path)[0]
        csv_output = f"{base_name}_speaker01.csv"
        txt_name = f"{base_name}.txt"

        # Return True if either the .txt or .csv file exists
        return os.path.isfile(txt_name) or os.path.isfile(csv_output)

    # Define function for looping over audio files
    def process_audio_file(audio_file):
        audio_file_path = transcripts_path + audio_file
        base_name = os.path.splitext(audio_file_path)[0]
        csv_output = f"{base_name}_speaker01.csv"

        print('.txt file does not exist. Beginning processing of ' + audio_file)

        # Load the WhisperX model
        model = whisperx.load_model("large-v3", device, compute_type=compute_type, language='en')

        # Load an audio file
        audio = whisperx.load_audio(audio_file_path)

        # Transcribe the audio
        transcription = model.transcribe(audio, batch_size=batch_size, chunk_size=chunk_size)

        print('Completed transcription of ' + audio_file)

        # Align whisper output
        model_a, metadata = whisperx.load_align_model(language_code=transcription["language"], device=device)
        result = whisperx.align(transcription["segments"], model_a, metadata, audio, device, return_char_alignments=False)

        # Assign speaker labels
        diarize_model = whisperx.DiarizationPipeline(use_auth_token=HF_TOKEN, device=device)

        # Add diarization to result
        diarize_segments = diarize_model(audio)

        # Add diarization to result
        diarized_result = whisperx.assign_word_speakers(diarize_segments, result)

        # Create variable name for transcription
        diarization = diarized_result["segments"]

        # Add speaker label if missing
        for segment in diarization:
            if 'speaker' not in segment:
                segment['speaker'] = 'Unknown'

        # Export resulting diarized transcript to .csv
        keys = diarization[0].keys()
        with open(csv_output, 'w', encoding='utf-8', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(diarization)

        if os.path.isfile(csv_output):
            print(audio_file + ' has been created.')
            print('Moving to next audio file.')
            return

    # Main code to process audio file
    # Step 1: Create a list of audio files that need processing
    files_to_process = [audio_file for audio_file in wav_files if not check_files_exist(audio_file, transcripts_path)]
    print(files_to_process)

    # Step 2: Process the audio files in the list
    for audio_file in files_to_process:
        print('Beginning processing for ' + audio_file)
        process_audio_file(audio_file)
        time.sleep(5)
