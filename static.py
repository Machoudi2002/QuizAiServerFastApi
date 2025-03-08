from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home():
    with open("Templates/main.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)
