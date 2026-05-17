from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
# Use relative import for routes within this package
from .api.v1.routes import chat, auth, attendance, leave, payroll, projects

app = FastAPI(title="AutoTricks Employee Portal API", version="1.0.0")

# Configure CORS for Angular Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chatbot"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(leave.router, prefix="/leave", tags=["Leave"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["Payroll"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to AutoTricks Employee Portal API"}
