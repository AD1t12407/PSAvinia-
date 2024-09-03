from scholarly import scholarly
import json

def fetch_scholar_data(faculty_name):
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
        citations = pub['num_citations']
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
    with open(f"authors/{author_data['author'].replace(' ', '_')}.json", 'w') as f:
        json.dump(author_data, f, indent=4)

if __name__ == "__main__":
    researcher = ["Geoffrey Hinton"]
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
            print(f"Author Data for {faculty_name} saved successfully")
        
            
