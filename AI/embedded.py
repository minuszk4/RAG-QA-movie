import json
import chromadb
from sentence_transformers import SentenceTransformer
import logging

def embedding():
    logging.basicConfig(level=logging.INFO)
    
    try:
        with open("movies.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        logging.error(f"Lỗi khi đọc file JSON: {e}")
        return

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("movies")
    model = SentenceTransformer("dangvantuan/vietnamese-embedding")
    
    movie_details = [
        {
            "id": f"{movie['title']}_{day}",
            "text": f"Tiêu đề: {movie['title']} | Thể loại: {movie['genre']} | Mô tả: {movie['description']}",
            "metadata": {
                "day": day,
                "title": movie["title"],
                "genre": movie["genre"],
                "duration": movie["duration"],
                "schedule": movie["schedule"]
            }
        }
        for day, movies in data.items() 
        for movie in movies
    ]
    
    texts = [doc["text"] for doc in movie_details]
    
    embeddings = model.encode(texts, batch_size=32, convert_to_numpy=True)
    
    collection.add(
        ids=[doc["id"] for doc in movie_details],
        embeddings=embeddings.tolist(),
        metadatas=[doc["metadata"] for doc in movie_details]
    )

    logging.info("Đã tạo embeddings và lưu vào ChromaDB!")

if __name__ == "__main__":
    embedding()
