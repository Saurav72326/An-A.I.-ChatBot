import os

from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename

from agent import build_agent
from rag import build_retriever
from config import PDF_PATH


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


_agent = None


def get_agent():

    global _agent

    if _agent is None:

        if PDF_PATH:
            build_retriever()

        _agent = build_agent()

    return _agent


CHAT_PAGE = """
YOUR COMPLETE HTML CODE HERE
"""


@app.route("/")
def index():

    return render_template_string(CHAT_PAGE)


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:

        return jsonify({
            "error": "No file selected."
        }), 400


    file = request.files["file"]


    if file.filename == "":

        return jsonify({
            "error": "No file selected."
        }), 400


    filename = secure_filename(file.filename)


    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )


    file.save(file_path)


    return jsonify({
        "message": f"{filename} uploaded successfully.",
        "filename": filename
    })


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
