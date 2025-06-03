import requests
from html.parser import HTMLParser
import urllib.parse
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

class DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.in_table = False
        self.row_links = []
        self.row_text = []
        self.in_link = False
        self.href = ""
        
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'a' and self.in_table:
            self.in_link = True
            for name, value in attrs:
                if name == 'href' and '/l/?uddg=' in value:
                    self.href = urllib.parse.unquote(value.split('uddg=')[1].split('&')[0])
                    break
    
    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'a' and self.in_link:
            self.in_link = False
            if self.href:
                self.row_links.append(self.href)
                self.href = ""
        elif tag == 'tr' and self.in_table:
            if self.row_links and self.row_text:
                url = self.row_links[0]
                if 'http' in url and 'duckduckgo.com' not in url:
                    self.results.append({
                        'title': self.row_text[0] if self.row_text else '',
                        'url': url,
                        'snippet': ' '.join(self.row_text[1:]) if len(self.row_text) > 1 else ''
                    })
            self.row_links = []
            self.row_text = []
    
    def handle_data(self, data):
        if self.in_table and data.strip():
            self.row_text.append(data.strip())

def search_web(query: str) -> dict:
    """Searches the web using DuckDuckGo for the specified query.

    Args:
        query (str): The search query to execute.

    Returns:
        dict: status and search results or error message.
    """
    try:
        response = requests.get(
            "https://lite.duckduckgo.com/lite/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        response.raise_for_status()
        
        parser = DDGParser()
        parser.feed(response.text)
        
        if parser.results:
            # Format results as a readable string
            results_text = f"Search results for '{query}':\n\n"
            for i, result in enumerate(parser.results[:5], 1):
                results_text += f"{i}. {result['title']}\n"
                results_text += f"   URL: {result['url']}\n"
                if result['snippet']:
                    results_text += f"   {result['snippet']}\n"
                results_text += "\n"
            
            return {
                "status": "success",
                "report": results_text.strip()
            }
        else:
            return {
                "status": "error",
                "error_message": f"No search results found for '{query}'."
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Search failed: {str(e)}"
        }

# Example agent setup
root_agent = Agent(
    name="web_search_agent",
    model=LiteLlm(model="ollama_chat/qwen3:14b"),
    description="Agent that can search the web for information.",
    instruction="You are a helpful agent who can search the web to find current information and answer user questions.",
    tools=[search_web],
)


