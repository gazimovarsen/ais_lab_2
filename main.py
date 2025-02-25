# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import schemas
from typing import List, Optional
from datetime import timedelta

# Import API route modules
from routers import auth_routes, teacher_routes, student_routes

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="English Gang API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers with prefixes
app.include_router(auth_routes.router, prefix="/api")
app.include_router(teacher_routes.router, prefix="/api")
app.include_router(student_routes.router, prefix="/api")


# Serve HTML pages
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("templates/index.html") as f:
        return HTMLResponse(content=f.read())


@app.get("/login.html", response_class=HTMLResponse)
async def serve_login():
    with open("templates/login.html") as f:
        return HTMLResponse(content=f.read())


@app.get("/registration.html", response_class=HTMLResponse)
async def serve_registration():
    with open("templates/registration.html") as f:
        return HTMLResponse(content=f.read())


# Health check endpoint for Nginx
@app.get("/health")
async def health_check():
    return {"status": "ok"}
