import os
import re
import json
import logging
from dotenv import load_dotenv
from pypdf import PdfReader
from crewai_tools import BaseTool
from typing import Optional, Dict, Any
import google.generativeai as genai

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini AI
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini AI initialized successfully")
    else:
        gemini_model = None
        logger.warning("GEMINI_API_KEY not found")
except Exception as e:
    logger.error(f"Failed to initialize Gemini: {str(e)}")
    gemini_model = None

class FinancialDocumentTool(BaseTool):
    name: str = "Financial PDF Analyzer"
    description: str = "Reads PDF financial documents and extracts financial data using AI analysis."

    def _run(self, path: str) -> dict:
        try:
            logger.info(f"Analyzing PDF: {path}")
            
            # Read PDF content
            reader = PdfReader(path)
            if not reader.pages:
                return {"error": "PDF has no pages"}

            full_text = ""
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    full_text += content + "\n"

            if not full_text:
                return {"error": "No text extracted from PDF"}

            # Extract company name
            company_name = self._extract_company_name(full_text, path)
            
            # Extract financial data using AI
            financial_data = self._extract_financial_data(full_text)
            
            return {
                "text": full_text,
                "company_name": company_name,
                "financial_data": financial_data,
                "page_count": len(reader.pages),
                "document_type": self._identify_document_type(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {"error": f"Error processing PDF: {str(e)}"}

    def _extract_company_name(self, text: str, filename: str) -> str:
        """Extract company name using AI or fallback methods."""
        if not gemini_model:
            return self._extract_company_name_regex(text, filename)
        
        try:
            prompt = f"""
            Extract the company name from this financial document. Return only the company name.
            
            Document text (first 1000 characters):
            {text[:1000]}
            """
            
            response = gemini_model.generate_content(prompt)
            company_name = response.text.strip()
            
            # Validate response
            if len(company_name) > 50 or not company_name:
                return self._extract_company_name_regex(text, filename)
            
            return company_name
            
        except Exception as e:
            logger.warning(f"AI company name extraction failed: {str(e)}")
            return self._extract_company_name_regex(text, filename)

    def _extract_company_name_regex(self, text: str, filename: str) -> str:
        """Fallback regex-based company name extraction."""
        # Common patterns for company names in financial documents
        patterns = [
            r'(?:^|\n)([A-Z][A-Za-z\s&,\.]+(?:Inc|Corp|Corporation|Company|Ltd|LLC)\.?)',
            r'Company[:\s]+([A-Z][A-Za-z\s&]+)',
            r'Corporation[:\s]+([A-Z][A-Za-z\s&]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # Fallback to filename
        return os.path.basename(filename).replace('.pdf', '').replace('_', ' ').title()

    def _extract_financial_data(self, text: str) -> dict:
        """Extract financial data using AI."""
        if not gemini_model:
            return {"status": "AI unavailable"}
        
        try:
            prompt = f"""
            Extract key financial metrics from this document. Return JSON:
            {{
                "revenue": <total revenue in millions>,
                "net_income": <net income in millions>,
                "operating_cash_flow": <operating cash flow in millions>,
                "total_assets": <total assets in millions>,
                "profit_margin": <profit margin percentage>,
                "debt_to_equity": <debt to equity ratio>,
                "eps": <earnings per share>
            }}

            Document text:
            {text[:8000]}
            """
            
            response = gemini_model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                financial_data = json.loads(json_match.group())
                logger.info("Successfully extracted financial data using AI")
                return financial_data
            else:
                logger.warning("Could not extract JSON from AI response")
                return {"status": "extraction_failed"}
                
        except Exception as e:
            logger.error(f"AI financial data extraction failed: {str(e)}")
            return {"status": "ai_error", "error": str(e)}

    def _identify_document_type(self, text: str) -> str:
        """Identify the type of financial document."""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['quarterly report', 'q1', 'q2', 'q3', 'q4']):
            return "Quarterly Report"
        elif 'annual report' in text_lower or '10-k' in text_lower:
            return "Annual Report"
        elif '10-q' in text_lower:
            return "Quarterly Filing (10-Q)"
        elif 'earnings' in text_lower:
            return "Earnings Report"
        else:
            return "Financial Document"

class InvestmentAnalysisTool(BaseTool):
    name: str = "Investment Analyzer"
    description: str = "Provides investment analysis and recommendations based on financial data."

    def _run(self, financial_data: dict, company_name: str = "Unknown") -> str:
        try:
            if not gemini_model:
                return "Investment analysis unavailable - AI not configured"
            
            prompt = f"""
            As an investment advisor, analyze this financial data for {company_name} and provide investment recommendations.
            
            Financial Data: {json.dumps(financial_data, indent=2)}
            
            Provide:
            1. Investment recommendation (buy/sell/hold)
            2. Key strengths supporting the recommendation
            3. Main risks to consider
            4. Target price considerations if applicable
            5. Portfolio allocation suggestion
            
            Format as professional investment analysis.
            """
            
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error in investment analysis: {str(e)}")
            return f"Investment analysis error: {str(e)}"

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessor"
    description: str = "Performs comprehensive risk analysis for investment decisions."

    def _run(self, financial_data: dict, company_name: str = "Unknown") -> str:
        try:
            if not gemini_model:
                return "Risk analysis unavailable - AI not configured"
            
            prompt = f"""
            Conduct comprehensive risk analysis for {company_name} investment.
            
            Financial Data: {json.dumps(financial_data, indent=2)}
            
            Analyze:
            1. Financial risks (leverage, liquidity, profitability)
            2. Market risks (competition, economic factors)
            3. Operational risks (management, regulatory)
            4. Strategic risks (market positioning, execution)
            5. Overall risk rating and mitigation strategies
            
            Provide specific, actionable risk assessment.
            """
            
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            return f"Risk analysis error: {str(e)}"