from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
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


class Topic(models.Model):
    topic = models.CharField(max_length=30)

    def get_and_insert(self):
        try:
            t = Topic.objects.get(topic=self.topic)
            return t
        except ObjectDoesNotExist:
            self.save()
            return self

class Keyword(models.Model):
    topic = models.ForeignKey(Topic)
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


class Site(models.Model):
    topic = models.ForeignKey(Topic, related_name='sites')
    url = models.CharField(max_length=200)
    last_fetched_article_date = models.BigIntegerField(null=True)
