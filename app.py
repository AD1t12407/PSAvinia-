
import streamlit as st
import json
import os
import plotly.express as px
import pandas as pd
from scrape import fetch_scholar_data, save_author_data
from summarization import BartSummarizer
from scrape import fetch_scholar_data, save_author_data
# Define the path to the authors folder
AUTHORS_FOLDER = 'authors'

def read_json_file(file_path):
    """Reads a JSON file and returns its content."""
    with open(file_path, 'r') as file:
        return json.load(file)

def filter_publications(publications, min_citations=0, start_year=None, end_year=None):
    """Filters publications based on the given criteria."""
    filtered = []
    for pub in publications:
        # Convert year to an integer if it's not 'Unknown'
        try:
            year = int(pub['year'])
        except ValueError:
            year = None  # Handle 'Unknown' year case
        
        if pub['citations'] >= min_citations:
            if year is not None and (start_year is None or year >= start_year) and \
               (end_year is None or year <= end_year):
                filtered.append(pub)
            elif year is None:  # If year is 'Unknown', include it if other conditions are met
                filtered.append(pub)
                
    return filtered
def main():
    st.title("Faculty Publication Summarizer")

    # List all JSON files in the authors folder
    files = [f for f in os.listdir(AUTHORS_FOLDER) if f.endswith('.json')]
    names = [os.path.splitext(f)[0] for f in files]
    # add a new faculty member
    new_name = st.text_input("Enter a new faculty member's name")
    try:
        if new_name:
            author_data = fetch_scholar_data(new_name)
            # buffer the next line by 10 secs to avoid the error
            if author_data:
                save_author_data(author_data)
                st.write(f"Data saved for {new_name}")
    except Exception as e:
        pass
    
    # Create a dropdown for selecting names
    selected_name = st.selectbox("Select a exsisitng faculty member", names)

    # If a name is selected, try to read the JSON file
    if selected_name:
        file_path = os.path.join(AUTHORS_FOLDER, f"{selected_name}.json")
        
        if os.path.exists(file_path):
            # Read and display the JSON data from the file
            json_data = read_json_file(file_path)
        else:
            st.write(f"No data available for {selected_name}. Please scrape the data first.")
            return

        st.json(json_data)

        # Filtering options
        st.subheader("Filter Publications")
        start_year = st.number_input("Start Year", min_value=1900, max_value=2024, value=2000)
        end_year = st.number_input("End Year", min_value=1900, max_value=2024, value=2024)
        min_citations = st.number_input("Minimum Citations", min_value=0, value=10)

        # Filter publications
        filtered_pubs = filter_publications(json_data['publications'], min_citations, start_year, end_year)

        # Display filtered publications
        st.write(f"Found {len(filtered_pubs)} publications matching the criteria.")
        for pub in filtered_pubs:
            st.write(f"**{pub['title']}** ({pub['year']}) - {pub['citations']} citations")

        # Display plots
        if filtered_pubs:
            st.subheader("Research Metrics Plots")
            
            # Plot: Number of Papers and Citations
            total_papers = len(filtered_pubs)
            total_citations = sum(pub['citations'] for pub in filtered_pubs)
            data = {
                "Metrics": ["Total Papers", "Total Citations"],
                "Count": [total_papers, total_citations]
            }
            df = pd.DataFrame(data)
            fig = px.bar(df, x="Metrics", y="Count", title=f"Research Metrics for {selected_name}")
            st.plotly_chart(fig)
            
            # Plot: Publications per Year
            publication_years = {}
            for pub in filtered_pubs:
                year = pub['year']
                if year in publication_years:
                    publication_years[year] += 1
                else:
                    publication_years[year] = 1

            years = list(publication_years.keys())
            counts = list(publication_years.values())
            data = {
                "Year": years,
                "Publications": counts
            }
            df = pd.DataFrame(data)
            fig = px.line(df, x="Year", y="Publications", title=f"Publications per Year for {selected_name}")
            st.plotly_chart(fig)
            
        # Summarization
        if st.button("Summarize Publications"):
            summarizer = BartSummarizer()
            st.subheader("Publication Summaries")
            for pub in filtered_pubs:
                summary = summarizer.summarize(pub['title'])
                st.write(f"**{pub['title']}** - Summary: {summary}")

if __name__ == "__main__":
    main()