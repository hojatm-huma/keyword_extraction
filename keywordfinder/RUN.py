#!/usr/bin/env python
# coding:utf-8
"""
Runs the keyword extraction algorithmn on an example
"""
__author__ = "Lavanya Sharan"

import sys
from keywordextraction import *


def main(text):
    # load keyword classifier
    preload = 1
    classifier_type = 'logistic'
    keyword_classifier = get_keywordclassifier(preload, classifier_type)['model']

    # extract top k keywords
    top_k = 15
    return extract_keywords(text, keyword_classifier, top_k, preload)