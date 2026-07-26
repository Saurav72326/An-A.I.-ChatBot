from agent import build_agent
from memory import save_message, format_history
from rag import build_retriever
from config import PDF_PATH


def run_agent(agent, prompt: str, user_id: int) -> str:
    save_message(user_id, "user", prompt)
    history = format_history(user_id, limit=20)

    contextual_prompt = (
        f"Conversation so far:\n{history}\n\n"
        f"Respond to the latest user message above."
    )

    response = agent.invoke({"messages": [("user", contextual_prompt)]})
    reply = response["messages"][-1].content

    save_message(user_id, "assistant", reply)
    return reply


def main():
    print("Starting chatbot...")

    if PDF_PATH:
        retriever = build_retriever()
        if retriever:
            print(f"Loaded and indexed document: {PDF_PATH}")
        else:
            print(f"Could not find PDF at '{PDF_PATH}' — continuing without it.")
    else:
        print("No PDF_PATH set in .env — document search tool will be unavailable.")

    agent = build_agent()

    print("\nChatbot ready. Type 'exit' to quit.\n")
    user_id = 1
    while True:
        prompt = input("You: ").strip()
        if prompt.lower() == "exit":
            print("Goodbye!")
            break
        if not prompt:
            continue
        reply = run_agent(agent, prompt, user_id)
        print(f"Bot: {reply}\n")


if __name__ == "__main__":
    main()
