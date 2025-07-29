from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from utils.config import config
from utils.logging import logger
from utils.file_operations import save_as_text  # Use new function instead

class WriterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        self.prompt = self._create_prompt()

    def _create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", """
            You are StartSmart Writer, an expert in creating professional business documents. Your tasks:
            1. Compile all research, analysis, and strategy into a cohesive business plan
            2. Structure the document professionally with clear sections
            3. Use appropriate business language and tone
            4. Include relevant data and visuals
            5. Format for readability and professionalism

            Document Structure:
            1. Executive Summary
            2. Business Description
            3. Market Analysis
            4. Competitive Analysis
            5. Target Customer Profile
            6. Revenue Models
            7. Marketing & Growth Strategy
            8. Operational Plan
            9. Risk Analysis
            10. Financial Projections (if data available)

            Guidelines:
            - Be concise but comprehensive
            - Use headings and bullet points for readability
            - Include key data points and visuals
            - Maintain consistent formatting
            """),
            ("human", "{input}"),
        ])

    def create_business_plan(self, all_data: Dict) -> Dict:
        try:
            input_text = f"""
            Please create a professional business plan using the following data:

            Research Findings:
            {all_data.get('research', {})}

            Market Analysis:
            {all_data.get('analysis', {})}

            Business Strategies:
            {all_data.get('strategy', {})}

            Additional Context:
            {all_data.get('context', {})}
            """

            chain = self.prompt | self.llm
            response = chain.invoke({"input": input_text})
            plan_text = response.content

            try:
                file_path = save_as_text(plan_text, "business_plan")  # Save as .txt instead
            except Exception as text_error:
                logger.error(f"Failed to save business plan as text: {text_error}")
                file_path = None

            return {
                "business_plan": plan_text,
                "file_path": file_path
            }

        except Exception as e:
            logger.error(f"Business plan creation failed: {e}")
            return {
                "business_plan": None,
                "file_path": None,
                "error": str(e)
            }
