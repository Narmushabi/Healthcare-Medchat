const API_URL = "http://127.0.0.1:5000";

// ✅ Send Message to Chatbot
document.getElementById("send-btn").addEventListener("click", async function () {
    const messageInput = document.getElementById("message-input");
    const chatBox = document.getElementById("chat-box");

    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    // Display user message
    chatBox.innerHTML += `<div class="message user-message">${userMessage}</div>`;
    messageInput.value = "";

    // Fetch AI response from backend
    const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
    });

    const data = await response.json();
    chatBox.innerHTML += `<div class="message bot-message">${data.response}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll
});

// ✅ Document Upload
document.getElementById("upload-btn").addEventListener("click", async function () {
    const fileInput = document.getElementById("document-upload");
    const uploadStatus = document.getElementById("upload-status");

    if (!fileInput.files.length) {
        uploadStatus.textContent = "Please select a file!";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("document", file);

    const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    uploadStatus.textContent = data.message;
});
