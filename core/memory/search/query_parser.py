"""
Query Parser — Analyzes and expands search queries.

Responsibilities:
  - Parse user query
  - Expand synonyms (Persian ↔ English)
  - Extract keywords
  - Detect query intent

Does NOT:
  - Search (KeywordSearch does that)
  - Rank (MemoryRanker does that)
"""

from typing import List, Set


# Persian ↔ English synonym map
SYNONYMS = {
    "پروژه": ["project", "atlas"],
    "حافظه": ["memory", "remember"],
    "خطا": ["error", "bug", "issue"],
    "کاربر": ["user", "person"],
    "جستجو": ["search", "find"],
    "برنامه": ["code", "program", "python"],
    "سیستم": ["system", "os"],
    "هوش مصنوعی": ["ai", "artificial intelligence", "model"],
    "ذخیره": ["save", "store"],
    "بازیابی": ["retrieve", "load"],
    "حذف": ["delete", "remove"],
    "بروزرسانی": ["update", "modify"],
}


class QueryParser:
    """
    Parses and expands search queries.

    Usage:
        parser = QueryParser()
        terms = parser.expand("پروژه Atlas")
        # Returns: ["پروژه", "Atlas", "project", "atlas"]
    """

    def __init__(self, synonyms=None):
        """
        Args:
            synonyms: Custom synonym map (optional)
        """
        self._synonyms = synonyms or SYNONYMS

    def parse(self, query: str) -> dict:
        """
        Parse a query into components.

        Returns:
            {
                "original": str,
                "keywords": List[str],
                "expanded": List[str],
                "is_persian": bool,
            }
        """
        keywords = self._extract_keywords(query)
        expanded = self.expand(query)
        is_persian = self._is_persian(query)

        return {
            "original": query,
            "keywords": keywords,
            "expanded": expanded,
            "is_persian": is_persian,
        }

    def expand(self, query: str) -> List[str]:
        """
        Expand query with synonyms.

        Args:
            query: Original query

        Returns:
            List of expanded terms (including original)
        """
        terms = {query}
        query_lower = query.lower()

        for persian, english_list in self._synonyms.items():
            if persian in query:
                terms.update(english_list)
            for eng in english_list:
                if eng in query_lower:
                    terms.add(persian)
                    terms.update(e for e in english_list if e != eng)
                    break

        return list(terms)

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract individual keywords from query."""
        return [w.strip() for w in query.split() if w.strip()]

    def _is_persian(self, text: str) -> bool:
        """Check if text contains Persian characters."""
        persian_ranges = [
            (0x0600, 0x06FF),  # Arabic
            (0x0750, 0x077F),  # Arabic Supplement
            (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        ]
        for char in text:
            code = ord(char)
            for start, end in persian_ranges:
                if start <= code <= end:
                    return True
        return False
