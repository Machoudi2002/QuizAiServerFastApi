from fastapi import FastAPI;
from fastapi.middleware.cors import CORSMiddleware
from static import router as static_router;
from deepseekCall import router as upload_router;

app = FastAPI();

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(static_router);
app.include_router(upload_router);







