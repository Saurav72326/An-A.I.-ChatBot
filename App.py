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
<!doctype html>
<html>
<head>
    <title>AI Chatbot</title>
</head>

<body>

<h2>AI Chatbot</h2>

<div id="log"></div>

<input
    id="msg"
    placeholder="Type a message..."
/>

<button onclick="send()">Send</button>


<script>

async function send() {

    const input = document.getElementById('msg');

    const text = input.value.trim();

    if (!text) return;

    log(text, 'You');

    input.value = '';

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

        if (!res.ok) {

            log(
                data.reply || 'Something went wrong.',
                'Bot'
            );

            return;
        }

        log(data.reply, 'Bot');

    }

    catch (error) {

        console.error(error);

        log(
            '⚠️ Unable to connect to the chatbot server.',
            'Bot'
        );
    }

}


function log(text, who) {

    const div = document.getElementById('log');

    div.innerHTML +=
        '<p><b>' +
        who +
        ':</b> ' +
        text +
        '</p>';

    div.scrollTop = div.scrollHeight;

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

        prompt = (
            data.get("message") or ""
        ).strip()


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
