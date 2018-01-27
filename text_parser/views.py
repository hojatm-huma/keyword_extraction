import subprocess
from datetime import datetime
import json
import operator
from random import randint
from sets import Set
from subprocess import call
from threading import Thread
from time import mktime

import feedparser
import nltk
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max, F, Value
from django.http import Http404
from django.http import JsonResponse

from text_parser.models import Text, Keyword, GameId, Site, Topic


def add_article(request):
    """
    this adds text file in db and extracts keywords from it. --> keyword (text, topic, keyword, rank)
    :param text: text to be added
    :param topic: topic of text
    :return: check status code. OK(200) else(400)
    """
    if request.method == 'POST':
        param = request.POST
        text = param.get('text')
        topic = param.get('topic')

        if text is not None and topic is not None:
            t = Text(text=text)
            t.save()
            topic = Topic(topic=topic).get_and_insert()

            t.save_keywords(topic)

            return JsonResponse({'msg': 'added succ.'}, status=200)
        else:
            return JsonResponse({'msg': 'bad input.'}, status=400)
    else:
        return JsonResponse({'msg': 'just POST !'}, status=400)


def update_from_web_check():
    return randint(0, 5) == 3


def update_from_web(topic):
    print 'fetching from web'
    sites = Site.objects.filter(topic=topic)
    if len(sites) > 0:
        index = randint(0, len(sites))
        site = [site for site in sites][index-1]
        print 'site to fetch:', site.url

        feed = feedparser.parse(site.url)
        last_feed = feed['entries'][0]
        last_feed_date = mktime(last_feed['published_parsed'])
        last_fetched_date = site.last_fetched_article_date
        if last_fetched_date == None or last_fetched_date < last_feed_date:
            text = Text(text=last_feed['summary'])
            text.save()
            print 'fetched text:', text.text

            text.save_keywords(topic)

            site.last_fetched_article_date = last_feed_date
            site.save()
        else:
            print 'text already fetched'


def get_keywords(request):
    """
    Return all keywords of this topic. Each keyword's rank is summed up in all texts it exists in.
    Returned keywords are sorted.
    :param request:
    :return: sorted keywords. --> {'keywords':[(kw1, 1), (kw2, 2), (kw3, 3)]}
                check status code. OK(200) else(400)    """
    if request.method == 'POST':
        param = request.POST
        topic = param.get('topic')

        if topic is not None:
            try:
                topic = Topic.objects.get(topic=topic)

                if update_from_web_check():
                    Thread(target=update_from_web, args=(topic, )).start()

                keywords = Keyword.objects.filter(topic=topic).values('keyword').annotate(Sum('rank')).order_by(
                    '-rank__sum')
                response = []
                for keyword in keywords:
                    response.append((keyword.get('keyword'), keyword.get('rank__sum')))

                return JsonResponse({'keywords': response}, status=200)
            except ObjectDoesNotExist:
                return JsonResponse({'msg': 'topic does not exists.'}, status=400)
        else:
            return JsonResponse({'msg': 'bad input.'}, status=400)
    else:
        return JsonResponse({'msg': 'just POST.'}, status=400)


def new_game(request):
    """
    create a new game from texts the players' keywords mostly exist in.

    :param request: topic --> topic of new game
                    keywords --> [one, two, three] , union of keywords players bought.
    :return: on OK --> {'msg':'new game started', 'game_id':1}
                check status code. OK(200) else(400)
    """
    if request.method == 'POST':
        topic = request.POST.get('topic')
        keywords = request.POST.get('keywords')
        try:
            if topic is None:
                raise ValueError
            topic = Topic.objects.get(topic=topic)

            keywords = json.loads(keywords)

            aggregated_texts = Set()
            for keyword in keywords:
                high_ranked_text = Keyword.objects.filter(topic=topic, keyword=keyword).order_by('rank')[0].text
                aggregated_texts.add(high_ranked_text.id)

            game_id = GameId()
            game_id.save()
            game_id.texts.add(*list(aggregated_texts))

            return JsonResponse({'msg': 'new game started!', 'game_id': game_id.id}, status=200)

        except ValueError:
            return JsonResponse({'msg': 'bad input.'}, status=400)
        except ObjectDoesNotExist:
            return JsonResponse({'msg': 'topic does not exists.'}, status=400)
    else:
        return JsonResponse({'msg': 'just POST!'}, status=400)


def get_containing_sentences(request):
    """
    returns two sentences which given keywords most probably exist in.
    :param request: game_id --> id of game players are in
                    keywords --> union of users' keywords.
    :return: {'sentences':[sen1, sen2]}
    """
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        keywords = request.POST.get('keywords')

        try:
            game_id = int(game_id)
            keywords = json.loads(keywords)

            text = GameId.objects.get(id=game_id).get_aggregated_text()

            sentences = nltk.data.load('tokenizers/punkt/english.pickle').tokenize(text)

            sentences_index = {}
            for sentence in enumerate(sentences):
                count = 0
                for keyword in keywords:
                    if keyword in sentence[1]:
                        count += 1
                sentences_index[sentence[0]] = count

            sentences_index = sorted(sentences_index.items(), key=operator.itemgetter(1), reverse=True)[:2]
            sentences = [sentences[s[0]] for s in sentences_index]
            return JsonResponse({'sentences': sentences}, status=200)

        except GameId.DoesNotExist:
            return JsonResponse({'msg': 'game_id not found'}, status=400)
        except ValueError:
            return JsonResponse({'msg': 'bad input.'}, status=400)
    else:
        return JsonResponse({'msg': 'json POST'}, status=400)


def get_containing_paragraphs(request):
    """
    like above but get paragraphs which given keywords most probably exists in.
    :param request: game_id --> paragraphs to be checked are selected from this game's texts.
                    keywords --> keywords to be searched for
    :return: {'paragraphs':[p1,p2]}
    """
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        keywords = request.POST.get('keywords')

        try:
            game_id = int(game_id)
            keywords = json.loads(keywords)

            text = GameId.objects.get(id=game_id).get_aggregated_text()

            paragraphs = text.split("\n")

            paragraphs_index = {}
            for paragraph in enumerate(paragraphs):
                count = 0
                for keyword in keywords:
                    if keyword in paragraph[1]:
                        count += 1
                paragraphs_index[paragraph[0]] = count

            paragraphs_index = sorted(paragraphs_index.items(), key=operator.itemgetter(1), reverse=True)[:2]
            paragraphs = [paragraphs[p[0]] for p in paragraphs_index]
            return JsonResponse({'paragraphs': paragraphs}, status=200)

        except GameId.DoesNotExist:
            return JsonResponse({'msg': 'game_id not found'}, status=400)
        except ValueError:
            return JsonResponse({'msg': 'bad input.'}, status=400)
    else:
        return JsonResponse({'msg': 'json POST'}, status=400)


def get_completed_sentence(request):
    """
    it searches for given regex in all texts of given game_id.

    :param request: game_id --> id of games. just this games texts will be searched against.
                    pattern --> regex to be searched for.
    :return: {'sentences':[sen1, sen2]}
    """
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        pattern = request.POST.get('pattern')

        try:
            game_id = int(game_id)
            game_id = GameId.objects.get(id=game_id)

            texts = game_id.get_aggregated_text()
            sentences = nltk.data.load('tokenizers/punkt/english.pickle').tokenize(texts)
            out = []
            for sentence in sentences:
                if nltk.re.search(pattern, sentence) is not None:
                    out.append(sentence)

            return JsonResponse({'sentences': out}, status=200)

        except GameId.DoesNotExist:
            return JsonResponse({'msg': 'game_id not found'}, status=400)
        except ValueError:
            return JsonResponse({'msg': 'bad input'}, status=400)
        except TypeError:
            return JsonResponse({'msg': 'bad input'}, status=400)
    else:
        return JsonResponse({'msg': 'just POST'}, status=400)


def is_sentence_complete(request):
    """
    it searches for exact match of given sentence in this game's texts.

    :param request: game_id
                    sentence --> sentence to be searched for
    :return: {'is_sentence_correct':true} | {'is_sentence_correct':false}
    """
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        sentence = request.POST.get('sentence')

        try:
            game_id = int(game_id)
            game_id = GameId.objects.get(id=game_id)

            texts = game_id.get_aggregated_text()
            sentences = nltk.data.load('tokenizers/punkt/english.pickle').tokenize(texts)
            for s in sentences:
                if s == sentence:
                    return JsonResponse({'is_sentence_correct': True}, status=200)

            return JsonResponse({'is_sentence_correct': False}, status=200)

        except GameId.DoesNotExist:
            return JsonResponse({'msg': 'game_id not found'}, status=400)
        except ValueError:
            return JsonResponse({'msg': 'bad input'}, status=400)
        except TypeError:
            return JsonResponse({'msg': 'bad input'}, status=400)
    else:
        return JsonResponse({'msg': 'just POST'}, status=400)


def get_topics(request):
    """
    it searches for exact match of given sentence in this game's texts.

    :param request: game_id
                    sentence --> sentence to be searched for
    :return: {'is_sentence_correct':true} | {'is_sentence_correct':false}
    """
    return JsonResponse({'topics': [topic.topic for topic in Topic.objects.all()]}, status=200)


def add_site(request):
    """
    Adds site to DB.

    :param request: topic
                    url
    :return: {'msg':'site added successfully' }
    """
    if request.method == 'POST':
        url = request.POST.get('url', '')
        topic = request.POST.get('topic', '')

        if len(url) <1 or len(topic)<1:
            return JsonResponse({'msg':'bad input.'}, status=400)

        topic = Topic(topic=topic).get_and_insert()
        Site(url=url, topic=topic).save()

        return JsonResponse({'msg':'added succ.'}, status=200)

    else:
        return JsonResponse({'msg': 'just POST'}, status=400)

def get_sites(request):
    response = []
    for topic in Topic.objects.all():
        sites = {}
        sites['topic'] = topic.topic
        sites['urls'] = [site.url for site in topic.sites.all()]

        response.append(sites)

    return JsonResponse({'sites':response}, status=200)