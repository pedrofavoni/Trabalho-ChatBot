import random
import nltk
from nltk.chat.util import Chat, reflections


pares = [
[
        r'Oi|Olá|E ai',
        [
            "Olá! Tudo bem? Qual time você torce?",
            "Oi! Como posso ajudar? Você acompanha o Brasileirão 2026?",
            "E aí! Tudo certo? Qual seu time no campeonato?"
        ]
    ],
    [
        r'Qual o maior time do mundo\?',
        ["É o bonde do MENGÃO SEM FREIO!!! Você torce para qual time?"]
    ],
    [
        r'Quais os times do brasileirao|Times do brasileirao',
        ["Times do Brasileirão:\n"
         "Vasco, Palmeiras, São Paulo, Corinthians, Cuiabá, Grêmio,\n"
         "Internacional, Atlético-MG, Cruzeiro, Botafogo,\n"
         "Fluminense, Athletico-PR, Bahia, Fortaleza,\n"
         "Ceará, Santos, Goiás, Coritiba, Bragantino, Flamengo.\n"
         "Qual desses é o seu time?"]
    ],
    [
        r'Quem lidera o brasileirao 2026\?',
        ["O Palmeiras está liderando o Brasileirão 2026. Você acha que ele vai manter a liderança?"]
    ],
    [
        r'Em que lugar esta o Flamengo\?',
        ["O Flamengo está em 3º lugar no Brasileirão 2026. Você acha que ele ainda pode ser campeão?"]
    ],
    [
        r'Em que lugar esta o Vasco\?',
        ["O Vasco está em 10º lugar. Você acha que ele consegue subir na tabela?"]
    ],
    [
        r'Qual o pior time do brasileirao 2026\?',
        ["Atualmente o lanterna é o Coritiba. Você acha que ele consegue escapar do rebaixamento?"]
    ],
    [
        r'Quem é o artilheiro do brasileirao 2026\?',
        ["O artilheiro é Pedro do Flamengo. Você acha que ele termina como artilheiro da temporada?"]
    ],
    [
        r'Qual o melhor ataque\?',
        ["O melhor ataque é do Palmeiras. Qual time você acha mais ofensivo?"]
    ],
    [
        r'Qual a melhor defesa\?',
        ["A melhor defesa é do Atlético-MG. Você prefere defesa sólida ou ataque forte?"]
    ],
    [
        r'Quem vai ser campeao\?',
        ["O Palmeiras é o favorito no momento. Qual é o seu palpite para campeão?"]
    ],
    [
        r'Quem vai cair\?',
        ["Coritiba, Goiás, Cuiabá e Bahia estão na zona de rebaixamento. Você mudaria algum desses times?"]
    ],
    [
        r'Quantos times tem no brasileirao\?',
        ["O Brasileirão tem 20 times. Você acha esse formato justo?"]
    ],
    [
        r'Qual o melhor time do brasil\?',
        ["Atualmente o Palmeiras vem sendo o mais consistente. Você concorda com isso?"]
    ],
    [
        r'O Flamengo vai ganhar\?',
        ["O Flamengo tem chances, mas depende dos próximos jogos. Você acha que ele consegue chegar na liderança?"]
    ],
    [
        r'Quais os times do brasileirao 2026\?',
        ["Os times incluem Flamengo, Palmeiras, Corinthians, São Paulo, Vasco, entre outros. Qual deles você torce?"]
    ],
    [
        r'Quem esta no G4\?',
        ["O G4 é formado por Palmeiras, Atlético-MG, Flamengo e Grêmio. Algum desses é o seu time?"]
    ],
    [
        r'Qual time tem mais vitorias\?',
        ["O Palmeiras é o time com mais vitórias até agora. Você acha que isso garante o título?"]
    ],
    [
        r'Qual time tem mais derrotas\?',
        ["O Coritiba é o time com mais derrotas. Você acha que ele ainda pode se recuperar?"]
    ],
    [
        r'Qual time mais empatou\?',
        ["O São Paulo é o time com mais empates. Você acha que empatar muito atrapalha na tabela?"]
    ],
    [
        r'Quem tem mais gols no campeonato\?',
        ["O Palmeiras tem o maior número de gols marcados. Qual time você acha mais ofensivo?"]
    ],
    [
        r'Qual jogo mais esperado da rodada\?',
        ["O clássico entre Flamengo e Vasco é o mais esperado. Quem você acha que ganha esse jogo?"]
    ],
    [
        r'Quem é o melhor tecnico\?',
        ["O técnico do Palmeiras vem se destacando bastante. Qual técnico você acha melhor?"]
    ],
    [
        r'(.*)',
        ["Não tenho essa informação agora. Você quer fazer outra pergunta sobre o Brasileirão 2026?"]
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
        print("Chatbot: Até mais! Vai acompanhar a próxima rodada?")
        break
    response = chatbot.respond(user_input)
    print("Chatbot:", response)