import chromadb
import torch
from transformers import AutoModel, AutoTokenizer
import numpy as np

model_name = "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("movies")

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).to(torch.float)
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)
    sum_mask = torch.clamp(torch.sum(input_mask_expanded, dim=1), min=1e-9)
    return sum_embeddings / sum_mask

def search_movie(query, expected_genre=None):
    encoded_input = tokenizer(query, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**encoded_input)
    query_embedding = mean_pooling(model_output, encoded_input["attention_mask"]).numpy()

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=5
    )

    if not results["metadatas"]:
        return "Không tìm thấy phim phù hợp."

    best_movies = []
    for metadata in results["metadatas"][0]:
        if expected_genre and expected_genre.lower() not in metadata["genre"].lower():
            continue  
        best_movies.append(metadata)

    if not best_movies:
        return "Không tìm thấy phim đúng thể loại."

    result = "\n".join([f"{m['title']} - {m['genre']} - {m['schedule']}" for m in best_movies])
    return result

while True:
    query = input("Bạn muốn hỏi gì về lịch chiếu phim? (Nhập 'exit' để thoát): ")
    if query.lower() == "exit":
        break
    
    genre = None
    if "hài" in query:
        genre = "Hài"
    elif "hoạt hình" in query:
        genre = "Hoạt Hình"
    
    print("trả lời:", search_movie(query, expected_genre=genre))
