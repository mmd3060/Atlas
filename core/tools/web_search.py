"""
Web Search Tool — Atlas can search the internet.
Uses DuckDuckGo HTML + API + Wikipedia (all free, no API key needed).
"""

import re
import urllib.parse
from typing import Any, Dict, Optional

import requests


class WebSearchTool:
    """Search the web for real-time information."""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Mobile Safari/537.36"
        )
    }
    MAX_RESULTS = 5

    def search(self, query: str) -> Dict[str, Any]:
        """Search the internet for a query."""
        results = {
            "query": query,
            "sources": [],
            "answer": None,
            "related_topics": [],
            "failed": True,
        }

        # 1. DuckDuckGo Instant Answer API
        try:
            ddg_answer = self._search_ddg_api(query)
            if ddg_answer:
                results["answer"] = ddg_answer
                results["sources"].append({"provider": "DuckDuckGo", "status": "ok"})
                results["failed"] = False
        except Exception:
            results["sources"].append({"provider": "DuckDuckGo API", "status": "failed"})

        # 2. DuckDuckGo HTML search (fallback)
        if results["failed"]:
            try:
                html_answer = self._search_ddg_html(query)
                if html_answer:
                    results["answer"] = html_answer
                    results["sources"].append({"provider": "DuckDuckGo HTML", "status": "ok"})
                    results["failed"] = False
            except Exception:
                pass

        # 3. Wikipedia (always try, even if DDG worked)
        try:
            wiki_answer = self._search_wikipedia(query)
            if wiki_answer:
                results["answer"] = wiki_answer
                results["sources"].append({"provider": "Wikipedia", "status": "ok"})
                results["failed"] = False
        except Exception:
            pass

        if results["failed"]:
            results["answer"] = f"No results found for '{query}'"

        return results

    def _search_ddg_api(self, query: str) -> Optional[str]:
        """DuckDuckGo Instant Answer API."""
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        response = requests.get(
            "https://api.duckduckgo.com/",
            params=params,
            headers=self.HEADERS,
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            abstract = data.get("Abstract", "")
            if abstract:
                return abstract
            # Check RelatedTopics for an answer
            topics = data.get("RelatedTopics", [])
            for t in topics:
                if isinstance(t, dict) and t.get("Text"):
                    return t["Text"]
        return None

    def _search_ddg_html(self, query: str) -> Optional[str]:
        """DuckDuckGo HTML scrape."""
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        response = requests.get(url, headers=self.HEADERS, timeout=15)
        if response.status_code == 200:
            match = re.search(
                r'class="result__a" href=".*?">(.*?)</a>',
                response.text,
                re.DOTALL,
            )
            if match:
                return re.sub(r"<[^>]+>", "", match.group(1)).strip()
        return None

    def _search_wikipedia(self, query: str) -> Optional[str]:
        """Wikipedia summary."""
        encoded = urllib.parse.quote(query)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        response = requests.get(url, headers=self.HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", None)
        return None

    def fetch_url(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL."""
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            return {
                "status": response.status_code,
                "content": response.text[:3000] if response.status_code == 200 else "",
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}",
            }
        except Exception as e:
            return {"status": 0, "content": "", "error": str(e)}