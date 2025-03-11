import chromadb
import torch
import re
from transformers import AutoModel, AutoTokenizer, pipeline, GPT2LMHeadModel
from typing import List, Dict, Optional
import logging

# Cấu hình logger chỉ hiển thị cảnh báo và lỗi
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MovieChatbot:
    def __init__(self):
        self.embedding_model_name = "dangvantuan/vietnamese-embedding"
        self.gen_model_name = "NlpHUST/gpt2-vietnamese"

        try:
            self.embedding_tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_name)
            self.embedding_model = AutoModel.from_pretrained(self.embedding_model_name)

            self.gen_tokenizer = AutoTokenizer.from_pretrained(self.gen_model_name)
            self.gen_model = GPT2LMHeadModel.from_pretrained(self.gen_model_name)
            self.generator = pipeline("text-generation", model=self.gen_model, tokenizer=self.gen_tokenizer)

            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.client.get_or_create_collection("movies")

            if self.collection.count() == 0:
                logger.warning("Collection 'movies' trống! Hãy thêm dữ liệu trước khi sử dụng.")
        except Exception as e:
            logger.error(f"Khởi tạo thất bại: {str(e)}")
            raise

    def normalize_text(self, text: str) -> str:
        return re.sub(r"[^\w\s]", "", text).lower()

    def mean_pooling(self, model_output, attention_mask) -> torch.Tensor:
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)
        sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
        return sum_embeddings / sum_mask

    def search_movie(self, query: str, expected_genre: Optional[str] = None) -> Optional[List[Dict]]:
        try:
            query_normalized = self.normalize_text(query)

            encoded_input = self.embedding_tokenizer(
                query_normalized, 
                padding=True, 
                truncation=True, 
                return_tensors="pt"
            )

            with torch.no_grad():
                model_output = self.embedding_model(**encoded_input)

            query_embedding = self.mean_pooling(model_output, encoded_input["attention_mask"]).numpy()

            filter_condition = {"genre": {"$in": expected_genre}} if expected_genre else None

            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=5,  
                where=filter_condition if filter_condition else None
            )

            movies = results.get("metadatas", [])
            return movies[0] if movies and any(movies) else None
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm phim: {str(e)}")
            return None

    def generate_response(self, query: str, movies: List[Dict]) -> str:
        movie_list = "\n".join([f"- {m['title']} ({m['genre']}) - Lịch chiếu: {m['schedule']}" for m in movies])
        
        prompt = f"""
Người dùng hỏi: "{query}"
Danh sách phim gợi ý:
{movie_list}
"""

        try:
            response = self.generator(prompt, 
                                    max_new_tokens=150,  
                                    num_return_sequences=1, 
                                    do_sample=True, 
                                    temperature=0.8, 
                                    top_p=0.9)[0]["generated_text"]
            return response.strip()
        except Exception:
            return f"Mình tìm được phim rồi, nhưng đây là vài gợi ý nhé:\n{movie_list}"

    def print_all_movies(self):
        try:
            all_movies = self.collection.get(include=["metadatas"])
            for idx, metadata in enumerate(all_movies["metadatas"]):
                print(f"{idx+1}. {metadata}")
        except Exception as e:
            logger.error(f"Lỗi khi lấy dữ liệu từ ChromaDB: {str(e)}")

def main():
    try:
        chatbot = MovieChatbot()
        while True:
            query = input("Nhập câu hỏi (hoặc 'exit' để thoát): ").strip()
            if query.lower() == "exit":
                break
            if not query:
                print("Bạn chưa nhập gì cả, thử lại nhé!")
                continue

            movies = chatbot.search_movie(query)
            reply = chatbot.generate_response(query, movies) if movies else "Xin lỗi, mình không tìm thấy phim nào phù hợp."
            print(reply)
    except Exception as e:
        logger.error(f"Lỗi chương trình: {str(e)}")

if __name__ == "__main__":
    main()
