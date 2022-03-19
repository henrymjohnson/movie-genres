import pandas as pd
import os
import json
from rapidfuzz import process
import re

"""
This function cleans the imsdb script data and incorporates the release date from the metadata into it.

Return: dataframe with the following columns
    string  file_name	
    string  movie_title	
    string  script	x
    string  release_date	
    string  title_year
"""

def clean_imsdb():
    movies_df = pd.DataFrame(columns = ['file_name', 'movie_title', 'script'])

    # Clean script data
    files = [f for f in os.listdir('./scripts/unprocessed/imsdb/') if os.path.isfile(os.path.join('./scripts/unprocessed/imsdb/', f))]
    for filename in files:
        if filename.endswith(".txt"): 
            file_name = os.path.join(filename)
            title = filename[:len(file_name)-4].replace('-', ' ')
            path = './scripts/unprocessed/imsdb/' + file_name
            with open(path, 'r') as file:
                # read in file and replace new line characters
                script = file.read().replace('\n', ' ')
            # replace multiple spaces with single space
            script = re.sub(' +', ' ', script)

            df = pd.DataFrame([{
                'file_name': file_name, 
                'movie_title':title, 
                'script':script
                }])
            movies_df = movies_df.append(df)
            continue
        else:
            continue

    # Pull in metadata
    meta_data_dict = json.load(open('scripts/metadata/imsdb.json'))
    meta_data_df = pd.DataFrame()

    file_name_arr = []
    release_date_arr = []
    for val in meta_data_dict.values():
        for k, v in val.items():
            file_name = ''
            release_date = ''
            if k == 'file_name':
                file_name = v
                file_name_arr.append(file_name)
            if k == 'release_date':
                release_date = v
                release_date_arr.append(release_date)

    meta_data_df['file_name'] = file_name_arr
    meta_data_df['file_name'] = meta_data_df['file_name'].map(lambda x: x + '.txt')
    meta_data_df['release_date'] = release_date_arr

    # Merge movie data with metadata
    movies_with_release_date = movies_df.merge(meta_data_df, on='file_name')
    movies_with_release_date['title_year'] = movies_with_release_date['movie_title'] + ' (' + movies_with_release_date['release_date'] + ')'

    # Return dataframe
    return movies_with_release_date