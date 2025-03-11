const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");

function sendMessage() {
    let message = userInput.value.trim();
    if (message === "") return;

    appendMessage("Bạn", message, "user-message");

    fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: message })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage("Chatbot", data.response, "bot-message");
    })
    .catch(error => {
        appendMessage("Chatbot", "Lỗi kết nối đến server!", "bot-message");
    });

    userInput.value = "";
}

function appendMessage(sender, text, className) {
    let messageElement = document.createElement("p");
    messageElement.classList.add(className);
    messageElement.textContent = `${sender}: ${text}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
