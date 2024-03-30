# test after 7 days
# a program that is suppose to generate app ideas
import requests

def query(word_type):
    # Set up Wordnik API parameters
    api_key = 'YOUR_API_KEY'  # Replace 'YOUR_API_KEY' with your actual API key
    base_url = 'http://api.wordnik.com/v4/words.json/randomWord'
    params = {
        'api_key': api_key,
        'includePartOfSpeech': word_type
    }

    # Make a request to the Wordnik API
    response = requests.get(base_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the word from the response
        word = response.json().get('word')
        if word:
            return word
        else:
            return "Error: No word found in API response"
    else:
        return "Error:", response.status_code

syntax = ["Article", "Noun", "Verb", "Article", "Noun", "Preposition",
          "Article", "Noun", "Preposition", "Adjective", "Noun", "Preposition",
          "Adjective", "Noun"]

sentence = ''
for word_type in syntax:
    word = query(word_type)
    sentence += " " + word

print(sentence)
