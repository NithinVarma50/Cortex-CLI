import requests
from bs4 import BeautifulSoup
from skills.base_skill import BaseSkill


class WebSearchSkill(BaseSkill):
    name: str = "web_search"
    description: str = "Search the web using DuckDuckGo to find information."
    version: str = "1.0.0"

    def execute(self, input_text: str, **kwargs) -> str:
        if not self.validate_input(input_text):
            return "Invalid search query."

        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        data = {"q": input_text}
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("div", class_="result")
            
            output = []
            for result in results[:5]:  # Top 5 results
                title_elem = result.find("a", class_="result__url")
                snippet_elem = result.find("a", class_="result__snippet")
                
                if title_elem and snippet_elem:
                    title = title_elem.text.strip()
                    url = title_elem.get("href", "")
                    snippet = snippet_elem.text.strip()
                    output.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}\n")
                    
            if not output:
                return "No useful results found."
                
            return "\n".join(output)
            
        except Exception as e:
            return f"Search failed: {str(e)}"
