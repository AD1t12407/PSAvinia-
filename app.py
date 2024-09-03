import streamlit as st
import json
import os
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

# Define the path to the authors folder
AUTHORS_FOLDER = 'authors'

def read_json_file(file_path):
    """Reads a JSON file and returns its content."""
    with open(file_path, 'r') as file:
        return json.load(file)

def scrape_google_scholar(name):
    """Placeholder function to scrape Google Scholar."""
    # Replace this with actual scraping logic
    return {
        "name": name,
        "papers": 0,
        "citations": 0,
        "publications": []
    }

def main():
    st.title("Name to JSON Viewer")

    # List all JSON files in the authors folder
    files = [f for f in os.listdir(AUTHORS_FOLDER) if f.endswith('.json')]
    names = [os.path.splitext(f)[0] for f in files]
    
    # Create a dropdown for selecting names
    selected_name = st.selectbox("Select a name", names)

    # If a name is selected, try to read the JSON file
    if selected_name:
        file_path = os.path.join(AUTHORS_FOLDER, f"{selected_name}.json")
        
        if os.path.exists(file_path):
            # Read and display the JSON data from the file
            json_data = read_json_file(file_path)
        else:
            # Scrape data if file does not exist
            json_data = scrape_google_scholar(selected_name)
            # Optionally, you could save this data to a file for future use
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)

        st.json(json_data)
        
        # Display charts
        if 'publications' in json_data:
            # Extract data for charts
            total_paers = json_data['total_papers']
            total_citations = json_data['total_citations']

            # Number of papers and citations
            st.write(f"Total Papers: {total_paers}")
            st.write(f"Total Citations: {total_citations}")

            # Create a bar chart for the number of papers and citations
            data = {
                "Metrics": ["Total Papers", "Total Citations"],
                "Count": [total_paers, total_citations]
            }
            df = pd.DataFrame(data)
            fig = px.bar(df, x="Metrics", y="Count", title=f"Research Metrics for {selected_name}")
            st.plotly_chart(fig)
            
            # Find the years of publication and citations
            publicationDict = {}
            for publication in json_data['publications']:
                year = publication['year']
                if year in publicationDict:
                    publicationDict[year] += 1
                else:
                    publicationDict[year] = 1
            
            # Create a line chart for the number of publications per year
            years = list(publicationDict.keys())
            counts = list(publicationDict.values())
            data = {
                "Year": years,
                "Publications": counts
            }
            df = pd.DataFrame(data)
            fig = px.line(df, x="Year", y="Publications", title=f"Publications per Year for {selected_name}")
            st.plotly_chart(fig)
            
            
            
                
                
            

            
        else:
            st.write("No publication data available.")

if __name__ == "__main__":
    main()
