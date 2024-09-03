import os
import requests
from bs4 import BeautifulSoup
import json

def scrape_google_scholar(faculty_name):
    # Check if the author has a JSON file
    json_path = f"authors/{faculty_name}.json"
    if os.path.exists(json_path):
        print(f"Already have the data for {faculty_name}")
        with open(json_path, "r") as f:
            return json.load(f)
    
    # Make the authors directory if it doesn't exist
    if not os.path.exists("authors"):
        os.makedirs("authors")
    
    search_url = f"https://scholar.google.com/scholar?q={faculty_name.replace(' ', '+')}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    publications = []
    total_citations = 0
    
    for result in soup.select('.gs_ri'):
        # Extract title
        title = result.select_one('.gs_rt').text.strip()
        
        # Extract link
        link_tag = result.select_one('.gs_rt a')
        link = link_tag['href'] if link_tag else "No link available"
        
        # Extract snippet
        snippet = result.select_one('.gs_rs').text.strip() if result.select_one('.gs_rs') else "No snippet available"
        
        # Extract citation count
        citation_tag = result.select_one('.gs_fl')
        citation_text = citation_tag.find(text=lambda x: "Cited by" in x) if citation_tag else None
        citations = int(citation_text.split()[-1]) if citation_text else 0
        total_citations += citations
        
        # Extract publication year
        year_tag = result.select_one('.gs_a')
        year_text = year_tag.text if year_tag else None
        year = None
        if year_text:
            # Try to find a 4-digit year in the text
            for part in year_text.split():
                if part.isdigit() and len(part) == 4:
                    year = part
                    break

        publications.append({
            "title": title, 
            "link": link, 
            "snippet": snippet, 
            "citations": citations,
            "year": year
        })
    
    # Summarize fields of work
    fields_of_work = set()
    for pub in publications:
        if pub['snippet']:
            fields_of_work.update(pub['snippet'].split())
    summary_of_fields = ', '.join(sorted(fields_of_work)) if fields_of_work else "Unknown"
    
    author_data = {
        "author": faculty_name,
        "total_papers": len(publications),
        "total_citations": total_citations,
        "publications": publications,
        "summary_of_fields": summary_of_fields
    }
    
    # Save to JSON file in the authors folder
    with open(json_path, "w") as f:
        json.dump(author_data, f, indent=4)
    
    print(f"Scraped data for {faculty_name}")
    return author_data

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
        scrape_google_scholar(faculty_name)
