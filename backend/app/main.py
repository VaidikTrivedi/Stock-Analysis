import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import uuid
from analysis import analyze_ticker

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TickerRequest(BaseModel):
    ticker: str

@app.post("/analyze")
def analyze(request: TickerRequest):
    try:
        result = analyze_ticker(request.ticker)
        return jsonable_encoder(result)
    except Exception as e:
        print(f"EXCEPTION - {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/{graph_id}")
def get_graph(graph_id: str):
    file_path = f"/tmp/{graph_id}.png"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Graph not found")
