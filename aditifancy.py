import requests
from bs4 import BeautifulSoup

def scrape_google_scholar(faculty_name, year=None, domain=None, title=None):
    # Construct the search query
    query = faculty_name
    if year:
        query += f" {year}"
    if domain:
        query += f" {domain}"
    if title:
        query += f" {title}"
    
    # Replace spaces with "+" for the URL
    search_url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
    response = requests.get(search_url)
    
    if response.status_code != 200:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract publication details
    publications = []
    for result in soup.select('.gs_ri'):
        pub_title = result.select_one('.gs_rt').text if result.select_one('.gs_rt') else "No title"
        link = result.select_one('.gs_rt a')['href'] if result.select_one('.gs_rt a') else "No link"
        snippet = result.select_one('.gs_rs').text if result.select_one('.gs_rs') else "No snippet"
        publication_info = result.select_one('.gs_a').text if result.select_one('.gs_a') else "No info"
        
        # Filter by year if provided
        if year and str(year) not in publication_info:
            continue
        
        # Filter by domain if provided
        if domain and domain.lower() not in snippet.lower():
            continue
        
        # Filter by title if provided
        if title and title.lower() not in pub_title.lower():
            continue

        publications.append({"title": pub_title, "link": link, "snippet": snippet})
    
    return publications

# Get user input
faculty_name = input("Enter the faculty name: ")
year = input("Enter the publication year (leave blank if not applicable): ")
domain = input("Enter the domain (leave blank if not applicable): ")
title = input("Enter the title (leave blank if not applicable): ")

# Convert year to integer if provided
year = int(year) if year else None

# Scrape Google Scholar
results = scrape_google_scholar(faculty_name, year=year, domain=domain, title=title)

# Display results
for pub in results:
    print(f"Title: {pub['title']}\nLink: {pub['link']}\nSnippet: {pub['snippet']}\n")
