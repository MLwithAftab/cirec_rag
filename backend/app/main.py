from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

from .config import get_settings
from .models import Token
from .api import query, admin, auth
from .core.rag_engine import rag_engine

# Initialize FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Document Query System with Multi-Format Support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates = Jinja2Templates(directory="../frontend/templates")

# Settings
settings = get_settings()

# Initialize RAG engine on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting RAG System...")
    rag_engine.load_or_create_index()
    print("✅ RAG System ready!")

# Include routers
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# Authentication endpoint
@app.post("/api/login", response_model=Token)
async def login(username: str, password: str):
    """Login to get access token"""
    if not auth.authenticate_user(username, password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Frontend routes
@app.get("/")
async def home(request: Request):
    """User interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
async def admin_page(request: Request):
    """Admin interface"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = rag_engine.get_index_stats()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "documents": stats.get('total_documents', 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)