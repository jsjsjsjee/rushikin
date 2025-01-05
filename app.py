from flask import Flask, request, render_template
import wikipediaapi
import wikipedia
import time
import os

app = Flask(__name__)

def fetch_wikipedia_data(topic):
    """Fetches detailed information and images about a topic from Wikipedia."""
    try:
        # Set up Wikipedia API with correct user agent format
        user_agent = "RushikSearch/1.0 (rushiksearch@example.com)"
        wiki_wiki = wikipediaapi.Wikipedia(
            'en',  # language
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            headers={'User-Agent': user_agent}  # Correct way to set user agent
        )
        
        try:
            # First try direct page access
            page = wiki_wiki.page(topic)
            
            if not page.exists():
                # Try Wikipedia search
                search_results = wikipedia.search(topic, results=1)
                if search_results:
                    page = wiki_wiki.page(search_results[0])
                else:
                    return {"text": f"No information found for '{topic}'.", "images": []}
            
            # Get text content
            text = page.text[:10000] + "..." if page.text else "No content available."
            
            # Get images with retry mechanism
            max_retries = 3
            images = []
            for attempt in range(max_retries):
                try:
                    # Set user agent for wikipedia package
                    wikipedia.set_user_agent(user_agent)
                    wiki_page = wikipedia.page(topic, auto_suggest=True)
                    
                    # Filter images
                    images = [
                        img for img in wiki_page.images
                        if any(img.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
                        and not img.lower().endswith('.svg')
                    ][:5]
                    break
                except wikipedia.exceptions.PageError:
                    print(f"Page not found for '{topic}'")
                    break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
            
            return {
                "text": text,
                "images": images
            }
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages
            try:
                first_option = e.options[0]
                page = wiki_wiki.page(first_option)
                text = page.text[:10000] + "..."
                
                wiki_page = wikipedia.page(first_option, auto_suggest=False)
                images = [
                    img for img in wiki_page.images
                    if any(img.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
                    and not img.lower().endswith('.svg')
                ][:5]
                
                return {
                    "text": text,
                    "images": images
                }
            except Exception as sub_e:
                print(f"Disambiguation handling error: {sub_e}")
                return {"text": f"Multiple topics found for '{topic}'. Please be more specific.", "images": []}
                
        except wikipedia.exceptions.PageError:
            return {"text": f"No information found for '{topic}'.", "images": []}
            
    except Exception as e:
        print(f"Error in fetch_wikipedia_data: {e}")
        return {"text": f"An error occurred while fetching data for '{topic}'.", "images": []}

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle both GET and POST requests to the main page."""
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        if not topic:
            return render_template('index.html', error="Please enter a topic to search.")
        
        try:
            data = fetch_wikipedia_data(topic)
            return render_template('index.html', topic=topic, data=data)
        except Exception as e:
            print(f"Error processing request: {e}")
            return render_template('index.html', error="An error occurred. Please try again.")
    
    return render_template('index.html')

if __name__ == '__main__':
    # Get port from environment variable or default to 10000
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
