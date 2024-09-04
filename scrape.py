from scholarly import scholarly
import json
import os

# Define the path to the authors folder
AUTHORS_FOLDER = 'authors'

def fetch_scholar_data(faculty_name):
    """Fetches data from Google Scholar for the given faculty name."""
    # Search for the author
    search_query = scholarly.search_author(faculty_name)
    author = next(search_query, None)

    if not author:
        print(f"No results found for {faculty_name}")
        return None

    # Fill in the details of the author
    author = scholarly.fill(author)
    
    # Retrieve author's publications and citations
    publications = []
    total_citations = 0

    for pub in author['publications']:
        title = pub['bib']['title']
        citations = pub.get('num_citations', 0)
        year = pub['bib'].get('pub_year', 'Unknown')
        link = pub.get('eprint_url', 'No link available')

        total_citations += citations

        publications.append({
            "title": title,
            "year": year,
            "citations": citations,
            "link": link
        })

    author_data = {
        "author": faculty_name,
        "affiliation": author['affiliation'],
        "total_papers": len(publications),
        "total_citations": total_citations,
        "publications": publications,
        "summary_of_fields": ', '.join(author['interests']) if author['interests'] else "Unknown"
    }

    return author_data

def save_author_data(author_data):
    """Saves the author data to a JSON file."""
    os.makedirs(AUTHORS_FOLDER, exist_ok=True)
    file_name = f"{author_data['author'].replace(' ', '_')}.json"
    file_path = os.path.join(AUTHORS_FOLDER, file_name)
    
    with open(file_path, 'w') as f:
        json.dump(author_data, f, indent=4)

if __name__ == "__main__":
    researchers = [
        "Geoffrey Hinton",
        "Yann LeCun",
        "Andrew Ng",
        "Yoshua Bengio",
        "Ian Goodfellow",
        "Christopher Manning",
        "Sebastian Ruder",
        "Fei-Fei Li",
        "Richard Socher",
        "Andrej Karpathy",
        "Jürgen Schmidhuber",
        "Thomas Mikolov",
        "Samy Bengio",
        "Tim Salimans",
        "Sergey Levine",
        "Alex Graves",
        "Pieter Abbeel",
        "Kyunghyun Cho",
        "Anima Anandkumar",
        "Ilya Sutskever"
    ]

    for faculty_name in researchers:
        author_data = fetch_scholar_data(faculty_name)
        if author_data:
            save_author_data(author_data)
            print(f"Author data for {faculty_name} saved successfully.")
