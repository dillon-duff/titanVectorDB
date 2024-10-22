import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorSearch:
    def __init__(self, index_path=None, vectors_path=None):
        """
        Initialize the VectorSearch with optional paths to save/load the FAISS index and vectors.
        """
        self.index = None
        self.vectors = {}
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        if vectors_path:
            self.load_vectors(vectors_path)
            self.build_index()
        
        if index_path:
            self.load_index(index_path)
    
    def load_vectors(self, vectors_path):
        """
        Load vectors from a JSON file.
        """
        with open(vectors_path, 'r') as f:
            self.vectors = json.load(f)
        self.vector_dim = len(next(iter(self.vectors.values())))
        print(f"Loaded {len(self.vectors)} vectors.")

    def build_index(self):
        """
        Build a FAISS index from the loaded vectors.
        """
        vector_matrix = np.array(list(self.vectors.values())).astype('float32')
        self.index = faiss.IndexFlatL2(self.vector_dim)
        self.index.add(vector_matrix)
        print("FAISS index built and vectors added.")

    def save_index(self, index_path):
        """
        Save the FAISS index to disk.
        """
        faiss.write_index(self.index, index_path)
        print(f"FAISS index saved to {index_path}.")

    def load_index(self, index_path):
        """
        Load a FAISS index from disk.
        """
        self.index = faiss.read_index(index_path)
        print(f"FAISS index loaded from {index_path}.")

    def search(self, query, top_k=5):
        """
        Search for the top_k most similar vectors to the query.
        """
        query_vector = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_vector, top_k)
        results = []
        urls = list(self.vectors.keys())
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(urls):
                results.append({'url': urls[idx], 'distance': distance})
        return results

if __name__ == "__main__":
    with open('data/vectors/DistrictPortal/vectors.json', 'r') as f:
        district_portal_vectors = json.load(f)
    with open('data/vectors/POS/vectors.json', 'r') as f:
        pos_vectors = json.load(f)
    
    combined_vectors = {**district_portal_vectors, **pos_vectors}
    
    with open('data/vectors/combined_vectors.json', 'w') as f:
        json.dump(combined_vectors, f)
    
    searcher = VectorSearch(vectors_path='data/vectors/combined_vectors.json')
    searcher.build_index()
    searcher.save_index('data/vectors/combined_index.faiss')
    
    # Create separate indices as before
    searcher = VectorSearch(vectors_path='data/vectors/DistrictPortal/vectors.json')
    searcher.build_index()
    searcher.save_index('data/vectors/DistrictPortal/index.faiss')
    
    searcher = VectorSearch(vectors_path='data/vectors/POS/vectors.json')
    searcher.build_index()
    searcher.save_index('data/vectors/POS/index.faiss')

    

    query = "How to void a transaction for a student"
    results = searcher.search(query, top_k=10)
    print("Top search results:")
    for res in results:
        print(res)
