from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from utils.config import config
from utils.logging import logger


class CriticAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        self.prompt = self._create_prompt()

    def _create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", """
            You are StartSmart Critic, a quality assurance expert for business plans. Your role:
            1. Review the business plan for completeness and quality
            2. Identify gaps, weaknesses, or areas needing improvement
            3. Suggest enhancements to strengthen the plan
            4. Ensure all claims are supported by data
            5. Check for logical consistency throughout

            Focus Areas:
            - Market analysis completeness
            - Competitive differentiation
            - Revenue model viability
            - Growth strategy feasibility
            - Risk assessment adequacy
            - Financial projection realism (if included)

            Guidelines:
            - Be constructive in your feedback
            - Prioritize the most important issues
            - Provide specific suggestions for improvement
            - Consider both short-term and long-term implications
            - Rate the plan on a scale of 1-10 based on completeness, feasibility, and clarity
            """),
            ("human", "{input}"),
        ])

    def review_plan(self, business_plan: Dict) -> Dict:
        """
        Review and provide feedback on the business plan.

        Args:
            business_plan: The business plan document to review

        Returns:
            Dictionary containing review results and feedback
        """
        try:
            input_text = f"""
            Please review this business plan and provide constructive feedback, including a rating (1-10):

            {business_plan.get('business_plan', '')}
            """

            chain = self.prompt | self.llm
            response = chain.invoke({"input": input_text})

            return {
                "feedback": response.content,
                "rating": self._rate_plan(response.content),
                "improvement_suggestions": self._extract_suggestions(response.content)
            }

        except Exception as e:
            logger.error(f"Plan review failed: {e}")
            return {"error": str(e)}

    def _rate_plan(self, feedback: str) -> int:
        """Rate the business plan quality based on feedback (1-10 scale)."""
        positive_keywords = ["comprehensive", "clear", "strong", "well-supported", "feasible"]
        negative_keywords = ["missing", "unclear", "weak", "incomplete", "unrealistic"]

        feedback_lower = feedback.lower()
        positive_count = sum(1 for word in positive_keywords if word in feedback_lower)
        negative_count = sum(1 for word in negative_keywords if word in feedback_lower)

        rating = 5 + positive_count - negative_count
        return max(1, min(10, rating))

    def _extract_suggestions(self, feedback: str) -> List[str]:
        """Extract specific improvement suggestions from feedback."""
        suggestions = [line.strip('- *1234567890. ') for line in feedback.split('\n')
                       if line.strip().startswith(('-', '*', '1.', '2.', '3.'))]
        return suggestions if suggestions else [
            "Add more data to support market size claims",
            "Clarify the unique value proposition",
            "Include 12-month financial projections if possible"
        ]