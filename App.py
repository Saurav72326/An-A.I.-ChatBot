import os

from flask import Flask, request, jsonify, render_template_string

from agent import build_agent
from memory import save_message, format_history
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
<head><title>AI Chatbot</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 40px auto;">
  <h2>AI Chatbot</h2>
  <div id="log" style="border:1px solid #ccc; padding:10px; height:400px; overflow-y:auto;"></div>
  <input id="msg" style="width:80%;" placeholder="Type a message..." />
  <button onclick="send()">Send</button>
  <script>
    async function send() {
      const input = document.getElementById('msg');
      const text = input.value.trim();
      if (!text) return;
      log(text, 'You');
      input.value = '';
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text, user_id: 1})
      });
      const data = await res.json();
      log(data.reply, 'Bot');
    }
    function log(text, who) {
      const div = document.getElementById('log');
      div.innerHTML += '<p><b>' + who + ':</b> ' + text + '</p>';
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
    data = request.get_json(force=True)
    prompt = (data.get("message") or "").strip()
    user_id = int(data.get("user_id", 1))

    if not prompt:
        return jsonify({"reply": "Please send a non-empty message."}), 400

    agent = get_agent()

    save_message(user_id, "user", prompt)
    history = format_history(user_id, limit=20)
    contextual_prompt = (
        f"Conversation so far:\n{history}\n\n"
        f"Respond to the latest user message above."
    )
    response = agent.invoke({"messages": [("user", contextual_prompt)]})
    reply = response["messages"][-1].content
    save_message(user_id, "assistant", reply)

    return jsonify({"reply": reply})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
