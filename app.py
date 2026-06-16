from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import json
import os
import sys

# Force UTF-8 stdout/stderr so emojis don't crash on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from IBrasileiraoRepository import LocalJsonRepository
from learningModel.HuggingFaceFallback import HuggingFaceFallback
from Orchestrator import ChatbotOrchestrator

load_dotenv(os.path.join(os.path.dirname(__file__), "src", ".env"), override=True)


def criar_bot():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "src", "dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    repository = LocalJsonRepository(data)

    token = os.getenv("HF_TOKEN")
    fallback = None
    if token:
        fallback = HuggingFaceFallback(token=token)
    else:
        print("Aviso: HF_TOKEN não encontrado no src/.env — o fallback LLM ficará desativado.")

    return ChatbotOrchestrator(repository, fallback=fallback)


def modo_cli(bot):
    print("--- Bem-vindo ao BrasileirãoBot (Beta) ---")
    print("Digite 'sair' para encerrar.\n")
    while True:
        user_input = input("Você: ")
        if user_input.lower() in ["sair", "exit", "quit"]:
            break
        resposta = bot.handle_message(user_input)
        tags = {"local": " [BASE]", "llm": " [LLM]"}
        tag = tags.get(resposta["source"], "")
        print(f"Bot{tag}: {resposta['text']}\n")


def modo_web(bot):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(base_dir, "src", "static")

    app = Flask(__name__, static_folder=static_path)

    @app.route("/")
    def index():
        return send_from_directory(static_path, "index.html")

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        mensagem = (data.get("mensagem", "") or "").strip()
        if not mensagem:
            return jsonify({"resposta": "Mensagem vazia.", "source": "local"}), 400
        resposta = bot.handle_message(mensagem)
        return jsonify({
            "resposta": resposta["text"],
            "source": resposta["source"],
        })

    app.run(debug=True, port=5000)


if __name__ == "__main__":
    bot = criar_bot()
    if "--web" in sys.argv:
        modo_web(bot)
    else:
        modo_cli(bot)
