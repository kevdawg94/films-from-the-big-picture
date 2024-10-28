def create_upload_file_df(directory_path, file_suffix):
    # file suffix can be .csv, .txt, etc.
    # returns upload_rss_df (df containing TPB RSS feed info)
    # also creates global variable files_to_process - a list of file names corressponding to df

    import sys
    import pandas as pd
    import os
    
    global files_to_process
    
    sys.path.append('/content/drive/MyDrive/python_functions/')

    # Read The Big Picture RSS feed for podcast information
    from parse_tpb_rss_feed import create_tpb_rss_dataframe
    tpb_rss_df = create_tpb_rss_dataframe()

    # Read my own letterboxd RSS feed to see what the most recent episode I've made a list for
    from parse_letterboxd_rss_feed import create_letterboxd_episode_dataframe
    letterboxd_rss_df = create_letterboxd_episode_dataframe()

    # Filter tpb rss df for last 50 episodes when letterboxd list has not been created 
    upload_rss_df = tpb_rss_df[-50:][~tpb_rss_df['episode_number'].isin(letterboxd_rss_df['episode_number'])]

    return upload_rss_df

def create_files_to_process(directory_path, file_suffix):
    # file suffix can be .csv, .txt, etc.
    # returns upload_rss_df (df containing TPB RSS feed info)
    # also creates global variable files_to_process - a list of file names corressponding to df

    import sys
    import pandas as pd
    import os
    
    global files_to_process
    
    sys.path.append('/content/drive/MyDrive/python_functions/')

    # Read The Big Picture RSS feed for podcast information
    from parse_tpb_rss_feed import create_tpb_rss_dataframe
    tpb_rss_df = create_tpb_rss_dataframe()

    # Read my own letterboxd RSS feed to see what the most recent episode I've made a list for
    from parse_letterboxd_rss_feed import create_letterboxd_episode_dataframe
    letterboxd_rss_df = create_letterboxd_episode_dataframe()

    # Filter tpb rss df for last 50 episodes when letterboxd list has not been created 
    upload_rss_df = tpb_rss_df[-50:][~tpb_rss_df['episode_number'].isin(letterboxd_rss_df['episode_number'])]

    # Create df containing local files with dates that map to  
    directory_files = sorted(os.listdir(directory_path))
    files = list(filter(lambda x: x.endswith(file_suffix), directory_files))
    local_files_df = pd.DataFrame()
    local_files_df['name'] = files

    files_to_process = []
    for index, row in local_files_df.iterrows():
        if row['name'][1:9] in upload_rss_df['date'].astype(str).values:
            files_to_process.append(row['name'])

    return files_to_process