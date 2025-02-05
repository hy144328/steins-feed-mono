import typing

import nltk.stem.snowball
import sklearn.feature_extraction.text

import steins_feed_model.feeds

from . import util

LANG2STEMMER: dict[steins_feed_model.feeds.Language, nltk.stem.snowball.StemmerI] = {
    steins_feed_model.feeds.Language.ENGLISH: nltk.stem.snowball.EnglishStemmer(),
    steins_feed_model.feeds.Language.GERMAN: nltk.stem.snowball.GermanStemmer(),
    steins_feed_model.feeds.Language.SWEDISH: nltk.stem.snowball.SwedishStemmer(),
}

class StemmingCountVectorizer(sklearn.feature_extraction.text.CountVectorizer):
    def __init__(
        self,
        lang: steins_feed_model.feeds.Language,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.lang = lang
        self.stemmer = LANG2STEMMER[lang]

    @typing.override
    def build_tokenizer(self, skip_stem: bool=False) -> typing.Callable[[str], list[str]]:
        tokenize: typing.Callable[[str], list[str]] = super().build_tokenizer()
        if skip_stem:
            return tokenize

        stem: typing.Callable[[str], str] = self.stemmer.stem
        return util.concatenate(tokenize, util.map_over(stem))
