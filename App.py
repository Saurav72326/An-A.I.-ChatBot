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
    height: 100vh;

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

    display: flex;
    flex-direction: column;

    overflow: hidden;

    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
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

}


.header-text h2 {
    font-size: 22px;
}


.header-text p {

    font-size: 13px;

    margin-top: 4px;

    opacity: 0.8;

}


.status {

    margin-left: auto;

    background: rgba(255,255,255,0.2);

    padding: 8px 14px;

    border-radius: 20px;

    font-size: 13px;

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

    margin-top: 100px;

    color: #64748b;

}


.welcome h2 {

    color: #1e293b;

    margin-bottom: 10px;

}


/* MESSAGE */

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

    border: 1px solid #e2e8f0;

    color: #1e293b;

    border-bottom-left-radius: 5px;

}


/* FILE PREVIEW */

.file-preview {

    display: none;

    align-items: center;

    gap: 10px;

    margin: 0 20px 10px;

    padding: 10px 15px;

    background: #eef2ff;

    border-radius: 10px;

    color: #3730a3;

}


.remove-file {

    margin-left: auto;

    cursor: pointer;

    font-size: 20px;

}


/* INPUT AREA */

.input-area {

    padding: 15px 20px;

    background: white;

    border-top: 1px solid #e2e8f0;

}


.input-wrapper {

    display: flex;

    align-items: center;

    gap: 10px;

}


.upload-btn {

    width: 50px;

    height: 50px;

    border: none;

    border-radius: 12px;

    background: #eef2ff;

    color: #4f46e5;

    font-size: 24px;

    cursor: pointer;

}


.input-wrapper input[type="text"] {

    flex: 1;

    padding: 15px;

    border: 1px solid #cbd5e1;

    border-radius: 12px;

    outline: none;

    font-size: 15px;

}


.input-wrapper input[type="text"]:focus {

    border-color: #4f46e5;

}


.send-btn {

    border: none;

    background: linear-gradient(135deg, #4f46e5, #7c3aed);

    color: white;

    padding: 15px 25px;

    border-radius: 12px;

    cursor: pointer;

    font-size: 15px;

}


.send-btn:disabled {

    opacity: 0.6;

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
Upload a document or ask me anything.
</p>

</div>

</div>



<div class="file-preview" id="filePreview">

<span>📄</span>

<span id="fileName"></span>

<span class="remove-file" onclick="removeFile()">×</span>

</div>



<div class="input-area">


<div class="input-wrapper">


<button class="upload-btn" onclick="document.getElementById('fileInput').click()">

📎

</button>


<input

type="file"

id="fileInput"

accept=".pdf,.txt,.doc,.docx"

style="display:none"

onchange="handleFile()"

>


<input

type="text"

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


</div>



<script>


const input = document.getElementById("msg");


input.addEventListener("keypress", function(event) {

    if (event.key === "Enter") {

        send();

    }

});


function handleFile() {

    const file = document.getElementById("fileInput").files[0];

    if (!file) return;


    document.getElementById("filePreview").style.display = "flex";

    document.getElementById("fileName").textContent = file.name;

}


function removeFile() {

    document.getElementById("fileInput").value = "";

    document.getElementById("filePreview").style.display = "none";

}


async function send() {


    const text = input.value.trim();


    if (!text) return;


    const welcome = document.getElementById("welcome");


    if (welcome) {

        welcome.remove();

    }


    log(text, "user");


    input.value = "";


    const button = document.getElementById("sendBtn");


    button.disabled = true;

    button.innerText = "Thinking...";


    try {


        const res = await fetch("/chat", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                message: text,

                user_id: 1

            })

        });


        const data = await res.json();


        if (data.reply) {

            log(data.reply, "bot");

        }

        else {

            log("Sorry, something went wrong.", "bot");

        }


    }

    catch(error) {

        log("⚠️ Unable to connect to the chatbot server.", "bot");

    }


    button.disabled = false;

    button.innerText = "Send ➤";


}


function log(text, who) {


    const chatBox = document.getElementById("log");


    const message = document.createElement("div");


    message.className = "message " + who;


    const bubble = document.createElement("div");


    bubble.className = "bubble";


    bubble.textContent = text;


    message.appendChild(bubble);


    chatBox.appendChild(message);


    chatBox.scrollTop = chatBox.scrollHeight;


}


</script>


</body>

</html>
"""


@app.route("/")
def index():
    return render_template_string(CHAT_PAGE)


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(force=True)

        prompt = (data.get("message") or "").strip()

        if not prompt:
            return jsonify({"reply": "Please enter a message."}), 400

        agent = get_agent()

        response = agent.invoke({
            "messages": [
                ("user", prompt)
            ]
        })

        reply = response["messages"][-1].content

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

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
