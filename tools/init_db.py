import requests
import os

SERVER_ADDR = 'http://localhost:8000/text_parser/add_article'
for dirname in os.walk('.'):
    if dirname[0] != '.':
        print dirname[0][2:]
        for texts in os.walk(dirname[0]):
            for text_name in texts[2]:
                with open(os.path.join(dirname[0],text_name),'r') as text:
                    r = requests.post(SERVER_ADDR, data={'topic':dirname[0][2:], 'text':text.read()})
                    print '\t', text_name, ':', r.status_code

