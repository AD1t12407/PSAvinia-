import streamlit as st
import pandas as pd
import requests
import pybtex.database
from transformers import BartForConditionalGeneration, BartTokenizer

# Initialize BART model and tokenizer
model_name = "facebook/bart-large-cnn"
bart_model = BartForConditionalGeneration.from_pretrained(model_name)
bart_tokenizer = BartTokenizer.from_pretrained(model_name)

# Function to get abstract from DOI using CrossRef API
def get_abstract_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        abstract = data['message'].get('abstract', 'No abstract found.')
        return abstract
    else:
        return f"Error: {response.status_code}"

# Function to summarize an abstract using BART
def summarize_abstract_bart(abstract):
    inputs = bart_tokenizer([abstract], max_length=1024, return_tensors="pt", truncation=True)
    summary_ids = bart_model.generate(inputs.input_ids, num_beams=4, max_length=150, early_stopping=True)
    summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Function to generate a combined summary using BART
def combined_summary_bart(abstracts):
    combined_text = " ".join(abstracts)
    summary = summarize_abstract_bart(combined_text)
    return summary

# Streamlit UI
st.title("Faculty Publication Summary Generator")

# Step 1: Upload BibTeX File
uploaded_file = st.file_uploader("Upload BibTeX File", type="bib")
if uploaded_file is not None:
    # Read the file as text
    file_content = uploaded_file.read().decode("utf-8")
    
    # Parse the BibTeX data
    bibtex_data = pybtex.database.parse_string(file_content, bib_format='bibtex')
    
    # Step 2: Extract and Select Author
    authors = set()
    author_papers = {}
    
    for entry in bibtex_data.entries.values():
        for person in entry.persons.get("author", []):
            # Full name construction
            full_name = " ".join(person.prelast_names + person.last_names)
            authors.add(full_name)
            if full_name not in author_papers:
                author_papers[full_name] = []
            author_papers[full_name].append(entry)
    
    selected_author = st.selectbox("Select Author", sorted(authors))
    
    if selected_author:
        # Step 3: Select Time Period
        years = [int(paper.fields.get('year', 0)) for paper in author_papers[selected_author]]
        
        if years:
            min_year = min(years)
            max_year = max(years)
            
            if min_year != max_year:
                selected_years = st.slider(
                    "Select Time Period",
                    min_value=min_year,
                    max_value=max_year,
                    value=(min_year, max_year)
                )
            else:
                # If min_year == max_year, no slider is needed
                selected_years = (min_year, max_year)
                st.write(f"Only one year available: {min_year}")
        else:
            st.write("No publication years available.")
            selected_years = (2022, 2022)  # Placeholder years
            
        # Filter papers by selected time period
        filtered_papers = [
            paper for paper in author_papers[selected_author]
            if int(paper.fields.get('year', 0)) >= selected_years[0] and int(paper.fields.get('year', 0)) <= selected_years[1]
        ]
        
        if filtered_papers:
            abstracts = []
            summaries = []
            for paper in filtered_papers:
                doi = paper.fields.get('doi', '')
                if doi:
                    abstract = get_abstract_from_doi(doi)
                    abstracts.append(abstract)
                    summary = summarize_abstract_bart(abstract)  # Summarize each abstract using BART
                    summaries.append({"DOI": doi, "Summary": summary})
            
            # Display individual summaries
            st.subheader(f"Summaries for {selected_author} ({selected_years[0]} - {selected_years[1]})")
            df_summaries = pd.DataFrame(summaries)
            st.write(df_summaries)
            
            # Generate and display combined summary
            if abstracts:
                combined = combined_summary_bart(abstracts)  # Generate combined summary using BART
                st.subheader("Combined Summary")
                st.write(combined)
                
                # Option to download summaries and combined summary as Excel
                df_summaries["Combined Summary"] = combined
                st.download_button("Download Summary as Excel", df_summaries.to_csv(index=False), file_name="publication_summary.xlsx")
        else:
            st.write("No publications found for the selected period.")
