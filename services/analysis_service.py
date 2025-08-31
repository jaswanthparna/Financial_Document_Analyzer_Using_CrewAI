from typing import Dict, Any, List
import google.generativeai as genai
import os
import re
import json
import logging
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class FinancialAnalysisService:
    """AI-powered financial document analysis service."""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Financial Analysis Service initialized")

    def analyze_document(self, file_content: bytes, filename: str, query: str) -> Dict[str, Any]:
        """Complete financial document analysis."""
        try:
            # Extract text from PDF
            text = self._extract_pdf_text(file_content)
            
            # Extract company name
            company_name = self._extract_company_name(text, filename)
            
            # Extract financial metrics
            financial_metrics = self._extract_financial_metrics(text)
            
            # Generate investment recommendations
            investment_recommendations = self._generate_investment_recommendations(text, financial_metrics, query)
            
            # Assess risks
            risk_assessments = self._assess_risks(text, financial_metrics)
            
            # Get market insights
            market_insights = self._get_market_insights(company_name, text)
            
            # Generate summary
            summary = self._generate_summary(financial_metrics, company_name, query)
            
            return {
                "company_name": company_name,
                "financial_metrics": financial_metrics,
                "investment_recommendations": investment_recommendations,
                "risk_assessments": risk_assessments,
                "market_insights": market_insights,
                "summary": summary,
                "query_response": self._answer_specific_query(text, query, financial_metrics)
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise

    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF bytes."""
        temp_path = f"data/temp_{os.getpid()}.pdf"
        try:
            with open(temp_path, "wb") as f:
                f.write(file_content)
            
            reader = PdfReader(temp_path)
            text = ""
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _extract_company_name(self, text: str, filename: str) -> str:
        """Extract company name using AI."""
        try:
            prompt = f"""
            Extract the company name from this financial document. Return only the company name.
            
            Document text (first 1000 characters):
            {text[:1000]}
            
            Filename: {filename}
            """
            
            response = self.model.generate_content(prompt)
            company_name = response.text.strip()
            
            # Validate response
            if len(company_name) < 100 and company_name:
                return company_name
                
        except Exception as e:
            logger.warning(f"AI company extraction failed: {str(e)}")
        
        # Fallback to filename
        return filename.replace('.pdf', '').replace('_', ' ').title()

    def _extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """Extract financial metrics using AI."""
        try:
            prompt = f"""
            Extract key financial metrics from this document. Return JSON format:
            {{
                "revenue": <number in millions>,
                "net_income": <number in millions>,
                "total_assets": <number in millions>,
                "operating_cash_flow": <number in millions>,
                "profit_margin": <percentage>,
                "debt_to_equity": <ratio>,
                "eps": <earnings per share>
            }}
            
            Document text: {text[:8000]}
            """
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response.text)
            if json_match:
                metrics = json.loads(json_match.group())
                return metrics
                
        except Exception as e:
            logger.warning(f"AI metrics extraction failed: {str(e)}")
        
        return {}

    def _generate_investment_recommendations(self, text: str, metrics: Dict, query: str) -> List[Dict[str, Any]]:
        """Generate investment recommendations using AI."""
        try:
            prompt = f"""
            Based on this financial data, provide 2-3 investment recommendations.
            
            Financial Metrics: {json.dumps(metrics)}
            User Query: {query}
            
            Return JSON array:
            [{{
                "action": "buy/sell/hold",
                "asset": "specific asset",
                "rationale": "detailed reasoning",
                "risk_level": "Low/Medium/High",
                "confidence": 0.0-1.0
            }}]
            
            Document context: {text[:3000]}
            """
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON array
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                return recommendations
                
        except Exception as e:
            logger.warning(f"AI recommendation generation failed: {str(e)}")
        
        # Fallback recommendations
        return [
            {
                "action": "monitor",
                "asset": "Company stock",
                "rationale": "Requires further analysis based on available metrics",
                "risk_level": "Medium",
                "confidence": 0.5
            }
        ]

    def _assess_risks(self, text: str, metrics: Dict) -> List[Dict[str, Any]]:
        """Assess investment risks using AI."""
        try:
            prompt = f"""
            Analyze risks based on this financial data. Return JSON array:
            [{{
                "category": "Financial/Market/Operational",
                "level": "Low/Medium/High",
                "description": "risk description",
                "mitigation": "mitigation strategy"
            }}]
            
            Financial Metrics: {json.dumps(metrics)}
            Document context: {text[:3000]}
            """
            
            response = self.model.generate_content(prompt)
            
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                risks = json.loads(json_match.group())
                return risks
                
        except Exception as e:
            logger.warning(f"AI risk assessment failed: {str(e)}")
        
        # Fallback risks
        return [
            {
                "category": "Market Risk",
                "level": "Medium",
                "description": "General market volatility affects all investments",
                "mitigation": "Diversify portfolio and maintain long-term perspective"
            }
        ]

    def _get_market_insights(self, company_name: str, text: str) -> List[str]:
        """Generate market insights using AI."""
        try:
            prompt = f"""
            Provide 3-5 key market insights for {company_name} based on this financial document.
            Return as JSON array of strings.
            
            Document context: {text[:2000]}
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to extract JSON array
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
                return insights
            
            # If not JSON, split by lines
            insights = [line.strip() for line in response.text.split('\n') if line.strip()]
            return insights[:5]
            
        except Exception as e:
            logger.warning(f"Market insights generation failed: {str(e)}")
        
        return ["Market analysis requires additional data"]

    def _generate_summary(self, metrics: Dict, company: str, query: str) -> str:
        """Generate analysis summary."""
        revenue = metrics.get('revenue', 'N/A')
        net_income = metrics.get('net_income', 'N/A')
        
        return f"""
        Financial Analysis Summary for {company}:
        
        Key Performance: Revenue of ${revenue}M and net income of ${net_income}M demonstrate the company's current financial position.
        
        Analysis Focus: This evaluation addresses your query: "{query}" by examining core financial metrics and operational performance.
        
        Investment Perspective: Based on available data, the company shows measurable financial indicators that inform strategic investment decisions.
        """

    def _answer_specific_query(self, text: str, query: str, metrics: Dict) -> str:
        """Answer user's specific query using AI."""
        try:
            prompt = f"""
            User asked: "{query}"
            
            Financial metrics: {json.dumps(metrics)}
            
            Provide a detailed answer to their specific question based on the document.
            
            Document excerpt: {text[:3000]}
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"Query-specific analysis failed: {str(e)}")
            return f"Unable to provide specific analysis for query: {query}"