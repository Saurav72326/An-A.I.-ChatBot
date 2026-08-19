import os
from werkzeug.utils import secure_filename

from flask import (
    Flask,
    request,
    jsonify,
    render_template_string
)

from agent import build_agent
from rag import build_retriever


app = Flask(__name__)


# Folder where uploaded PDFs will be stored
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


_agent = None


def get_agent():

    global _agent

    if _agent is None:
        _agent = build_agent()

    return _agent


# -------------------------------
# HTML PAGE
# -------------------------------

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
}

.chat-header {

    background: linear-gradient(
        135deg,
        #4f46e5,
        #7c3aed
    );

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
    font-size: 22px;
}

.header-text p {
    opacity: 0.8;
    margin-top: 5px;
}

.status {

    margin-left: auto;

    background: rgba(255,255,255,0.2);

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
}

.user .bubble {

    background: linear-gradient(
        135deg,
        #4f46e5,
        #7c3aed
    );

    color: white;
}

.bot .bubble {

    background: white;

    border: 1px solid #e2e8f0;

    color: #1e293b;
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

    padding: 12px;

    background: #eef2ff;

    border-radius: 10px;

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

    font-size: 15px;
}

.send-btn {

    border: none;

    background: linear-gradient(
        135deg,
        #4f46e5,
        #7c3aed
    );

    color: white;

    padding: 0 25px;

    border-radius: 12px;

    font-size: 16px;

    cursor: pointer;
}

.send-btn:disabled {

    opacity: 0.6;

    cursor: not-allowed;
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


<!-- CHAT -->

<div class="chat-box" id="log">

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
>
</div>

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


const input =
document.getElementById("msg");


const fileInput =
document.getElementById("fileInput");


// -------------------------
// UPLOAD PDF
// -------------------------

fileInput.addEventListener(
    "change",
    async function() {

        const file =
        fileInput.files[0];

        if (!file) return;


        document.getElementById(
            "fileName"
        ).innerText =
        "Uploading: " + file.name;


        const formData =
        new FormData();


        formData.append(
            "file",
            file
        );


        try {

            const response =
            await fetch(
                "/upload",
                {
                    method: "POST",
                    body: formData
                }
            );


            const data =
            await response.json();


            if (response.ok) {

                document.getElementById(
                    "fileName"
                ).innerText =
                "✅ PDF Ready: " +
                data.filename;


                log(
                    "📄 PDF uploaded successfully. You can now ask questions about it.",
                    "bot"
                );

            }

            else {

                document.getElementById(
                    "fileName"
                ).innerText =
                "❌ Upload failed";

            }

        }

        catch (error) {

            document.getElementById(
                "fileName"
            ).innerText =
            "❌ Unable to upload PDF";

        }

    }
);


// -------------------------
// SEND MESSAGE
// -------------------------

input.addEventListener(
    "keypress",
    function(event) {

        if (
            event.key === "Enter"
        ) {

            send();

        }

    }
);


async function send() {

    const text =
    input.value.trim();


    if (!text) return;


    log(
        text,
        "user"
    );


    input.value = "";


    const button =
    document.getElementById(
        "sendBtn"
    );


    button.disabled = true;

    button.innerText =
    "Thinking...";


    try {

        const response =
        await fetch(
            "/chat",
            {

                method: "POST",

                headers: {

                    "Content-Type":
                    "application/json"

                },

                body:
                JSON.stringify({

                    message: text

                })

            }
        );


        const data =
        await response.json();


        log(
            data.reply ||
            "Something went wrong.",
            "bot"
        );

    }

    catch (error) {

        log(
            "⚠️ Unable to connect to server.",
            "bot"
        );

    }


    button.disabled = false;

    button.innerText =
    "Send ➤";

}


function log(
    text,
    who
) {

    const chatBox =
    document.getElementById(
        "log"
    );


    const message =
    document.createElement(
        "div"
    );


    message.className =
    "message " + who;


    const bubble =
    document.createElement(
        "div"
    );


    bubble.className =
    "bubble";


    bubble.textContent =
    text;


    message.appendChild(
        bubble
    );


    chatBox.appendChild(
        message
    );


    chatBox.scrollTop =
    chatBox.scrollHeight;

}


</script>


</body>

</html>
"""


# -------------------------------
# HOME PAGE
# -------------------------------

@app.route("/")
def index():

    return render_template_string(
        CHAT_PAGE
    )


# -------------------------------
# PDF UPLOAD
# -------------------------------

@app.route(
    "/upload",
    methods=["POST"]
)

def upload_pdf():

    if "file" not in request.files:

        return jsonify({

            "error":
            "No file uploaded"

        }), 400


    file =
    request.files["file"]


    if file.filename == "":

        return jsonify({

            "error":
            "No file selected"

        }), 400


    if not file.filename.lower().endswith(
        ".pdf"
    ):

        return jsonify({

            "error":
            "Only PDF files are allowed"

        }), 400


    filename =
    secure_filename(
        file.filename
    )


    pdf_path =
    os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )


    # Save uploaded PDF
    file.save(
        pdf_path
    )


    try:

        # Process PDF and create retriever
        retriever =
        build_retriever(
            pdf_path
        )


        if retriever is None:

            return jsonify({

                "error":
                "Could not process PDF"

            }), 500


        return jsonify({

            "message":
            "PDF uploaded successfully",

            "filename":
            filename

        })


    except Exception as e:

        print(
            "PDF UPLOAD ERROR:",
            repr(e)
        )


        return jsonify({

            "error":
            str(e)

        }), 500


# -------------------------------
# CHAT
# -------------------------------

@app.route(
    "/chat",
    methods=["POST"]
)

def chat():

    try:

        data =
        request.get_json(
            force=True
        )


        prompt =
        (
            data.get("message")
            or ""
        ).strip()


        if not prompt:

            return jsonify({

                "reply":
                "Please enter a message."

            }), 400


        agent =
        get_agent()


        response =
        agent.invoke({

            "messages": [

                (
                    "user",
                    prompt
                )

            ]

        })


        reply =
        response["messages"][-1].content


        # Fix Gemini list response
        if isinstance(
            reply,
            list
        ):

            reply =
            "".join(

                item.get(
                    "text",
                    ""
                )

                for item in reply

                if isinstance(
                    item,
                    dict
                )

            )


        return jsonify({

            "reply":
            str(reply)

        })


    except Exception as e:

        print(
            "CHAT ERROR:",
            repr(e)
        )


        return jsonify({

            "reply":
            "Server error: " +
            str(e)

        }), 500


# -------------------------------
# HEALTH CHECK
# -------------------------------

@app.route("/health")
def health():

    return jsonify({

        "status":
        "ok"

    })


# -------------------------------
# RUN APPLICATION
# -------------------------------

if __name__ == "__main__":

    port =
    int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(

        host="0.0.0.0",

        port=port

    )
