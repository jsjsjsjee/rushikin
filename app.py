from flask import Flask, request, render_template
import wikipediaapi
import wikipedia
import time  # Add this for rate limiting

app = Flask(__name__)

def fetch_wikipedia_data(topic):
    """Fetches detailed information and images about a topic from Wikipedia."""
    try:
        # Set up Wikipedia API with user agent
        user_agent = "WikipediaSearchApp/1.0 (your-email@example.com)"  # Change this to your email
        wiki_wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent=user_agent
        )
        
        # Search for the page with better error handling
        try:
            page = wiki_wiki.page(topic)
            if not page.exists():
                # Try searching with Wikipedia's search function
                try:
                    search_results = wikipedia.search(topic)
                    if search_results:
                        topic = search_results[0]  # Use the first search result
                        page = wiki_wiki.page(topic)
                    else:
                        return {"text": f"No information found for '{topic}'.", "images": []}
                except Exception as e:
                    print(f"Search error: {e}")
                    return {"text": f"No information found for '{topic}'.", "images": []}
        except Exception as e:
            print(f"Page fetch error: {e}")
            return {"text": f"Error fetching information for '{topic}'.", "images": []}

        # Get the page text with better formatting
        try:
            text = page.text[:10000]
            if text:
                text = text + "..."
            else:
                text = "No text content available."
        except Exception as e:
            print(f"Text processing error: {e}")
            text = "Error processing text content."

        # Fetch images with better error handling
        images = []
        try:
            wikipedia.set_user_agent(user_agent)
            time.sleep(1)  # Add small delay to prevent rate limiting
            wiki_page = wikipedia.page(topic, auto_suggest=False)
            
            # Filter for valid image URLs
            images = [
                img for img in wiki_page.images
                if any(img.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
                and not img.lower().endswith('.svg')
                and ('commons' in img.lower() or 'wikipedia' in img.lower())
            ][:5]  # Limit to 5 images
            
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Disambiguation error: {e}")
            # Try to use the first suggestion
            try:
                wiki_page = wikipedia.page(e.options[0], auto_suggest=False)
                images = [
                    img for img in wiki_page.images
                    if any(img.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
                    and not img.lower().endswith('.svg')
                    and ('commons' in img.lower() or 'wikipedia' in img.lower())
                ][:5]
            except Exception as sub_e:
                print(f"Sub-error in disambiguation handling: {sub_e}")
                
        except Exception as e:
            print(f"Image fetch error: {e}")
        
        return {
            "text": text,
            "images": images
        }
    
    except Exception as e:
        print(f"Main error in fetch_wikipedia_data: {e}")
        return {"text": "An error occurred while fetching data.", "images": []}

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle both GET and POST requests to the main page."""
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        if not topic:
            return render_template('index.html', error="Please enter a topic to search.")
        
        try:
            data = fetch_wikipedia_data(topic)
            if not data['text'] or data['text'] == "An error occurred while fetching data.":
                return render_template('index.html', 
                                    error=f"No information found for '{topic}'. Please try another search term.")
            
            print(f"Found {len(data['images'])} images for topic: {topic}")  # Debug info
            return render_template('index.html', topic=topic, data=data)
            
        except Exception as e:
            print(f"Error processing request: {e}")
            return render_template('index.html', 
                                error="An error occurred. Please try again with a different search term.")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
