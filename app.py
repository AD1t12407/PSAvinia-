
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

# Define the gradient colors
colors = ["red", "orange", "yellow", "blue", "purple"]

# Function to determine the color based on the citation count
def get_color(citations):
    # Define citation thresholds
    thresholds = [10, 50, 100, 200]  # Example thresholds, adjust according to your data
    if citations < thresholds[0]:
        return colors[0]  # red
    elif citations < thresholds[1]:
        return colors[1]  # orange
    elif citations < thresholds[2]:
        return colors[2]  # yellow
    elif citations < thresholds[3]:
        return colors[3]  # blue
    else:
        return colors[4]  # p

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
                json_data = read_json_file(os.path.join(AUTHORS_FOLDER, f"{new_name}.json"))
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

        # Display filtered publications as bullet points
        st.write(f"Found {len(filtered_pubs)} publications matching the criteria.")
        count = 1
        for pub in filtered_pubs:
            #st.write(f"**{pub['title']}** ({pub['year']}) - {pub['citations']} citations")
            color = get_color(pub["citations"])
            st.write(f"{count}. **{pub['title']}** ({pub['year']}) - <span style='color:{color};'>{pub['citations']} citations</span>", unsafe_allow_html=True)
            count += 1
            
            

        # Display plots
        if filtered_pubs:
            st.subheader("Research Metrics Plots")
            
            # Plot: Number of Papers and Citations 
            total_papers = len(filtered_pubs)
            total_citations = sum(pub['citations'] for pub in filtered_pubs)
            st.write(f"Total Papers: {total_papers}")
            st.write(f"Total Citations: {total_citations}")
            
            
            # Plot: Publications per Year bar plot
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
            fig = px.bar(df, x="Year", y="Publications", title=f"Publications per Year for {selected_name}")
            st.plotly_chart(fig)
            
            # year wise citation growth graph
            citation_years = {}
            for pub in filtered_pubs:
                year = pub['year']
                if year in citation_years:
                    citation_years[year] += pub['citations']
                else:
                    citation_years[year] = pub['citations']
            
            years = list(citation_years.keys())
            counts = list(citation_years.values())
            data = {
                "Year": years,
                "Citations": counts
            }
            df = pd.DataFrame(data)
            fig = px.bar(df, x="Year", y="Citations", title=f"Citations per Year for {selected_name}")
            st.plotly_chart(fig)
            
            # Plot: Citations culminated over the years graph
            # sort citation years by year and then aggregate the citations till that year
            citation_years = dict(sorted(citation_years.items()))
            # make culmulative citations a dict with till that year as key and total citations till that year as value
            cumulative_citations = {}
            total = 0
            for year, citation in citation_years.items():
                total += citation
                cumulative_citations[year] = total
            
            # now plot only the cumulative citations dict as bar plot
            years = list(cumulative_citations.keys())
            counts = list(cumulative_citations.values())
            data = {
                "Year": years,
                "Citations": counts
            }
            df = pd.DataFrame(data)
            # give nice looking gradient color to the bar plot
            fig = px.bar(df, x="Year", y="Citations", title=f"Cumulative Citations per Year for {selected_name}", color='Citations')
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