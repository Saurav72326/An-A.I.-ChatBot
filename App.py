import os

from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename

from agent import build_agent
from rag import build_retriever


# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)

# Maximum upload size: 20 MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

# Folder for uploaded PDFs
UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================
# GLOBAL AGENT
# ==========================================

_agent = None


def get_agent():
    global _agent

    if _agent is None:
        _agent = build_agent()

    return _agent


# ==========================================
# HTML PAGE
# ==========================================

CHAT_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AI Chatbot</title>

<style>

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #111827, #1e293b);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.chat-container {
    width: 900px;
    max-width: 95%;
    height: 85vh;
    background: white;
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}

/* HEADER */

.chat-header {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 22px 30px;
    display: flex;
    align-items: center;
    gap: 15px;
}

.bot-icon {
    width: 50px;
    height: 50px;
    background: white;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 25px;
}

.header-text h2 {
    font-size: 24px;
}

.header-text p {
    font-size: 14px;
    opacity: 0.8;
    margin-top: 4px;
}

.status {
    margin-left: auto;
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 15px;
    border-radius: 20px;
}

/* CHAT AREA */

.chat-box {
    flex: 1;
    padding: 25px;
    overflow-y: auto;
    background: #f8fafc;
}

/* WELCOME */

.welcome {
    text-align: center;
    margin-top: 80px;
    color: #64748b;
}

.welcome h2 {
    color: #1e293b;
    margin-bottom: 10px;
}

/* MESSAGES */

.message {
    display: flex;
    margin-bottom: 18px;
}

.message.user {
    justify-content: flex-end;
}

.message.bot {
    justify-content: flex-start;
}

.bubble {
    max-width: 70%;
    padding: 14px 18px;
    border-radius: 18px;
    font-size: 16px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.user .bubble {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    border-bottom-right-radius: 5px;
}

.bot .bubble {
    background: white;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-bottom-left-radius: 5px;
}

/* UPLOAD AREA */

.upload-area {
    padding: 10px 20px;
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
}

.upload-label {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 15px;
    background: #eef2ff;
    border-radius: 12px;
    cursor: pointer;
    color: #4f46e5;
    font-weight: bold;
}

.upload-label:hover {
    background: #e0e7ff;
}

#fileInput {
    display: none;
}

.file-name {
    margin-top: 8px;
    font-size: 14px;
    color: #475569;
}

/* INPUT AREA */

.input-area {
    padding: 20px;
    background: white;
    border-top: 1px solid #e2e8f0;
    display: flex;
    gap: 12px;
}

.input-area input {
    flex: 1;
    padding: 15px 18px;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    outline: none;
    font-size: 16px;
}

.input-area input:focus {
    border-color: #4f46e5;
}

.send-btn {
    border: none;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 0 25px;
    border-radius: 12px;
    font-size: 16px;
    cursor: pointer;
}

.send-btn:hover {
    opacity: 0.9;
}

.send-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

@media (max-width: 600px) {

    .chat-container {
        width: 100%;
        max-width: 100%;
        height: 100vh;
        border-radius: 0;
    }

    .bubble {
        max-width: 85%;
    }

    .status {
        display: none;
    }

}

</style>

</head>


<body>

<div class="chat-container">

    <!-- HEADER -->

    <div class="chat-header">

        <div class="bot-icon">
            🤖
        </div>

        <div class="header-text">
            <h2>AI Chatbot</h2>
            <p>Powered by Gemini AI</p>
        </div>

        <div class="status">
            ● Online
        </div>

    </div>


    <!-- CHAT BOX -->

    <div class="chat-box" id="log">

        <div class="welcome" id="welcome">

            <h2>Hello! 👋</h2>

            <p>
                Upload a PDF or ask me anything.
            </p>

        </div>

    </div>


    <!-- PDF UPLOAD -->

    <div class="upload-area">

        <label for="fileInput" class="upload-label">

            📎 Upload PDF

        </label>

        <input
            type="file"
            id="fileInput"
            accept=".pdf"
        >

        <div
            class="file-name"
            id="fileName"
        ></div>

    </div>


    <!-- MESSAGE INPUT -->

    <div class="input-area">

        <input
            id="msg"
            placeholder="Ask anything..."
            autocomplete="off"
        >

        <button
            class="send-btn"
            id="sendBtn"
            onclick="send()"
        >
            Send ➤
        </button>

    </div>

</div>


<script>

const input = document.getElementById("msg");
const fileInput = document.getElementById("fileInput");
const sendButton = document.getElementById("sendBtn");


/* ======================================
   ENTER KEY
====================================== */

input.addEventListener("keypress", function(event) {

    if (event.key === "Enter") {
        send();
    }

});


/* ======================================
   PDF UPLOAD
====================================== */

fileInput.addEventListener("change", async function() {

    const file = fileInput.files[0];

    if (!file) {
        return;
    }


    const fileName = document.getElementById("fileName");

    fileName.innerText = "⏳ Uploading " + file.name + "...";


    const formData = new FormData();

    formData.append("file", file);


    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });


        const data = await response.json();


        if (response.ok) {

            fileName.innerText =
                "✅ PDF Ready: " + data.filename;

            removeWelcome();

            log(
                "📄 PDF uploaded successfully! You can now ask questions about this document.",
                "bot"
            );

        } else {

            fileName.innerText =
                "❌ Upload failed: " +
                (data.error || "Unknown error");

        }

    } catch (error) {

        console.error(error);

        fileName.innerText =
            "❌ Unable to upload PDF.";

    }

});


/* ======================================
   SEND MESSAGE
====================================== */

async function send() {

    const text = input.value.trim();

    if (!text) {
        return;
    }


    removeWelcome();


    log(text, "user");


    input.value = "";


    sendButton.disabled = true;

    sendButton.innerText = "Thinking...";


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: text
            })

        });


        const data = await response.json();


        if (data.reply) {

            log(data.reply, "bot");

        } else {

            log(
                data.error || "Something went wrong.",
                "bot"
            );

        }

    } catch (error) {

        console.error(error);

        log(
            "⚠️ Unable to connect to the chatbot server.",
            "bot"
        );

    }


    sendButton.disabled = false;

    sendButton.innerText = "Send ➤";

    input.focus();

}


/* ======================================
   REMOVE WELCOME
====================================== */

function removeWelcome() {

    const welcome =
        document.getElementById("welcome");

    if (welcome) {
        welcome.remove();
    }

}


/* ======================================
   DISPLAY MESSAGE
====================================== */

function log(text, who) {

    const chatBox =
        document.getElementById("log");


    const message =
        document.createElement("div");


    message.className =
        "message " + who;


    const bubble =
        document.createElement("div");


    bubble.className =
        "bubble";


    bubble.textContent =
        text;


    message.appendChild(bubble);

    chatBox.appendChild(message);


    chatBox.scrollTop =
        chatBox.scrollHeight;

}

</script>

</body>

</html>
"""


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def index():

    return render_template_string(CHAT_PAGE)


# ==========================================
# PDF UPLOAD
# ==========================================

@app.route("/upload", methods=["POST"])
def upload():

    try:

        if "file" not in request.files:
            return jsonify({
                "error": "No file selected."
            }), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({
                "error": "No file selected."
            }), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({
                "error": "Only PDF files are allowed."
            }), 400

        upload_folder = "uploads"

        os.makedirs(upload_folder, exist_ok=True)

        pdf_path = os.path.join(
            upload_folder,
            file.filename
        )

        file.save(pdf_path)

        print("PDF saved:", pdf_path)

        retriever = build_retriever(pdf_path)

        if retriever is None:
            return jsonify({
                "error": "Could not process the PDF."
            }), 500

        return jsonify({
            "success": True,
            "message": "PDF uploaded successfully!"
        })

    except Exception as e:

        error_message = str(e)

        print("UPLOAD ERROR:", repr(e))

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

            return jsonify({
                "error": (
                    "Gemini API quota exceeded. "
                    "Please wait a few seconds and upload again."
                )
            }), 429

        return jsonify({
            "error": f"Upload failed: {error_message}"
        }), 500


# ==========================================
# CHAT ROUTE
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)

        prompt = (data.get("message") or "").strip()

        if not prompt:
            return jsonify({
                "reply": "Please enter a message."
            }), 400

        agent = get_agent()

        response = agent.invoke({
            "messages": [
                ("user", prompt)
            ]
        })

        messages = response.get("messages", [])

        if not messages:
            return jsonify({
                "reply": "The AI did not return a response. Please try again."
            }), 500

        last_message = messages[-1]

        reply = getattr(last_message, "content", "")

        if isinstance(reply, list):
            reply = "".join(
                item.get("text", "")
                for item in reply
                if isinstance(item, dict)
            )

        if not reply:
            reply = "No response was generated. Please try again."

        return jsonify({
            "reply": str(reply)
        })

    except Exception as e:

        error_message = str(e)

        print("CHAT ERROR:", repr(e))

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

            return jsonify({
                "reply": (
                    "⚠️ Gemini API quota has been reached. "
                    "Please wait a few seconds and try again."
                )
            }), 429

        return jsonify({
            "reply": f"Server error: {error_message}"
        }), 500

# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
    )
    
