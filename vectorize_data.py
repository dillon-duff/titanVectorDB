import json
from sentence_transformers import SentenceTransformer
import concurrent.futures
import os

def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def vectorize_text(model, text):
    return model.encode(text).tolist()

def process_data(data, model):
    """
    Vectorize all text data concurrently.
    """
    vectors = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {
            executor.submit(vectorize_text, model, content): url 
            for url, content in data.items()
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                vectors[url] = future.result()
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")
    return vectors

def save_vectors(vectors, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(vectors, f)

def main():
    model = SentenceTransformer('all-MiniLM-L6-v2')

    district_portal_data = load_data('data/clean/DistrictPortal/data.json')
    pos_data = load_data('data/clean/POS/data.json')

    print("Vectorizing DistrictPortal data...")
    district_portal_vectors = process_data(district_portal_data, model)
    print("Vectorizing POS data...")
    pos_vectors = process_data(pos_data, model)

    print("Saving vectors...")
    save_vectors(district_portal_vectors, 'data/vectors/DistrictPortal/vectors.json')
    save_vectors(pos_vectors, 'data/vectors/POS/vectors.json')
    print("Vectorization complete.")

if __name__ == "__main__":
    main()
