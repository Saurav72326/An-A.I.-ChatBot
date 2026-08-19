import os

from flask import Flask, request, jsonify, render_template_string

from agent import build_agent
from rag import build_retriever
from config import PDF_PATH


app = Flask(__name__)
_agent = None


def get_agent():
    global _agent

    if _agent is None:
        if PDF_PATH:
            build_retriever()

        _agent = build_agent()

    return _agent


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
    background: #ffffff;
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0,0,0,0.35);
}

/* HEADER */

.chat-header {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 20px 30px;
    display: flex;
    align-items: center;
    gap: 15px;
}

.bot-icon {
    width: 50px;
    height: 50px;
    background: white;
    color: #4f46e5;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 25px;
    flex-shrink: 0;
}

.header-text h2 {
    font-size: 22px;
}

.header-text p {
    font-size: 13px;
    opacity: 0.9;
    margin-top: 4px;
}

.status {
    margin-left: auto;
    font-size: 13px;
    background: rgba(255,255,255,0.2);
    padding: 8px 14px;
    border-radius: 20px;
    white-space: nowrap;
}

/* CHAT AREA */

.chat-box {
    flex: 1;
    padding: 25px;
    overflow-y: auto;
    background: #f8fafc;
}

/* WELCOME MESSAGE */

.welcome {
    text-align: center;
    margin-top: 60px;
    color: #64748b;
}

.welcome h2 {
    color: #1e293b;
    margin-bottom: 10px;
    font-size: 28px;
}

.welcome p {
    font-size: 15px;
    line-height: 1.6;
}

/* PDF DOCUMENT NOTICE */

.document-notice {
    max-width: 500px;
    margin: 30px auto;
    padding: 16px 20px;
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    border-radius: 14px;
    color: #3730a3;
    font-size: 15px;
    line-height: 1.5;
}

.document-notice .icon {
    font-size: 25px;
    margin-bottom: 8px;
}

.document-notice b {
    color: #4f46e5;
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
    font-size: 15px;
    line-height: 1.5;
    word-wrap: break-word;
    white-space: pre-wrap;
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

/* TYPING INDICATOR */

.typing {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 18px;
}

.typing-bubble {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 14px 18px;
    border-radius: 18px;
    border-bottom-left-radius: 5px;
    color: #64748b;
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
    font-size: 15px;
}

.input-area input:focus {
    border-color: #4f46e5;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1);
}

.send-btn {
    border: none;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 0 25px;
    border-radius: 12px;
    font-size: 15px;
    cursor: pointer;
    transition: 0.2s;
}

.send-btn:hover {
    transform: scale(1.04);
}

.send-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* MOBILE */

@media(max-width: 600px) {

    body {
        align-items: stretch;
    }

    .chat-container {
        height: 100vh;
        width: 100%;
        max-width: 100%;
        border-radius: 0;
    }

    .status {
        display: none;
    }

    .bubble {
        max-width: 85%;
    }

    .chat-header {
        padding: 16px;
    }

    .input-area {
        padding: 12px;
    }

    .send-btn {
        padding: 0 16px;
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


    <!-- CHAT AREA -->

    <div class="chat-box" id="log">

        <div class="welcome" id="welcome">

            <h2>Hello! 👋</h2>

            <p>
                I'm your AI assistant.<br>
                Ask me anything and I'll do my best to help.
            </p>

            <div class="document-notice">

                <div class="icon">
                    📄
                </div>

                <b>Document Question Answering</b>

                <br><br>

                Set <b>PDF_PATH</b> and ask a question answered
                within the document.

            </div>

        </div>

    </div>


    <!-- INPUT AREA -->

    <div class="input-area">

        <input
            id="msg"
            placeholder="Type your message..."
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

const input = document.getElementById('msg');


input.addEventListener('keypress', function(event) {

    if (event.key === 'Enter') {

        send();

    }

});


async function send() {

    const text = input.value.trim();

    if (!text) return;


    const welcome = document.getElementById('welcome');

    if (welcome) {

        welcome.remove();

    }


    log(text, 'user');

    input.value = '';


    const button = document.getElementById('sendBtn');

    button.disabled = true;

    button.innerText = 'Thinking...';


    showTyping();


    try {

        const res = await fetch('/chat', {

            method: 'POST',

            headers: {

                'Content-Type': 'application/json'

            },

            body: JSON.stringify({

                message: text,

                user_id: 1

            })

        });


        const data = await res.json();


        removeTyping();


        if (data.reply) {

            log(data.reply, 'bot');

        } else {

            log(

                data.error || 'Sorry, something went wrong.',

                'bot'

            );

        }


    } catch (error) {

        removeTyping();

        log(

            '⚠️ Unable to connect to the chatbot server.',

            'bot'

        );

    }


    button.disabled = false;

    button.innerText = 'Send ➤';

    input.focus();

}


/* ADD MESSAGE */

function log(text, who) {

    const chatBox = document.getElementById('log');


    const message = document.createElement('div');

    message.className = 'message ' + who;


    const bubble = document.createElement('div');

    bubble.className = 'bubble';


    bubble.textContent = text;


    message.appendChild(bubble);

    chatBox.appendChild(message);


    chatBox.scrollTop = chatBox.scrollHeight;

}


/* SHOW THINKING MESSAGE */

function showTyping() {

    const chatBox = document.getElementById('log');


    const typing = document.createElement('div');

    typing.className = 'typing';

    typing.id = 'typing';


    const bubble = document.createElement('div');

    bubble.className = 'typing-bubble';

    bubble.textContent = '🤖 Thinking...';


    typing.appendChild(bubble);

    chatBox.appendChild(typing);


    chatBox.scrollTop = chatBox.scrollHeight;

}


/* REMOVE THINKING MESSAGE */

function removeTyping() {

    const typing = document.getElementById('typing');

    if (typing) {

        typing.remove();

    }

}

</script>

</body>

</html>"""


@app.route("/")
def index():
    return render_template_string(CHAT_PAGE)


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

        reply = response["messages"][-1].content

        # Fix Gemini response format
        if isinstance(reply, list):
            reply = "".join(
                item.get("text", "")
                for item in reply
                if isinstance(item, dict)
            )

        return jsonify({
            "reply": str(reply)
        })

    except Exception as e:
        print("CHAT ERROR:", repr(e))

        return jsonify({
            "reply": f"Server error: {str(e)}"
        }), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })
