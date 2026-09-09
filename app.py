from flask import Flask, request, jsonify
import os
import json
import urllib.request
import urllib.error

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-3-flash-preview"

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AK AI Tools</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: white;
}

.header {
    padding: 20px;
    text-align: center;
    background: #111827;
    border-bottom: 1px solid #334155;
}

.header h1 {
    margin: 0;
    font-size: 28px;
}

.header p {
    color: #94a3b8;
}

.container {
    max-width: 750px;
    margin: 20px auto;
    padding: 15px;
}

.tools {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 15px;
}

.tool {
    padding: 13px;
    border: 1px solid #334155;
    border-radius: 12px;
    background: #1e293b;
    color: white;
    cursor: pointer;
}

.tool:hover {
    background: #334155;
}

.chat {
    background: #111827;
    border-radius: 18px;
    padding: 15px;
    min-height: 400px;
}

.messages {
    min-height: 300px;
    max-height: 500px;
    overflow-y: auto;
}

.msg {
    padding: 12px;
    margin: 10px 0;
    border-radius: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
}

.user {
    background: #2563eb;
    margin-left: 20%;
}

.ai {
    background: #1e293b;
    margin-right: 10%;
}

.input-area {
    display: flex;
    gap: 8px;
    margin-top: 15px;
}

textarea {
    flex: 1;
    resize: none;
)
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #475569;
    background: #0f172a;
    color: white;
    font-size: 16px;
}

button {
    border: none;
    border-radius: 12px;
    padding: 12px 18px;
    cursor: pointer;
    font-size: 15px;
}

.send {
    background: #22c55e;
    color: white;
}

.clear {
    margin-top: 10px;
    background: #ef4444;
    color: white;
}

#status {
    text-align: center;
    color: #94a3b8;
    margin: 10px;
}

@media(max-width:600px) {
    .tools {
        grid-template-columns: 1fr 1fr 1fr;
    }

    .user {
        margin-left: 5%;
    }

    .ai {
        margin-right: 5%;
    }
}
</style>
</head>

<body>

<div class="header">
    <h1>🤖 AK AI Tools</h1>
    <p>Your Smart AI Assistant</p>
</div>

<div class="container">

<div class="tools">
    <button class="tool" onclick="setMode('chat')">💬 Chat</button>
    <button class="tool" onclick="setMode('writer')">✍️ Writer</button>
    <button class="tool" onclick="setMode('translate')">🌐 Translate</button>
</div>

<div class="chat">

<div id="messages" class="messages">
    <div class="msg ai">
        नमस्ते! 👋 मैं AK AI हूँ।<br>
        आप मुझसे कुछ भी पूछ सकते हैं।
    </div>
</div>

<div id="status"></div>

<div class="input-area">
    <textarea id="question"
    placeholder="यहाँ अपना सवाल लिखें..."></textarea>

    <button class="send" onclick="askAI()">Send</button>
</div>

<button class="clear" onclick="clearChat()">🗑️ Clear Chat</button>

</div>
</div>

<script>

let mode = "chat";

function setMode(newMode) {
    mode = newMode;

    let box = document.getElementById("question");

    if (mode === "writer") {
        box.placeholder = "क्या लिखवाना चाहते हैं? जैसे: YouTube article...";
    }

    if (mode === "translate") {
        box.placeholder = "Text लिखें जिसे translate करना है...";
    }

    if (mode === "chat") {
        box.placeholder = "यहाँ अपना सवाल लिखें...";
    }
}

function addMessage(text, type) {
    let messages = document.getElementById("messages");

    let div = document.createElement("div");
    div.className = "msg " + type;
    div.textContent = text;

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

async function askAI() {

    let input = document.getElementById("question");
    let question = input.value.trim();

    if (!question) {
        return;
    }

    addMessage(question, "user");
    input.value = "";

    document.getElementById("status").textContent =
        "🤔 AI सोच रहा है...";

    try {

        let response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: question,
                mode: mode
            })
        });

        let data = await response.json();

        if (data.reply) {
            addMessage(data.reply, "ai");
        } else {
            addMessage("❌ " + (data.error || "कुछ गलती हुई"), "ai");
        }

    } catch (error) {

        addMessage(
            "❌ Server से connection नहीं हो पाया।",
            "ai"
        );

    }

    document.getElementById("status").textContent = "";
}

function clearChat() {
    document.getElementById("messages").innerHTML =
        '<div class="msg ai">Chat साफ कर दी गई है। 👋</div>';
}

document.getElementById("question").addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            askAI();
        }

    }
);

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return HTML


@app.route("/api/chat", methods=["POST"])
def chat():

    if not API_KEY:
        return jsonify({
            "error": "GEMINI_API_KEY सेट नहीं है।"
        }), 500

    data = request.get_json() or {}

    message = data.get("message", "").strip()
    mode = data.get("mode", "chat")

    if not message:
        return jsonify({
            "error": "Message खाली है।"
        }), 400

    if mode == "writer":
        prompt = (
            "You are a professional AI writer. "
            "Write clear, useful and engaging content. "
            "User request: " + message
        )

    elif mode == "translate":
        prompt = (
            "Translate the following text accurately. "
            "If the text is Hindi, translate to English. "
            "If English, translate to Hindi. "
            "Text: " + message
        )

    else:
        prompt = (
            "You are AK AI, a helpful AI assistant. "
            "Answer clearly and naturally. "
            "Prefer Hindi when the user writes Hindi. "
            "User: " + message
        )

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/" + MODEL + ":generateContent"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(req, timeout=60) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        reply = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({
            "reply": reply
        })

    except urllib.error.HTTPError as e:

        error_text = e.read().decode("utf-8")

        return jsonify({
            "error": "Gemini API error: " + error_text
        }), 500

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
)

