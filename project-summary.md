# Project Summary
This project is meant to build a vector database for the purpose of building a natural language search for Titan's tech support webpages.

# Directory Structure
- data/raw
- data/clean
- data/vectors

# Steps
1. Scrape the tech support webpages and gather all of the links in data/raw for each of DistrictPortal and POS
- Run scrape_tech_support.py
2. Extract the content from each of the links and store in data/clean for each of DistrictPortal and POS
- Run clean_data.py
3. Vectorize the data and store in data/vectors
- Run vectorize_data.py
4. Build the vector database with FAISS
- Run search_vectors.py
5. Run the Flask app to host the QA system
- Run app.py
