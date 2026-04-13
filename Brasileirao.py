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
            1: ['time', 'club'],
            2: ['favorit'],
            3: ['lider'],
            4: ['g4', 'libertador'],
            5: ['surpreend', 'surpresa', 'campeã'],
            7: ['rebaix', 'zona', 'z4'],
            9: ['ataqu', 'gol'],
            11: ['defes'],
            15: ['artilheir'],
            17: ['classic']
        }

        # respostas pré-definidas para cada etapa
        self.respostas = {
            4: "O G4 atualmente tem Palmeiras, Flamengo, São Paulo e FluminenCe.",
            5: "Times como Coritiba e EC Vitória podem surpreender.",
            7: "Na zona de rebaixamento está Cruziro, Remo, Chapecoense e Mirassol.",
            9: "O melhores ataques do Brasileirão é do Palmeiras.",
            11: "Defesas mais sólidas até o momento é a do Flamengo.",
            15: "O artilheiro é o Carlos Vinícius do gremio com 7 gols.",
            17: "Os clássicos mais importantes incluem o Clássico dos Milhões, com Flamengo e Vasco e o GreNal, com Gremio e Internacional."
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
        nao = ['não', 'nao', 'nunca', 'jamais', 'discordo']

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
            1: "Qual é o seu time?",
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
                return "Fala! ⚽\nQual é o seu time?"
            return "Digite 'Oi' pra começar 😄"

        elif self.step == 1:
            self.memoria['time'] = user_input
            self.step = 2
            return f"{user_input.title()} é muito bom 🔥\nVocê acha o Palmeiras favorito?"

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
            if sentimento == 'sim':
                return "Ele ta sempre brigando pelo topo 🏆\nVocê sabe quem está no G4?"
            elif sentimento == 'nao':
                return "Realmente o topo da tabela tá disputado!\nVocê sabe quem está no G4?"
            else:
                return "É justo 🤔\nVocê sabe quem está no G4?"

        elif self.step == 4:
            self.step = 5
            if sentimento == 'sim':
                return "Só time forte ali 🔥!\nQuem você acha que vai ser campeão?"
            elif sentimento == 'nao':
                return "O G4 atualmente tem Palmeiras, Flamengo, São Paulo e FluminenCe.\nQuem você acha que vai ser campeão?"
            else:
                return "Compreendo 🤔\nQuem você acha que vai ser campeão?"

        elif self.step == 5:
            self.memoria['campeao'] = user_input
            self.step = 6
            return f"{user_input.title()} é uma boa aposta!\nE o Vasco pode brigar?"

        elif self.step == 6:
            self.step = 7
            if sentimento == 'sim':
                return "É o gigante💢 não tem jeito!\nVocê sabe quem está na zona de rebaixamento?"
            elif sentimento == 'nao':
                return "Situação complicada 😅\nVocê sabe quem está na zona de rebaixamento?"
            return "Entendo 🤔\nVocê sabe quem está na zona de rebaixamento?"

        elif self.step == 7:
            self.step = 8
            if sentimento == 'sim':
                return "Parte tensa 😬\nAlgum desses escapa?"
            elif sentimento == 'nao':
                return "Na zona de rebaixamento está Cruziro, Remo, Chapecoense e Mirassol.\nAlgum desses escapa?"
            else:
                return "Faz sentido 🤔\nAlgum desses escapa?"

        elif self.step == 8:
            self.step = 9
            if sentimento == 'nao':
                return "É realmente uma situação dificil de sair 😬\nVocê sabe qual time tem o melhor ataque?"
            else:
                return "Precisa reagir rápido!\nVocê sabe qual time tem o melhor ataque??"

        elif self.step == 9:
            self.step = 10
            if sentimento == 'sim':
                return "Ataque decide muito ⚽\nVocê acha que isso ganha campeonato?"
            elif sentimento == 'nao':
                return "O melhores ataques do Brasileirão é do Palmeiras.\nVocê acha que isso ganha campeonato?"
            else:
                return "É justo 🤔\nVocê acha que isso ganha campeonato?"

        elif self.step == 10:
            self.step = 11
            return "Defesa também conta 🛡️\nVocê sabe quem tem a melhor defesa?"

        elif self.step == 11:
            self.step = 12
            if sentimento == 'nao':
                "Defesas mais sólidas até o momento é a do Flamengo.\nNa sua opinião o equilíbrio é mais importante?"
            else:
                return "Equilíbrio é chave!\nNa sua opinião o equilíbrio é mais importante?"

        elif self.step == 12:
            self.step = 13
            if sentimento == 'nao':
                "Defesas mais sólidas até o momento é a do Flamengo.\nSabe quem tem o maior numero de vitorias?"
            else:
                return "Regularidade vence 🏆\nSabe quem tem o maior numero de vitorias?"

        elif self.step == 13:
            self.step = 14
            if sentimento == 'nao':
                "Defesas mais sólidas até o momento é a do Flamengo.\nSabe quem tem o maior numero de vitorias?"
            else:
                return "Vitórias ajudam!\nIsso garante título?"

        elif self.step == 14:
            self.step = 15
            return "É, nem sempre 😄\nE o artilheiro você sabe quem é?"

        elif self.step == 15:
            self.step = 16
            if sentimento == 'sim':
                "Ele tá voando 🔥\nEle mantém o ritmo?"
            else:
                return "O artilheiro é o Carlos Vinícius do gremio com 7 gols.\nEle mantém o ritmo?"

        elif self.step == 16:
            self.step = 17
            if sentimento == 'sim':
                return "Ele pode decidir jogos!\nVamo falar de clássicos, qual é o maior?"
            elif sentimento == 'nao':
                return "É normal alguns jogadores cair de rendimento \nVamo falar de clássicos, qual é o maior?"
            else:
                return "Compreendo 🤔\nVamo falar de clássicos, qual é o maior?"


        elif self.step == 17:
            self.memoria['classico'] = user_input
            self.step = 18
            return f"{user_input.title()} é pesado 🔥\nE no Clássico dos Milhões, Flamengo ou Vasco?"

        elif self.step == 18:
            self.step = 0
            resposta = user_input.lower().strip()

            flamengo_keywords = [
                "flamengo","mengão", "mengao","mengo","fla"
            ]

            vasco_keywords = [
                "vasco","vascão", "vascao","gigante da colina","vascudo","gigante"
            ]

            if any(palavra in resposta for palavra in flamengo_keywords):
                self.step = 0
                return "É o MENGÃO🔴⚫🦅! Ele é o maior vencedor do clássico com 168 vitórias a 139 vitórias do Vasco\nBoa conversa! Quer começar de novo?"

            elif any(palavra in resposta for palavra in vasco_keywords):
                self.step = 0
                return "É o trem bala da Colina💢, Ele possui a maior goleada do clássico por Vas 7 x 0 Fla!\nBoa conversa! Quer começar de novo?"

            else:
                self.step = 0
                return "Clássico é clássico 😅 emoção garantida dos dois lados!\nBoa conversa! Quer começar de novo?"
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