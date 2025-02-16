from flask import Flask, render_template, request, jsonify
import wikipedia
from googletrans import Translator, LANGUAGES

app = Flask(__name__)
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/get_summary', methods=['POST'])
def get_summary():
    data = request.json
    query = data.get('query')
    target_language = data.get('language', 'en')
    
    try:
        # Detect language of the query
        query_language = translator.detect(query).lang
        print(f"Detected language: {query_language}")
        
        # Translate the query to English if it's not already in English
        if query_language != 'en':
            query_in_english = translator.translate(query, src=query_language, dest='en').text
        else:
            query_in_english = query
        print(f"Query in English: {query_in_english}")
        
        # Fetch summary in English
        summary = wikipedia.summary(query_in_english, sentences=3)
        page = wikipedia.page(query_in_english)
        
        # Translate the summary to the target language
        if target_language != 'en':
            translated_summary = translator.translate(summary, src='en', dest=target_language).text
        else:
            translated_summary = summary
        
        # Get the main image URL
        image_url = page.images[0] if page.images else None
    except wikipedia.exceptions.DisambiguationError as e:
        translated_summary = f"Your query is ambiguous, please be more specific. Possible options: {', '.join(e.options)}"
        image_url = None
    except wikipedia.exceptions.PageError:
        translated_summary = "The page does not exist, please try another query."
        image_url = None
    except Exception as e:
        translated_summary = f"An error occurred: {e}"
        image_url = None
    
    return jsonify({'summary': translated_summary, 'image_url': image_url})

if __name__ == '__main__':
    app.run(debug=True)
