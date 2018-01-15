# -*- coding: utf-8 -*-
import requests
import re
import os
import codecs

SITE_ADDR = 'https://www.eslfast.com/robot'
def parse_topic_pages():
    r = requests.get(SITE_ADDR)
    return re.findall('<a href="(.*)">.*\. (.*)</a>', r.text)

def parse_subtopic_pages(url):
    r = requests.get(url)
    return re.findall('<a href="(.*)">.*</a>', r.text)
def parse_page(url):
    r = requests.get(url)
    text = []
    texts = []
    for line in r.text.split('\n'):
        line = line.lstrip()
        if len(line) == 0:
            if len(text) >0 :
                texts.append(' '.join(text))
            text = []
        if line.startswith('<b>'):
            text.append(line.replace('<b>', '').replace('</b>', '').replace('<br>',''))

    return texts

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


topics = parse_topic_pages()
for topic in topics:
    subtopic_url = '%s/%s'%(SITE_ADDR, topic[0])
    topic_title = topic[1]
    print topic_title

    make_dir(topic_title)

    n = 1
    subtopics=parse_subtopic_pages(subtopic_url)
    for subtopic in subtopics:
        print '\t',subtopic
        page_url = '%s/%s'%( re.findall('(.*)\/.*', subtopic_url)[0],subtopic)
        for text in parse_page(page_url):
            with codecs.open(os.path.join(topic_title, str(n)), 'w', encoding='utf-8') as f:
                f.write(text)
            n+=1

    print topic_title, '\t:\t', n
