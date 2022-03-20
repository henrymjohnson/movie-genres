# Predicting Movie Genres

## About

This project classifies movies into various genres based on their scripts.

## Structure

The bulk of the project is contained in the jupyter notebook with various helper functions defined in other files.
- `imsdb.py` is scrapes script data from IMSDB using `BeautifulSoup`
- `clean_imsdb.py` is used to clean data scraped from the IMSDB website
- `fuzzy.py` defines a function to provide fuzzy matching for combining data from different sources that may have slight differences in the movie names

## Usage

To use, you'll need SciKit-Learn, Pandas, Numpy, tqdm, rapidfuzz, bs4.

After installing these packages, clone the repo, and run it.

Alternatively, you can run it directly in the browser by substituting '.dev' for '.com' in the GitHub url and stepping through the notebook.
