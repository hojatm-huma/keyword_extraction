# keyword_extraction
## What am I ?
This is a django app which extracts keywords from the given texts and stores them in a database. It was written to be the core of an English learning game. Codes of the game is not included here. 

### The game
In the game, gamers get a list of topics. After choosing a topic, a list of keywords of the topic is shown to them. Gamers buy some of the keywords and then a text containing their chosen keywords is shown to them with some of them missing in the text. Gamers must fill in the blanks with the correct form of their chosen keywords.

### The code
This project is supposed to be the core of the game. It accepts texts from the admin, parses them and extracts their keywords and store the texts and their keyword in the database.

In order to parse the texts and extract keywords I used [keywordfinder] (https://github.com/lvsh/keywordfinder). This is a greate library thanks to lvsh. You can read its documantation in its page.

## API documantation
In the following, I describe APIs and their corresponding input output.

### add a text to database
It accepts a text and its topic, then parses it and stores the text and its keywords in the database.
```
POST /text_parser/add_article
```
**parameters:**

|  Name |  Type  | Description |
| ----- | ------ | ----------- |
| topic | string | topic of the text |
| text  | string | the text to be added |

### get available topics
It gives the topics existing in the database.
```
GET /text_parser/get_topics
```
**parameters:**

|  Name |  Type  | Description |
| ----- | ------ | ----------- |
| - | - | - |

### get keywords for a topic
It accepts a topic and return its keywords.
```
POST /text_parser/get_key_words
```
**parameters:**

|  Name |  Type  | Description |
| ----- | ------ | ----------- |
| topic | string | topic to get keywords from |

### start a new game
It accepts a topic and the gamer's chosen keywords. Then finds the texts containing most of the given keywords and store them as this game's text. Then returns the id of the game.
```
POST /text_parser/new_game
```
**parameters:**

|  Name |  Type  | Description |
| ----- | ------ | ----------- |
| topic | string | topic of the game |
| keywords  | array of strings | gamers' chosen keywords |

### get paragraphs containing most of the given keywords
It accepts a game_id and a list of keywords. Searches for paragraphs containing most of the keywords and return a sorted list of them.
```
POST /text_parser/get_containing_paragraph
```
**parameters:**

|  Name |  Type  | Description |
| ----- | ------ | ----------- |
| game_id | int | id of the game |
| keywords  | array of strings | gamers' chosen keywords |

### get completed sentence
It accepts a game_id and a regex. Searches through the text of the game and returns matchig sentences.
```
POST /text_parser/get_completed_sentece
```
**parameters:**

|  Name |  Type  | Description |
| ----- | ------ | ----------- |
| game_id | int | id of the game |
| sentence  | string | a regex to be searched for |
