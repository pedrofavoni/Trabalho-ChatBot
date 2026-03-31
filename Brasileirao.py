import random
import nltk
from nltk.chat.util import Chat, reflections


pares = [
    [
        r'Oi|Olá|E ai',
        ["Oi! Tudo bem? Pra começar, na sua opinião, qual é o maior time do mundo?"]
    ],
    [
        r'(.*)',
        ["Entendi seu ponto. Muita gente discute isso mesmo. Mas pensando no Brasil, você sabe quem foi o último campeão do Brasileirão?"]
    ],
    [
        r'(.*)',
        ["O último campeão foi o Palmeiras. Você acha que ele entra como favorito também em 2026?"]
    ],
    [
        r'(.*)',
        ["Faz sentido. Inclusive, ele está liderando o campeonato agora. Você acha que ele consegue manter essa liderança até o final?"]
    ],
    [
        r'(.*)',
        ["Porque a disputa está forte no topo da tabela. Você sabe quais times estão no G4 atualmente?"]
    ],
    [
        r'(.*)',
        ["O G4 hoje tem Palmeiras, Atlético-MG, Flamengo e Grêmio. Desses, qual você acha que tem mais chance de ser campeão?"]
    ],
    [
        r'(.*)',
        ["Boa escolha. Inclusive o Flamengo está logo ali brigando no topo. Você acha que ele consegue assumir a liderança?"]
    ],
    [
        r'(.*)',
        ["E olhando mais pra baixo na tabela, o Vasco está no meio. Você acha que ele ainda pode brigar por algo maior?"]
    ],
    [
        r'(.*)',
        ["Agora pensando na parte de baixo, a situação já complica. Você sabe quem está na zona de rebaixamento?"]
    ],
    [
        r'(.*)',
        ["Atualmente são Coritiba, Goiás, Cuiabá e Bahia. Você acha que algum desses consegue escapar?"]
    ],
    [
        r'(.*)',
        ["Pra sair dessa situação, o desempenho ofensivo é muito importante. Você sabe qual time tem o melhor ataque até agora?"]
    ],
    [
        r'(.*)',
        ["O melhor ataque é do Palmeiras. Você acha que ataque forte é o principal fator pra ganhar o campeonato?"]
    ],
    [
        r'(.*)',
        ["Mas não é só ataque, né? Defesa também conta muito. Você sabe qual time tem a melhor defesa?"]
    ],
    [
        r'(.*)',
        ["A melhor defesa é do Atlético-MG. Você acha que um time equilibrado tem mais chances que um só ofensivo?"]
    ],
    [
        r'(.*)',
        ["Falando em desempenho, vitórias fazem muita diferença. Você sabe qual time mais venceu até agora?"]
    ],
    [
        r'(.*)',
        ["O Palmeiras lidera também em número de vitórias. Você acha que isso praticamente garante o título?"]
    ],
    [
        r'(.*)',
        ["Além do coletivo, tem o destaque individual. Você sabe quem é o artilheiro do campeonato?"]
    ],
    [
        r'(.*)',
        ["O artilheiro é o Pedro do Flamengo. Você acha que ele mantém esse ritmo até o final?"]
    ],
    [
        r'(.*)',
        ["Jogadores decisivos fazem diferença em jogos grandes. Falando nisso, qual clássico você acha mais importante hoje?"]
    ],
    [
        r'(.*)',
        ["Um dos maiores é Flamengo contra Vasco. Quem você acha que leva a melhor nesse confronto?"]
    ],
    [
        r'(.*)',
        ["Ah, entendi... pelo jeito você não sabe muito de bola mesmo 😄"]
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