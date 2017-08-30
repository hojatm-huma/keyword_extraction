from __future__ import unicode_literals

from django.db import models

from keywordfinder import RUN


class Text(models.Model):
    """
    model saving text.
    """
    text = models.TextField()

    def save_keywords(self, topic):
        keywords = RUN.main(self.text)

        for keyword in keywords:
            Keyword(topic=topic, text=self, keyword=keyword[0], rank=keyword[1]).save()


class Keyword(models.Model):
    topic = models.CharField(max_length=20)
    text = models.ForeignKey(Text)
    keyword = models.CharField(max_length=20)
    rank = models.FloatField()


class GameId(models.Model):
    texts = models.ManyToManyField(Text)

    def get_aggregated_text(self):
        aggregated_texts = ''
        for text in self.texts.all():
            aggregated_texts = aggregated_texts + '\n' + text.text

        return aggregated_texts