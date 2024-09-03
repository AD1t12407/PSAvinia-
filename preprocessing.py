import json
import re
from collections import Counter
import nltk

# Download the 'punkt' tokenizer models
nltk.download('punkt')

# Download the stopwords corpus
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download the NLTK stopwords
nltk.download('stopwords')
nltk.download('punkt')

def clean_text(text):
    # Remove special characters, numbers, and convert to lower case
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

def extract_keywords(publications):
    all_titles = " ".join([pub['title'] for pub in publications])
    all_titles_cleaned = clean_text(all_titles)
    
    # Tokenize and remove stopwords
    tokens = word_tokenize(all_titles_cleaned)
    filtered_tokens = [word for word in tokens if word not in stopwords.words('english')]
    
    # Count term frequencies
    term_frequencies = Counter(filtered_tokens)
    
    return term_frequencies

def process_author_data(author_data):
    # Extract keywords from the author's publications
    term_frequencies = extract_keywords(author_data['publications'])
    
    # Get the top 20 most common terms
    most_common_terms = term_frequencies.most_common(20)
    
    return most_common_terms

if __name__ == "__main__":
    # Load the JSON data (replace with the actual path to your JSON file)
    with open('authors/geoffrey_hinton.json', 'r') as f:
        author_data = json.load(f)
    
    # Process the author's data
    most_common_terms = process_author_data(author_data)
    
    print(f"Most Common Terms for {author_data['author']}:")
    for term, frequency in most_common_terms:
        print(f"{term}: {frequency}")
