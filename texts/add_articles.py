import os

topics = os.walk('.').next()[1]

for topic in topics:
    texts = os.walk(topic)
    for text in texts:
        print text
