from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from AI.AI_QA import MovieChatbot

app = Flask(__name__)
CORS(app)

chatbot = MovieChatbot()
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "Câu hỏi không hợp lệ"}), 400
    
    movies = chatbot.search_movie(query)
    reply = chatbot.generate_response(query, movies) if movies else "Xin lỗi, mình không tìm thấy phim nào phù hợp."
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
