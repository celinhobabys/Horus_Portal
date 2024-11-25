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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_content BLOB NOT NULL
    )
    """)
    conn.commit()
    conn.close()

initialize_database()

log_router = APIRouter(
    prefix="/log",
    tags="log"
)

@app.post("/register_log/")
async def register_log(date: str = Form(...), file: UploadFile = None):
    """
    Registers a log entry with a date and file.
    """
    # Validate date format
    try:
        formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd/mm/yyyy.")

    # Ensure file is provided
    if not file:
        raise HTTPException(status_code=400, detail="File is required.")

    # Read the file content
    file_content = await file.read()

    try:
        # Insert the data into the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO log (date, file_name, file_content)
        VALUES (?, ?, ?)
        """, (formatted_date, file.filename, file_content))
        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "Log entry registered successfully."}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_logs/")
async def list_logs():
    """
    Retrieves a list of all logs.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, date, file_name, file_content FROM log
        """)
        logs = cursor.fetchall()
        conn.close()

        # Format the logs into a structured response
        log_list = [
            {"id": log[0], "date": datetime.strptime(log[1], "%Y-%m-%d").strftime("%d/%m/%Y"), "file_name": log[2], "content": log[3].decode("utf-8")} for log in logs
        ]

        return JSONResponse(content={"logs": log_list}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_logs_by_date/")
async def list_logs_by_date(
    date_min: str = Query(..., description="The minimum date in dd/mm/yyyy format"),
    date_max: str = Query(..., description="The maximum date in dd/mm/yyyy format"),
):
    """
    Lists all logs that are newer than date_min and older than date_max.
    """
    try:
        # Convert date_min and date_max to the correct format
        try:
            date_min_formatted = datetime.strptime(date_min, "%d/%m/%Y").strftime("%Y-%m-%d")
            date_max_formatted = datetime.strptime(date_max, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use dd/mm/yyyy.")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Query logs within the specified date range
        cursor.execute("""
        SELECT id, date, file_name, file_content FROM log
        WHERE date > ? AND date < ?
        """, (date_min_formatted, date_max_formatted))
        logs = cursor.fetchall()
        conn.close()

        # Format the logs into a structured response
        log_list = [
            {"id": log[0], "date": datetime.strptime(log[1], "%Y-%m-%d").strftime("%d/%m/%Y"), "file_name": log[2], "content": log[3].decode("utf-8")} for log in logs
        ]

        return {"logs": log_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_file_by_name/")
async def get_file_by_name(file_name: str):
    """
    Retrieves the content of a file by its name from the database and returns it as a downloadable file.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Query for the file content by name
        cursor.execute("""
        SELECT file_content FROM log WHERE file_name = ?
        """, (file_name,))
        result = cursor.fetchone()
        conn.close()

        # If the file is not found, return 404
        if not result:
            raise HTTPException(status_code=404, detail="File not found.")

        # Write the file content to a temporary file
        temp_file_path = f"temp_{file_name}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(result[0])

        # Return the file as a response
        return FileResponse(temp_file_path, filename=file_name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # finally:
    #     # Clean up the temporary file after response (best effort)
    #     if os.path.exists(temp_file_path):
    #         os.remove(temp_file_path)

@app.delete("/delete_all_logs/")
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

# Run this to test in development using `uvicorn` (e.g., uvicorn main:app --reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
