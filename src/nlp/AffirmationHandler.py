import unicodedata
from typing import List

from nltk.stem import RSLPStemmer
from nltk.classify import NaiveBayesClassifier

from .IntentHandlers import IntentHandler

TRAINING_DATA = [
    ("sim", "afirmacao"),
    ("sim por favor", "afirmacao"),
    ("claro", "afirmacao"),
    ("com certeza", "afirmacao"),
    ("quero", "afirmacao"),
    ("quero sim", "afirmacao"),
    ("pode ser", "afirmacao"),
    ("vai", "afirmacao"),
    ("ok", "afirmacao"),
    ("okay", "afirmacao"),
    ("isso", "afirmacao"),
    ("exato", "afirmacao"),
    ("s", "afirmacao"),
    ("yep", "afirmacao"),
    ("yes", "afirmacao"),
    ("positivo", "afirmacao"),
    ("por favor", "afirmacao"),

    ("nao", "negacao"),
    ("não", "negacao"),
    ("nao quero", "negacao"),
    ("não precisa", "negacao"),
    ("deixa", "negacao"),
    ("obrigado nao", "negacao"),
    ("pode pular", "negacao"),
    ("n", "negacao"),
    ("nope", "negacao"),
    ("negativo", "negacao"),
    ("ta bom nao", "negacao"),
    ("nao obrigado", "negacao"),
    ("nao preciso", "negacao"),
    ("dispenso", "negacao"),
    ("para", "negacao"),

    ("quem e o tecnico", "outro"),
    ("qual a classificacao", "outro"),
    ("me fale do elenco", "outro"),
    ("quantos titulos", "outro"),
    ("quem e o artilheiro", "outro"),
    ("me conta uma curiosidade", "outro"),
    ("quais os classicos", "outro"),
    ("quem esta no g4", "outro"),
    ("oi", "outro"),
    ("tchau", "outro"),
]


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def _extrair_features(tokens: List[str]) -> dict:
    return {token: True for token in tokens}


class AffirmationHandler(IntentHandler):
    """Classifica respostas de sim/não (afirmação/negação) com Naive Bayes."""

    def __init__(self, stemmer: RSLPStemmer):
        self._stemmer = stemmer
        self._classifier = self._treinar()
        self._ultimo_rotulo: str = "afirmacao"

    def _treinar(self) -> NaiveBayesClassifier:
        conjunto_treino = [
            (_extrair_features(self._tokenizar(texto)), rotulo)
            for texto, rotulo in TRAINING_DATA
        ]
        return NaiveBayesClassifier.train(conjunto_treino)

    def _tokenizar(self, texto: str) -> List[str]:
        normalizado = _normalizar(texto)
        tokens = normalizado.split()
        return [self._stemmer.stem(t) for t in tokens]

    def _raw_keywords(self) -> List[str]:
        return []

    def matches(self, tokens: List[str]) -> bool:
        if not tokens:
            return False
        features = _extrair_features(tokens)
        rotulo = self._classifier.classify(features)
        self._ultimo_rotulo = rotulo
        return rotulo in {"afirmacao", "negacao"}

    def get_intent_name(self) -> str:
        return "ask_affirmation"

    def get_label(self) -> str:
        return self._ultimo_rotulo

    def get_stemmed_keywords(self) -> List[str]:
        return []
