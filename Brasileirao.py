import random
import nltk
from nltk.chat.util import Chat, reflections


pares = [
    [
        r'Oi|Olá|E ai',
        ["Olá!","Como posso ajudar?", "Oi, como está?"]
    ],
    [
        r'Qual o maior time do mundo\?',
        ["O gigantesco VASCO DA GAMA!!!"]
    ],
    [
        r'quais times do brasileirao|times do brasileirao',
        ["Times do Brasileirão:\n"
            "Vasco\n"
            "Palmeiras\n"
            "São Paulo\n"
            "Corinthians\n"
            "Cuiabá\n"
            "Grêmio\n"
            "Internacional\n"
            "Atlético-MG\n"
            "Cruzeiro\n"
            "Botafogo\n"
            "Fluminense\n"
            "Athletico-PR\n"
            "Bahia\n"
            "Fortaleza\n"
            "Ceará\n"
            "Santos\n"
            "Goiás\n"
            "Coritiba\n"
            "Bragantino\n"
            "Flamengo"
        ]
    ],
    [
        r'(.*)',
        ["Desculpa, não tenho uma resposta pra essa pergunta.", "Pode reformular a pergunta?"]
    ],
]

# pares.extende([
#     [r'(.*)', ["Entendi. Diga-me mais.", "Pode me contar mais sobre isso?", "Interessante. Conte-me mais.."]]
# ])

reflexoes = {
    "eu" : "você",
    "meu" : "seu",
    "você" : "eu",
    "seu" : "meu",
    "eu sou" : "você é",
    "você é" : "eu sou",
    "você estava" : "eu estava",
    "eu estava" : "você estava",
}

chatbot = Chat(pares, reflections)

while True:
    user_input = input("Você:")
    if user_input.lower() == "sair":
        print("Chatbot:", response)
        break
    response = chatbot.respond(user_input)
    print("Chatbot:", response)