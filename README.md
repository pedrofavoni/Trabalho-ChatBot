# BrasileirãoBot — Chatbot híbrido (NLTK + Base de Conhecimento + LLM)

Trabalho Final de Inteligência Artificial e Machine Learning
**Tema:** Campeonato Brasileiro (Brasileirão)
**Participantes:** Pedro Vittor Favoni, Lucas Tinoco, Samuel Marcellino e Ian Pablo

## Visão geral

Chatbot com **arquitetura híbrida**: o agente tenta responder primeiro pela
**base de conhecimento estruturada** (local, em `src/dataset.json`) e, quando não
há informação suficiente, recorre a um **modelo de linguagem (LLM) da Hugging
Face** como *fallback*. Esse fluxo atende ao requisito do trabalho:

> O agente tenta responder utilizando a base de conhecimento → se não houver
> informação suficiente, o LLM é utilizado como *fallback*.

A resposta sempre indica a **fonte**: `BASE` (base de conhecimento) ou `LLM`.

## Arquitetura

```
app.py                      # ponto de entrada (modo CLI e modo Web/Flask)
src/
├── dataset.json            # base de conhecimento estruturada (times, jogadores, técnicos, clássicos)
├── IBrasileiraoRepository  # interface + LocalJsonRepository (consulta à base)
├── Orchestrator.py         # orquestra o fluxo: base -> (se preciso) LLM
├── StateManagement.py      # contexto da conversa (time/técnico em foco)
├── entities/               # Team, Player, Coach (dataclasses)
├── nlp/                    # camada de PLN
│   ├── NLPProcessor.py        # normalização, tokenização e stemming (NLTK RSLPStemmer)
│   ├── IntentClassifier.py    # cadeia de handlers de intenção
│   ├── IntentHandlers.py      # handlers por palavra-chave (tabela, G4, artilheiro...)
│   ├── GreetingMLHandler.py   # saudações via Naive Bayes (ML supervisionado)
│   ├── AffirmationHandler.py  # sim/não via Naive Bayes (ML supervisionado)
│   ├── EntityExtractor.py     # extração de times/jogadores (similaridade de strings)
│   └── ResponseEnricher.py    # ganchos de follow-up para guiar a conversa
├── learningModel/          # camada do LLM
│   ├── ILLMFallback.py        # interface do fallback
│   └── HuggingFaceFallback.py # implementação com InferenceClient
└── static/index.html       # interface web
```

### Técnicas de IA / ML / PLN utilizadas
- **PLN (NLTK):** normalização Unicode, tokenização e *stemming* em português
  (`RSLPStemmer`).
- **Machine Learning (supervisionado):** classificadores **Naive Bayes** treinados
  para detectar saudações/despedidas e respostas de sim/não.
- **Recuperação de informação (retrieval):** consulta a uma base estruturada via
  *Repository Pattern*, com extração de entidades por similaridade de strings.
- **Modelo de linguagem (transformer):** `meta-llama/Llama-3.1-8B-Instruct` via
  Hugging Face Inference API, usado como *fallback*.

### Por que o modelo `Llama-3.1-8B-Instruct`?
Modelo *open-source* instruído, com bom desempenho em português, tamanho
equilibrado (qualidade x custo) e disponível na plataforma da Hugging Face,
acessível via `InferenceClient`.

## Como executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure o token da Hugging Face:
   ```bash
   # copie o exemplo e edite com o seu token
   cp src/.env.example src/.env
   # no Windows (PowerShell): Copy-Item src/.env.example src/.env
   ```
   Edite `src/.env` e preencha `HF_TOKEN=...`.
   > Sem o token, o bot ainda funciona apenas com a base de conhecimento (o
   > *fallback* LLM fica desativado).
3. Execute:
   ```bash
   python app.py          # modo terminal (CLI)
   python app.py --web    # modo web em http://localhost:5000
   ```

## Exemplos de perguntas

**Respondidas pela base:**
- "qual o líder do brasileirão?"
- "quem é o artilheiro?"
- "quais times estão no G4?"
- "quem está na zona de rebaixamento?"
- "quantos títulos o Palmeiras tem?"
- "me fala do Flamengo"
- "quais são os maiores clássicos?"

**Encaminhadas ao LLM (fora da base):**
- "quem ganhou a Libertadores de 2022?"
- "qual a história do futebol brasileiro?"
