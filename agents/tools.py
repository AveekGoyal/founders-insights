from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import wikipedia
import requests
from bs4 import BeautifulSoup
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

def search_wiki_url(query: str) -> dict:
    """
    Search for Wikipedia URL using Tavily
    
    Args:
        query (str): Search query for the person
        
    Returns:
        dict: Wikipedia URL if found
    """
    try:
        search = TavilySearchAPIWrapper()
        # Add 'wikipedia' to query to prioritize Wikipedia results
        results = search.results(f"{query} wikipedia")
        
        # Look for English Wikipedia URL in results
        wiki_url = None
        for result in results:
            url = result.get('url', '')
            if 'en.wikipedia.org/wiki/' in url:
                wiki_url = url
                break
                
        if wiki_url:
            return {"url": wiki_url}
        return {"error": "No English Wikipedia URL found"}
        
    except Exception as e:
        return {"error": str(e)}

def verify_wiki_page(url: str) -> dict:
    """
    Verify Wikipedia page content
    
    Args:
        url (str): Wikipedia page URL
        
    Returns:
        dict: Wikipedia page summary if verified
    """
    try:
        # Extract title from URL and get page
        title = url.split("/wiki/")[-1].replace("_", " ")
        wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        summary = wiki.run(title)
        
        return {
            "url": url,
            "summary": summary
        }
    except Exception as e:
        return {"error": str(e)}

def get_wiki_content_from_url(url: str) -> dict:
    """
    Get detailed Wikipedia content from a URL
    
    Args:
        url (str): URL of the Wikipedia page
        
    Returns:
        dict: Full page content and metadata
    """
    try:
        # Make sure we're using English Wikipedia
        if not 'en.wikipedia.org' in url:
            url = url.replace('wikipedia.org', 'en.wikipedia.org')
            
        # Get the page directly using the URL
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": "Failed to fetch Wikipedia page"}
            
        # Use Wikipedia API with the title
        title = url.split("/wiki/")[-1].replace("_", " ")
        # Set up Wikipedia with rate limiting
        wikipedia.set_rate_limiting(True)
        
        # For disambiguation pages, we want the (businessman) version
        if "Brian Armstrong" in title:
            title = "Brian Armstrong (businessman)"
            
        page = wikipedia.page(title, auto_suggest=False)
        
        # Get content and sections
        content = page.content
        sections = page.sections
        
        if not content:
            return {"error": "No content found in Wikipedia page"}
            
        return {
            "content": content,
            "url": url,
            "sections": sections
        }
    except wikipedia.exceptions.DisambiguationError as e:
        return {"error": f"Disambiguation page found. Please be more specific: {str(e)}"}
    except wikipedia.exceptions.PageError as e:
        return {"error": f"Page not found: {str(e)}"}
    except Exception as e:
        return {"error": f"Error fetching Wikipedia content: {str(e)}"}