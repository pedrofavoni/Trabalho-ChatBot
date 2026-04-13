import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk

# Ao executar pela primeira vez
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class Chatbot:
    def __init__(self):
        self.step = 0
        self.memoria = {}

        self.stemmer = SnowballStemmer('portuguese')
        self.stop_words = set(stopwords.words('portuguese'))

        # palavras-chave para detectar intenções
        self.intents = {
            1: ['time', 'club', 'mai', 'mund'],
            2: ['flameng', 'favorit'],
            3: ['lider', 'palmeir'],
            4: ['g4', 'libertador'],
            5: ['surpreend', 'surpresa', 'campeã'],
            7: ['rebaix', 'zona'],
            9: ['ataqu', 'gol'],
            11: ['defes'],
            15: ['artilheir'],
            17: ['classic']
        }

        # respostas pré-definidas para cada etapa
        self.respostas = {
            4: "O G4 atualmente tem Palmeiras, Flamengo, Atlético-MG e Grêmio.",
            5: "Times como Atlético-GO e Mirassol podem surpreender.",
            7: "A zona de rebaixamento geralmente inclui os últimos colocados da tabela.",
            9: "Os melhores ataques costumam ser de times como Palmeiras e Flamengo.",
            11: "Defesas sólidas geralmente são de times como Atlético-MG.",
            15: "O artilheiro costuma ser um destaque ofensivo, como Pedro do Flamengo.",
            17: "Os clássicos mais importantes incluem Flamengo x Vasco e GreNal."
        }

    # 🔹 NLP
    def processar_texto(self, texto):
        texto = texto.lower().strip()
        tokens = word_tokenize(texto)

        tokens = [t for t in tokens if t.isalnum() and t not in self.stop_words]
        stems = [self.stemmer.stem(t) for t in tokens]

        return stems, texto

    # 🔹 intenção
    def detectar_intencao(self, stems):
        for step, palavras in self.intents.items():
            for stem in stems:
                for palavra in palavras:
                    if stem.startswith(palavra):
                        return step
        return None

    # 🔹 sentimento
    def detectar_sentimento(self, texto):
        sim = ['sim', 'claro', 'aham', 'com certeza']
        nao = ['não', 'nunca', 'jamais', 'discordo']

        for s in sim:
            if s in texto:
                return 'sim'
        for n in nao:
            if n in texto:
                return 'nao'
        return 'neutro'

    # 🔹 perguntas
    def pergunta_atual(self):
        perguntas = {
            1: "Qual é o maior time do mundo na sua opinião?",
            2: "Você acha o Flamengo favorito?",
            3: "Ele mantém a liderança?",
            4: "Quem você acha que vai ser campeão entre os do G4?",
            5: "Algum time pode surpreender?",
            6: "O Vasco pode brigar por algo maior?",
            7: "Algum desses da zona consegue escapar?",
            8: "Qual time pode reagir?",
            9: "Você acha que ataque ganha campeonato?",
            10: "Defesa também é importante?",
            11: "Você prefere ataque ou defesa forte?",
            12: "Equilíbrio é mais importante?",
            13: "Regularidade decide campeonato?",
            14: "Isso garante título?",
            15: "Você acha que o artilheiro decide o campeonato?",
            16: "Ele mantém o ritmo?",
            17: "Qual clássico mais te chama atenção?",
            18: "Flamengo ou Vasco?"
        }
        return perguntas.get(self.step, "Vamos falar de futebol ⚽")

    #  MAIN
    def respond(self, user_input):
        stems, entrada = self.processar_texto(user_input)
        sentimento = self.detectar_sentimento(entrada)

        #  PULO INTELIGENTE
        step_detectado = self.detectar_intencao(stems)
        if step_detectado:
            self.step = step_detectado

            resposta = self.respostas.get(self.step, "")

            # CONTINUAÇÃO INTELIGENTE
            if self.step == 1:
                return (
                    f"O Real Madrid é considerado o maior time do mundo! ⚽\n"
                    f"{resposta}\n"
                    f"{self.pergunta_atual()}"
                )
            
            if self.step == 2:
                return f"O flamengo é um time muito forte!\n{self.pergunta_atual()}"
            
            if self.step == 3:
                return f"O Palmeiras é o líder do campeonato!\n{self.pergunta_atual()}"

            if self.step == 4:
                return f"{resposta}\nQuem você acha que vai ser campeão?"
            
            if self.step == 5:
                return f"{resposta}\nAlgum time pode surpreender?"

            if self.step == 15:
                return f"{resposta}\nVocê acha que ele mantém o ritmo?"

            if resposta:
                return f"{resposta}\n{self.pergunta_atual()}"

            return self.pergunta_atual()

        # 🔥 FLUXO NORMAL
        if self.step == 0:
            if re.search(r'\b(oi|olá|ola|eai)\b', entrada):
                self.step = 1
                return "Fala! ⚽\nQual é o maior time do mundo?"
            return "Digite 'Oi' pra começar 😄"

        elif self.step == 1:
            self.memoria['time'] = user_input
            self.step = 2
            return f"{user_input.title()} é gigante 🔥\nVocê acha o Flamengo favorito?"

        elif self.step == 2:
            self.step = 3
            if sentimento == 'sim':
                return "Também acho! Vem forte 💪\nEle mantém a liderança?"
            elif sentimento == 'nao':
                return "Tem concorrência pesada 👀\nEle mantém a liderança?"
            else:
                return "Faz sentido 🤔\nEle mantém a liderança?"

        elif self.step == 3:
            self.step = 4
            return "Topo da tabela tá disputado!\nQuem está no G4?"

        elif self.step == 4:
            self.step = 5
            return "Só time forte ali!\nQuem você acha que vai ser campeão?"

        elif self.step == 5:
            self.memoria['campeao'] = user_input
            self.step = 6
            return f"{user_input.title()} é uma boa aposta!\nO Vasco pode brigar?"

        elif self.step == 6:
            self.step = 7
            return "Situação complicada 😅\nQuem está na zona de rebaixamento?"

        elif self.step == 7:
            self.step = 8
            return "Parte tensa 😬\nAlgum desses escapa?"

        elif self.step == 8:
            self.step = 9
            return "Precisa reagir rápido!\nQual time tem o melhor ataque?"

        elif self.step == 9:
            self.step = 10
            return "Ataque decide muito ⚽\nVocê acha que isso ganha campeonato?"

        elif self.step == 10:
            self.step = 11
            return "Defesa também conta 🛡️\nQuem tem a melhor defesa?"

        elif self.step == 11:
            self.step = 12
            return "Equilíbrio é chave!\nEquilíbrio é mais importante?"

        elif self.step == 12:
            self.step = 13
            return "Regularidade vence!\nQuem mais venceu?"

        elif self.step == 13:
            self.step = 14
            return "Vitórias ajudam!\nIsso garante título?"

        elif self.step == 14:
            self.step = 15
            return "Nem sempre 😄\nQuem é o artilheiro?"

        elif self.step == 15:
            self.memoria['artilheiro'] = user_input
            self.step = 16
            return f"{user_input.title()} tá voando 🔥\nEle mantém o ritmo?"

        elif self.step == 16:
            self.step = 17
            return "Pode decidir jogos!\nQual clássico mais importante?"

        elif self.step == 17:
            self.memoria['classico'] = user_input
            self.step = 18
            return f"{user_input.title()} é pesado 🔥\nFlamengo ou Vasco?"

        elif self.step == 18:
            self.step = 0
            return f"{user_input.title()} hein 😄\nBoa conversa! Quer começar de novo?"

        # 🔥 FALLBACK
        return f"Não entendi 🤔\n{self.pergunta_atual()}"


# RUN
chatbot = Chatbot()

if __name__ == "__main__":
    print("Chatbot Brasileirão ⚽\n")
    while True:
        entrada = input("Você: ")
        if entrada.lower() == 'sair':
            break
        print("Bot:", chatbot.respond(entrada))