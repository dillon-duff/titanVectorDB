from search_vectors import VectorSearch
import json
from typing import Callable, Dict, Any
import os
from openai import OpenAI

searcher = VectorSearch()
searcher.load_vectors("data/vectors/DistrictPortal/vectors.json")
searcher.load_index("data/vectors/DistrictPortal/index.faiss")


def get_page_content(url):
    with open("data/clean/DistrictPortal/data.json", "r") as f:
        data = json.load(f)
    return data.get(url, "Content not found")


class QAModel:
    def __init__(self, model_func: Callable[[str, str], Dict[str, Any]]):
        self.model_func = model_func

    def generate_answer(self, question: str, context: str, contexts_dict) -> Dict[str, Any]:
        return self.model_func(question, context, contexts_dict)


def openai_model(
    question: str, context: str, contexts_dict: Dict[int, str]
) -> Dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Please cite your sources using numbered references "
                        "like {1}, {2}, etc., based on the provided context."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Given the context: {context}\n\nAnswer this question by citing sources: {question}",
                },
            ],
        )
        resp = response.choices[0].message.content
        for i in range(10):
            ref = f"{{{i}}}"
            if ref in resp and i < len(contexts_dict):
                resp = resp.replace(ref, f"[{i+1}]({contexts_dict[i]})")
        return {"answer": resp}
    except Exception as e:
        return {"error": str(e)}


qa_model = QAModel(openai_model)


def qa_system(question: str, top_k: int = 5):
    if not question:
        raise ValueError("Question text is required.")

    results = searcher.search(question, top_k=top_k)

    numbered_results = {i + 1: res["url"] for i, res in enumerate(results)}

    contexts = [f"[{i}] {get_page_content(url)}" for i, url in numbered_results.items()]

    contexts_dict = {i: url for i, url in numbered_results.items()}

    combined_context = " ".join(contexts)

    answer = qa_model.generate_answer(question, combined_context, contexts_dict)

    return answer


if __name__ == "__main__":
    question = input("Enter your question: ")
    answer = qa_system(question)
    print(answer)
    for line in answer["answer"].split("\n"):
        print(line)
