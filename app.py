from flask import Flask, request, render_template
import wikipediaapi
import wikipedia

app = Flask(__name__)

def fetch_wikipedia_data(topic):
    """Fetches detailed information and images about a topic from Wikipedia."""
    try:
        # Set up Wikipedia API with user agent
        user_agent = "WikipediaSearchApp/1.0 (rushikesh@example.com)"
        wiki_wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent=user_agent
        )
        
        # Search for the page
        page = wiki_wiki.page(topic)
        
        if not page.exists():
            # Try with "(actor)" suffix if the main topic isn't found
            page = wiki_wiki.page(f"{topic} (actor)")
            if not page.exists():
                return {"text": "No information found.", "images": []}

        # Get the page text
        text = page.text[:10000] + "..."  # Limit text length for better display
        
        # Fetch images
        try:
            wikipedia.set_user_agent(user_agent)
            wiki_page = wikipedia.page(topic)
            # Filter for valid image URLs
            images = [
                img for img in wiki_page.images
                if img.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
                and not img.lower().endswith('.svg')
                and 'commons' in img.lower()  # Only get Wikimedia Commons images
            ]
        except Exception as e:
            print(f"Error fetching images: {e}")
            images = []
        
        return {
            "text": text,
            "images": images[:5]  # Limit to 5 images
        }
    
    except Exception as e:
        print(f"Error in fetch_wikipedia_data: {e}")
        return {"text": "An error occurred while fetching data.", "images": []}

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle both GET and POST requests to the main page."""
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        if topic:
            try:
                data = fetch_wikipedia_data(topic)
                print(f"Found {len(data['images'])} images for topic: {topic}")  # Debug info
                return render_template('index.html', topic=topic, data=data)
            except Exception as e:
                print(f"Error processing request: {e}")
                return render_template('index.html', error="An error occurred while processing your request.")
        else:
            return render_template('index.html', error="Please enter a topic to search.")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)