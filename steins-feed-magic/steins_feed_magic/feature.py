import typing

import nltk.stem.snowball
import sklearn.feature_extraction.text

import steins_feed_logging
import steins_feed_model.feeds

import util

logger = steins_feed_logging.LoggerFactory.get_logger(__name__)

LANG2STEMMER: dict[steins_feed_model.feeds.Language, nltk.stem.snowball.StemmerI] = {
    steins_feed_model.feeds.Language.ENGLISH: nltk.stem.snowball.EnglishStemmer(),
    steins_feed_model.feeds.Language.GERMAN: nltk.stem.snowball.GermanStemmer(),
    steins_feed_model.feeds.Language.SWEDISH: nltk.stem.snowball.SwedishStemmer(),
}

class NoStemmer(nltk.stem.snowball.StemmerI):
    @typing.override
    def stem(self, token: str) -> str:
        return token

class CountVectorizer(sklearn.feature_extraction.text.CountVectorizer):
    def __init__(
        self,
        lang: typing.Optional[steins_feed_model.feeds.Language],
        **kwargs,
    ):
        super().__init__(**kwargs)

        if lang is None:
            self.stemmer = NoStemmer()
        elif lang in LANG2STEMMER:
            self.stemmer = LANG2STEMMER[lang]
        else:
            logger.warning(f"No stemmer of language {lang}.")
            self.stemmer = NoStemmer()

    @typing.override
    def build_preprocessor(self) -> typing.Callable[[str], str]:
        preprocess = super().build_preprocessor()
        return util.chain(util.text_content, preprocess)

    @typing.override
    def build_tokenizer(self) -> typing.Callable[[str], list[str]]:
        tokenize = super().build_tokenizer()
        return lambda x: [self.stemmer.stem(s) for s in tokenize(x)]
