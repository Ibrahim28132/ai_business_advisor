from typing import Dict, List
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from utils.config import config
from utils.logging import logger

class ResearchAgent:
    def __init__(self):
        self.client = TavilySearch(api_key=config.TAVILY_API_KEY)

    def conduct_research(self, query: str, max_results: int = 5) -> Dict:
        """
        Conducts research using TavilySearch and returns structured results.
        """
        try:
            response = self.client.run(query)

            results = response.get("results", [])
            if not isinstance(results, list):
                logger.error(f"Expected 'results' to be a list, got: {type(results)}")
                return {"error": "Unexpected results format from TavilySearch"}

            top_results = results[:max_results]

            summary_text = "\n\n".join(
                f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nSnippet: {r.get('content', '')}"
                for r in top_results
            )

            return {
                "results": top_results,
                "answer": summary_text,
                "related_questions": [],
                "follow_up_questions": self._generate_follow_ups(query, summary_text),
            }

        except Exception as e:
            logger.error(f"Research failed: {e}")
            return {"error": str(e)}

    def _generate_follow_ups(self, query: str, context: str) -> List[str]:
        try:
            prompt = ChatPromptTemplate.from_template("""
            Based on the following business research, suggest 3 intelligent follow-up questions to guide deeper research.

            Original Query: {query}

            Research Summary:
            {context}

            Provide the questions as a bulleted list.
            """)

            chain = prompt | ChatOpenAI(model=config.MODEL_NAME, temperature=0.3)
            output = chain.invoke({
                "query": query,
                "context": context
            })

            return output.content.strip().split("\n")

        except Exception as e:
            logger.error(f"Failed to generate follow-ups: {e}")
            return []
