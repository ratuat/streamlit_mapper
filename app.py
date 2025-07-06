import streamlit as st
import pandas as pd
from utils import *

import requests
import json

def api_request (payload, API_KEY, API_URL):

    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        # Send POST request
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except ValueError as e:
        return f"Failed to decode JSON response: {e}"
    
API_KEY = st.secrets['API_KEY']
API_URL = st.secrets['API_URL']

if 'results' not in st.session_state:
    st.session_state.results = []
    
# Initialize the session state DataFrame
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        'concept_code': [''],
        'concept_name': [''],
        'domain_id': [''],
        'vocabulary_id': [''],
        'processing': ['']
    })

# Editable table with only first 4 columns editable
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,  # 👈 Hides the index column
    column_config={
        "processing": st.column_config.TextColumn("processing", disabled=True)
    }
)

# Add row programmatically
if st.button('Process the data'):

    # Ensure column is string type to avoid dtype warning
    st.session_state.df = edited_df
    
    edited_df['processing'] = edited_df['processing'].astype(str)
    
    for index, row in edited_df.iterrows():
        
        if row['processing']:
            continue
        
        code = row['concept_code']
        name = row['concept_name']
        domain = row['domain_id']
        vocab = row['vocabulary_id']
        
        code = code if code else ''
        domain = domain if domain else ''
        vocab = vocab if vocab else ''
        
        payload = {
            "concept_code": code,
            "concept_name": name,
            "domain_id": domain,
            "vocabulary_id": vocab
        }
        print (payload)
        results = api_request(payload, API_KEY, API_URL)
        
        print (results)
        
        for result in results:
        
            top_1 = f"{result['top_1']['concept_id']} | {result['top_1']['concept_name']} | {result['top_1']['domain_id']} | {result['top_1']['vocabulary_id']} | {result['top_1']['score']}"
            mapping_candidates = result['mapping_candidates']
            
            mapping_candidates_to_list = [f"{candidate['concept_id']} | {candidate['concept_name']} | {candidate['vocabulary_id']} | {candidate['domain_id']} | {candidate['score']}"
                                          for candidate in mapping_candidates]

        st.session_state.results.append([f"{code} - {name} - {domain} - {vocab}", mapping_candidates_to_list, top_1])

        edited_df.loc[index, 'processing'] = 'processed'
    
    # Save back to session state
    st.session_state.df = edited_df    


if st.session_state.results:
    st.title("Concept Mapping Results")
    
    for i, result in enumerate(st.session_state.results):
        concept_str = result[0]
        candidates = result[1]
        top_1 = result[2][0] if result[2] else "No top-1 match"

        with st.expander(f"🧠 Concept: {concept_str.strip()}"):

            selected = st.selectbox(
                f"List of candidates",
                options=candidates,
                key=f"select_{i}"
            )
            st.markdown(f"Top_1 candidate: :blue[{selected}]")