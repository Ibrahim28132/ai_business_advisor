from typing import Dict, List, Optional
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from utils.config import config
from utils.logging import logger


class WebSearchTool:
    def __init__(self):
        self.client = TavilySearch(api_key=config.TAVILY_API_KEY)

    @tool
    def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict:
        """
        Perform a web search using Tavily API.

        Returns:
            Dictionary containing search results
        """
        try:
            raw_response = self.client.run(query)

            # Ensure raw_response is a list of dicts
            if not isinstance(raw_response, list):
                logger.error(f"Tavily returned unexpected type: {type(raw_response)}")
                return {"error": "Unexpected response format from Tavily API."}

            results = raw_response[:max_results]

            formatted_answer = "\n\n".join(
                f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nSnippet: {r.get('content', '')}"
                for r in results
            )

            return {
                "answer": formatted_answer,
                "results": results,
                "related_questions": [],
                "follow_up_questions": self._generate_follow_ups(query, results)
            }

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {"error": str(e)}

    def _generate_follow_ups(self, query: str, results: List[Dict]) -> List[str]:
        """
        Generate 3 follow-up questions based on search results.
        """
        try:
            prompt = ChatPromptTemplate.from_template("""
            Based on the original query and search results, generate 3 relevant follow-up questions.

            Original Query: {query}
            Search Results: {results}

            Generate questions that would help deepen the understanding of the topic.
            Return only a bulleted list of questions, no additional commentary.
            """)

            chain = prompt | ChatOpenAI(model=config.MODEL_NAME, temperature=0.5)
            output = chain.invoke({
                "query": query,
                "results": str(results)
            })

            return output.content.strip().split("\n")
        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")
            return []
