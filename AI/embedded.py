import json
import chromadb
from sentence_transformers import SentenceTransformer

def embedding():
    with open("movies.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    client = chromadb.PersistentClient(path="./chroma_db")  
    collection = client.get_or_create_collection("movies")

    model = SentenceTransformer("VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")

    movie_details = []
    for day, movies in data.items():
        for movie in movies:
            doc = {
                "id": f"{movie['title']}_{day}", 
                "text": f"Tiêu đề: {movie['title']} Thể loại: {movie['genre']} Mô tả: {movie['description']}",
                "metadata": {
                    "day": day,
                    "title": movie["title"],
                    "genre": movie["genre"],
                    "duration": movie["duration"],
                    "schedule": movie["schedule"]
                }
            }
            movie_details.append(doc)

    texts = [m["text"] for m in movie_details]
    embeddings = model.encode(texts, convert_to_numpy=True)

    collection.add(
        ids=[m["id"] for m in movie_details],
        embeddings=embeddings.tolist(),
        metadatas=[m["metadata"] for m in movie_details]
    )

    print("Đã tạo embedding và lưu vào ChromaDB!")

embedding()
