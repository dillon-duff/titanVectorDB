# Project Summary
This project implements an advanced Question Answering (QA) system for Titan's tech support webpages. It uses NLP and vector search to provide context-aware responses to user queries. The system scrapes tech support content, processes it into a vector database, and uses this to power a Flask-based web application that can understand and respond to user questions in natural language.

# Directory Structure
- data/raw: Contains scraped links from tech support webpages
- data/clean: Stores processed and cleaned textual content
- data/vectors: Houses vectorized data and FAISS index files

# Project Setup
1. Clone the repository:
   ```
   git clone https://github.com/dillon-duff/titanVectorDB
   cd titanVectorDB
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here # On Windows use:
                                           # set OPENAI_API_KEY=your_api_key_here
   ```

# Step
1. Scrape the tech support webpages and gather all of the links in data/raw for each of DistrictPortal and POS
   - Run `python scrape_tech_support.py`
2. Extract the content from each of the links and store in data/clean for each of DistrictPortal and POS
   - Run `python clean_data.py`
3. Vectorize the data and store in data/vectors
   - Run `python vectorize_data.py`
4. Build the vector database with FAISS
   - Run `python build_search_vectors.py`
5. Run the Flask app to host the QA system
   - Run `python app.py`

After completing these steps, the QA system should be up and running. You can access it by opening a web browser and navigating to `http://localhost:5000`
