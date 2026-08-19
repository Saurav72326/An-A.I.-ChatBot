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
    padding: 22px 30px;
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
    font-size: 24px;
}

.header-text h2 {
    font-size: 22px;
}

.header-text p {
    font-size: 13px;
    opacity: 0.8;
    margin-top: 4px;
}

.status {
    margin-left: auto;
    font-size: 13px;
    background: rgba(255,255,255,0.2);
    padding: 8px 14px;
    border-radius: 20px;
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
    margin-top: 80px;
    color: #64748b;
}

.welcome h2 {
    color: #1e293b;
    margin-bottom: 10px;
}

.welcome p {
    font-size: 15px;
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
    transform: scale(1.05);
}

.send-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* MOBILE */

@media(max-width: 600px) {

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

}

</style>

</head>


<body>

<div class="chat-container">

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


    <div class="chat-box" id="log">

        <div class="welcome" id="welcome">

            <h2>Hello! 👋</h2>

            <p>
                I'm your AI assistant.<br>
                Ask me anything and I'll do my best to help.
            </p>

        </div>

    </div>


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


        if (data.reply) {

            log(data.reply, 'bot');

        } else {

            log(
                data.error || 'Sorry, something went wrong.',
                'bot'
            );

        }


    } catch (error) {

        log(
            '⚠️ Unable to connect to the chatbot server.',
            'bot'
        );

    }


    button.disabled = false;

    button.innerText = 'Send ➤';

    input.focus();

}


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

</script>

</body>

</html>
"""


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


if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
