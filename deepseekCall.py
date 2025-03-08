from fastapi import File, UploadFile, HTTPException, APIRouter, Request
from pydantic import BaseModel
import PyPDF2
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import json
import re
from openai import OpenAI
import os
import logging

# Initialize FastAPI app
router = APIRouter()
templates = Jinja2Templates(directory="Templates")
apiKey = os.getenv("OPENAI_API_KEY")
print(apiKey)
# Initialize OpenAI client
client = OpenAI(
    api_key=apiKey,  # Store your API key in an environment variable
    base_url="https://openrouter.ai/api/v1",
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic model for the response
class QuizResponse(BaseModel):
    quiz: list[dict]

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            # Remove surrogate characters
            page_text = page_text.encode('utf-8', 'ignore').decode('utf-8')
            text += page_text
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

# System prompt for generating the quiz
system_prompt = """
The user will provide some text extracted from a PDF. Please generate a multiple-choice quiz based on the content of the text.
Each question should have one correct answer and three incorrect answers. Output the quiz in JSON format.

EXAMPLE OUTPUT:
{
    "quizName": "english quiz",
    "quiz": [
        {
            "question": "Which is the highest mountain in the world?",
            "options": ["Mount Everest", "K2", "Kangchenjunga", "Lhotse"],
            "correct_answer": "Mount Everest"
        },
        {
            "question": "Which is the longest river in the world?",
            "options": ["Nile River", "Amazon River", "Yangtze River", "Mississippi River"],
            "correct_answer": "Nile River"
        }
    ]
}

IMPORTANT: The response must be in JSON format.
"""

# FastAPI endpoint to upload PDF and generate quiz
@router.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: Request, file: UploadFile = File(...)):
    try:
        # Step 1: Extract text from the uploaded PDF
        logger.info("Extracting text from PDF")
        pdf_text = extract_text_from_pdf(file.file)
        logger.info("Extracted text from PDF")

        # Step 2: Prepare the prompt for Deepseek API
        user_prompt = f"Generate in french a multiple-choice quiz with a minimum of 15 questions based on the following text:\n\n{pdf_text}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Step 3: Call the Deepseek API
        logger.info("Calling Deepseek API")
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=messages,
            response_format={
                'type': 'json_object'
            }
        )
        logger.info("Received response from Deepseek API")

        response = response.choices[0].message.content
        json_match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
        if json_match:
            # Extract the JSON string
            json_str = json_match.group(1)
    
            # Parse the JSON string into a Python dictionary
            try:
                json_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                raise HTTPException(status_code=500, detail="Failed to parse JSON")
        else:
            logger.error("No JSON match found in the response")
            raise HTTPException(status_code=500, detail="No JSON match found in the response")
        
        logger.info("Generated quiz successfully")
        
        # Render the quiz using Jinja2 template
        return JSONResponse(json_data)
    except Exception as e:
        logger.error(f"Failed to generate quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")
