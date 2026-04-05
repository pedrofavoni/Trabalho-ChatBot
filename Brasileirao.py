import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk

# Download dos recursos necessários (primeira vez)
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
        self.respostas_anteriores = {}
        self.stemmer = SnowballStemmer('portuguese')
        self.stop_words = set(stopwords.words('portuguese'))
        
        # Mapear sinônimos e variações
        self.sim_patterns = ['sim', 'verdade', 'claro', 'com certeza', 'acho que sim', 'concordo', 'óbvio', 'definitivamente', 'pois é', 'exato']
        self.nao_patterns = ['não', 'nope', 'nada', 'nunca', 'acho que não', 'discordo', 'difícil', 'talvez']
    
    def processar_texto(self, texto):
        """Processa e limpa o texto com NLTK"""
        texto = texto.lower().strip()
        tokens = word_tokenize(texto)
        tokens_raw = [palavra for palavra in tokens if palavra.isalnum() and palavra not in self.stop_words]
        # Remove stopwords e tokeniza
        tokens_limpos = [self.stemmer.stem(palavra) for palavra in tokens_raw]
        return tokens_limpos, texto, tokens_raw
    
    def detectar_sentimento(self, entrada):
        """Detecta se é sim/não/neutro"""
        entrada_lower = entrada.lower()
        
        if any(palavra in entrada_lower for palavra in self.sim_patterns):
            return 'sim'
        elif any(palavra in entrada_lower for palavra in self.nao_patterns):
            return 'nao'
        return 'neutro'
    
    def extrair_resposta_usuario(self, tokens_raw, entrada):
        """Extrai palavras-chave da resposta do usuário"""
        # Remove palavras muito curtas e stopwords
        palavras_chave = [t for t in tokens_raw if len(t) > 2]
        return ' '.join(palavras_chave[:3]) if palavras_chave else entrada
    
    def respond(self, user_input):
        tokens, entrada, tokens_raw = self.processar_texto(user_input)
        sentimento = self.detectar_sentimento(entrada)
        
        # Passo 0: Saudação
        if self.step == 0:
            if any(palavra in tokens for palavra in ['oi', 'olá', 'ola', 'eai', 'tudo', 'bem']):
                self.step = 1
                return "Oi! Tudo bem? Pra começar, na sua opinião, qual é o maior time do mundo?"
            else:
                return "Olá! Digite 'Oi' para começar a conversar sobre futebol! ⚽"
        
        # Passo 1: Qual é o maior time?
        elif self.step == 1:
            self.respostas_anteriores['maior_time'] = self.extrair_resposta_usuario(tokens_raw, entrada)
            self.step = 2
            return f"Que legal! {self.respostas_anteriores['maior_time'].title()} é uma ótima resposta. O Flamengo foi o último campeão do Brasileirão. Você acha que ele entra como favorito também em 2026?"
        
        # Passo 2: Palmeiras como favorito?
        elif self.step == 2:
            if sentimento == 'sim':
                self.step = 3
                return "Faz sentido! Inclusive, ele está liderando o campeonato agora. Você acha que ele consegue manter essa liderança até o final?"
            else:
                self.step = 3
                return "Entendo seu ponto de vista. De qualquer forma, ele está liderando o campeonato agora. Você acha que ele consegue manter essa liderança até o final?"
        
        # Passo 3: Palmeiras manter liderança?
        elif self.step == 3:
            self.step = 4
            return "Porque a disputa está forte no topo da tabela. Você sabe quais times estão no G4 atualmente?"
        
        # Passo 4: Qual é o G4?
        elif self.step == 4:
            self.step = 5
            return "O G4 hoje tem Palmeiras, Atlético-MG, Flamengo e Grêmio. Desses, qual você acha que tem mais chance de ser campeão?"
        
        # Passo 5: Qual time do G4?
        elif self.step == 5:
            self.respostas_anteriores['favorito_g4'] = self.extrair_resposta_usuario(tokens_raw, entrada)
            self.step = 6
            time_escolhido = self.respostas_anteriores['favorito_g4'].title()
            return f"Boa escolha! O {time_escolhido} realmente merece destaque. E olhando mais pra baixo na tabela, o Vasco está no meio. Você acha que ele ainda pode brigar por algo maior?"
        
        # Passo 6: Vasco pode brigar?
        elif self.step == 6:
            self.step = 7
            return "Agora pensando na parte de baixo, a situação já complica. Você sabe quem está na zona de rebaixamento?"
        
        # Passo 7: Zona de rebaixamento
        elif self.step == 7:
            self.step = 8
            return "Atualmente estão Coritiba, Goiás, Cuiabá e Bahia. É uma situação complicada para esses times. Você acha que algum desses consegue escapar?"
        
        # Passo 8: Escapar do rebaixamento?
        elif self.step == 8:
            self.step = 9
            return "Realmente é difícil. Pra sair dessa situação, o desempenho ofensivo é muito importante. Você sabe qual time tem o melhor ataque até agora?"
        
        # Passo 9: Melhor ataque
        elif self.step == 9:
            self.step = 10
            return "O melhor ataque é do Palmeiras! Você acha que ter um ataque forte é o principal fator pra ganhar o campeonato?"
        
        # Passo 10: Ataque vs Defesa
        elif self.step == 10:
            if sentimento == 'sim':
                self.step = 11
                return "Exatamente! Gols é o que mais importa no final. Mas a defesa também é crucial. Qual time você acha que tem a melhor defesa?"
            else:
                self.step = 11
                return "Faz sentido, a defesa também é importante demais. Qual time você acha que tem a melhor defesa?"
        
        # Passo 11: Melhor defesa
        elif self.step == 11:
            self.step = 12
            return "A melhor defesa é do Atlético-MG! Você acha que um time equilibrado entre ataque e defesa tem mais chances que um só ofensivo?"
        
        # Passo 12: Equilíbrio
        elif self.step == 12:
            self.step = 13
            return "Boa observação! Falando em números, você sabe qual time mais venceu até agora no campeonato?"
        
        # Passo 13: Mais vitórias
        elif self.step == 13:
            self.step = 14
            return "O Palmeiras lidera em número de vitórias também! Você acha que isso praticamente garante o título?"
        
        # Passo 14: Garante título?
        elif self.step == 14:
            self.step = 15
            return "Entendo. Além do coletivo, tem o destaque individual. Você sabe quem é o artilheiro do campeonato?"
        
        # Passo 15: Artilheiro
        elif self.step == 15:
            self.step = 16
            return "O artilheiro é o Pedro do Flamengo! Você acha que ele mantém esse ritmo goleador até o final da temporada?"
        
        # Passo 16: Pedro mantém ritmo?
        elif self.step == 16:
            self.step = 17
            return "Jogadores decisivos fazem muita diferença em jogos grandes. Falando nisso, qual clássico você acha mais importante nessa temporada?"
        
        # Passo 17: Clássico importante
        elif self.step == 17:
            self.step = 18
            time_classico = self.extrair_resposta_usuario(tokens_raw, entrada).title()
            return f"Interessante! {time_classico} é realmente importante. E pensando no Flamengo contra Vasco, quem você acha que leva a melhor nesse clássico?"
        
        # Passo 18: Flamengo vs Vasco
        elif self.step == 18:
            time_vencedor = self.extrair_resposta_usuario(tokens_raw, entrada).title()
            self.step = 19
            return f"Legal! Você torce pro {time_vencedor} então? Isso foi uma ótima conversa sobre futebol! ⚽"
        
        # Final
        else:
            if any(palavra in entrada for palavra in ['oi', 'olá', 'ola', 'eai']):
                self.step = 1
                return "Oi! Tudo bem? Pra começar, na sua opinião, qual é o maior time do mundo?"
            return "Foi um prazer conversar sobre futebol com você! Quer começar uma nova conversa? Digite 'Oi'!"

# Criar instância do chatbot
chatbot = Chatbot()

# Loop principal (apenas se executado diretamente)
if __name__ == "__main__":
    print("Chatbot Brasileirão ⚽ (digite 'sair' para encerrar)\n")
    while True:
        entrada = input("Você: ")
        if entrada.lower() == 'sair':
            break
        print(f"Bot: {chatbot.respond(entrada)}\n")