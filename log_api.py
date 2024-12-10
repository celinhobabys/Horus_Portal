from fastapi import FastAPI, Query, UploadFile, Form, HTTPException, APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

# Initialize the FastAPI app
app = FastAPI()

# Database setup
DB_FILE = "logs.db"

# Ensure the database and table exist
def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS log (
        date TEXT PRIMARY KEY,
        file_content TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

initialize_database()

log_router = APIRouter(
    prefix="/log",
    tags=["log"]
)

class log(BaseModel):
    date: str
    file: str

@log_router.post("/register/")
async def register_log(log: log):
    """
    Registers a log entry with a date and file.
    """
    # Validate date format
    date = log.date
    file = log.file
    try:
        formatted_date = datetime.strptime(date, "%y/%m/%d").strftime("%Y-%m-%d")
        print("formatted_date", formatted_date)
    except ValueError:
        print("DATE ERROR")
        raise HTTPException(status_code=400, detail="Invalid date format. Use yy/mm/dd.")

    # Read the file content

    try:
        # Insert the data into the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO log (date, file_content)
        VALUES (?, ?)
        """, (formatted_date, file))
        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "Log entry registered successfully."}, status_code=201)
    except Exception as e:
        print("error", e)
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@log_router.get("/list/")
async def list_logs():
    """
    Retrieves a list of all logs.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT date, file_content FROM log
        """)
        logs = cursor.fetchall()
        conn.close()

        # Format the logs into a structured response
        log_list = [
            {"date": datetime.strptime(log[0], "%Y-%m-%d").strftime("%d/%m/%Y"), "content": log[1]} for log in logs
        ]

        return JSONResponse(content={"logs": log_list}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@log_router.delete("/delete/")
async def delete_all_logs():
    """
    Deletes all logs from the database.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Count logs before deletion
        cursor.execute("SELECT COUNT(*) FROM log")
        log_count = cursor.fetchone()[0]

        # If no logs are found, return a 404 response
        if log_count == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="No logs to delete.")

        # Delete all logs
        cursor.execute("DELETE FROM log")
        conn.commit()
        conn.close()

        return {"message": f"Successfully deleted {log_count} log(s)."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(log_router)

# Run this to test in development using `uvicorn` (e.g., uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
