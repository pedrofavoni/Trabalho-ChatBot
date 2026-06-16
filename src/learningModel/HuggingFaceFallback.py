from huggingface_hub import InferenceClient
from learningModel.ILLMFallback import ILLMFallback

SYSTEM_PROMPT = """Você é o BrasileirãoBot, um assistente simpático, descontraído e curioso sobre o Campeonato Brasileiro de futebol.
Responda sempre em português brasileiro, de forma conversacional e natural, como se fosse um amigo apaixonado por futebol.
Você pode conversar sobre qualquer assunto — filosofia, comida, ciência, entretenimento, o que for — mas sempre com um leve toque de futebol na sua personalidade.
Quando o assunto não for futebol, responda normalmente e, se fizer sentido de forma natural, mencione uma conexão engraçada ou criativa com o Brasileirão. Mas não force essa conexão em toda resposta.
Seja conciso, direto e use linguagem informal. Evite respostas longas demais."""

REFINE_PROMPT = """Você é o BrasileirãoBot, um assistente simpático e conversacional sobre o Campeonato Brasileiro.
Você receberá o contexto da conversa, a pergunta do usuário e uma resposta técnica gerada automaticamente.
Reescreva a resposta de forma natural e humanizada, em português brasileiro.

Regras obrigatórias:
- NÃO adicione frases introdutórias como "Que ótima pergunta!" ou "Claro!".
- NÃO invente informações novas. Use APENAS o que está na resposta técnica fornecida.
- Mantenha TODAS as informações originais — apenas melhore o estilo.
- Vá direto ao ponto e seja conciso."""


class HuggingFaceFallback(ILLMFallback):
    def __init__(self, token: str, model: str = "Qwen/Qwen2.5-7B-Instruct"):
        self._client = InferenceClient(
            provider="auto",
            api_key=token,
        )
        self._model = model

    def answer(self, question: str, context: str) -> str:
        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Contexto: {context}\n\nPergunta: {question}"}
                ],
                max_tokens=250,
            )
            return self._truncate_at_last_sentence(completion.choices[0].message.content.strip())
        except Exception as e:
            import traceback, pathlib
            pathlib.Path("llm_error.log").write_text(traceback.format_exc())
            return "Não entendi bem sua pergunta. Posso falar da tabela, artilharia, G4, rebaixamento, clássicos ou de um time específico. O que você quer saber?"

    def refine(self, question: str, raw_response: str, context: str = "") -> str:
        try:
            user_content = f"Pergunta original: {question}\n\nResposta para refinar: {raw_response}"
            if context:
                user_content = f"Contexto da conversa: {context}\n\n{user_content}"

            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": REFINE_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=250,
            )
            return self._truncate_at_last_sentence(completion.choices[0].message.content.strip())
        except Exception:
            return raw_response

    def _truncate_at_last_sentence(self, text: str) -> str:
        last_period = max(
            text.rfind("."),
            text.rfind("!"),
            text.rfind("?"),
        )
        if last_period == -1:
            return text
        return text[:last_period + 1]
