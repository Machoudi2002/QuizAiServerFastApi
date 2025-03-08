from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

class FileUploadResponse(BaseModel):
    filename: str
    message: str

UploadDir = "uploads"
os.makedirs(UploadDir, exist_ok=True)



client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)




@router.post("/upload", response_model=FileUploadResponse)
async def uploadPDF(file: UploadFile = File()):
    try:
        filePath = os.path.join(UploadDir, file.filename)
        with open(filePath, "wb") as f:
            f.write(await file.read())
        return FileUploadResponse(filename=file.filename, message="Upload successful")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



'''
messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    response_format={
        'type': 'json_object'
    }
)
'''
