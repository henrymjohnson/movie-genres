from rapidfuzz import process

def fuzz_merge(left_df, right_df, left_key, right_key, lowest_acceptable_score=60):
    """
    left_df: left table
    right_df: right table
    left_key: left table's key value
    right_key: right table's key value
    lowest_acceptable_score: the score_cutoff parameter for process.extractOne()
    returns a dataframe with matched title
    """
    possible_matches = right_df[right_key].tolist()

    # process.extractOne returns a tuple with the match title, score, and the choice's key
    matches = left_df[left_key].apply(lambda x: process.extractOne(x, possible_matches, score_cutoff=lowest_acceptable_score)[0]) 
    left_df['matched_title'] = matches 
    
    return left_df