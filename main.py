from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import string, random, sqlite3, os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_NAME = "urls.db"

# Ensure database exists
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_id TEXT UNIQUE,
                long_url TEXT
            )
        """)
init_db()

def generate_short_id(num_chars=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=num_chars))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten")
async def shorten_url(long_url: str = Form(...)):
    short_id = generate_short_id()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO urls (short_id, long_url) VALUES (?, ?)", (short_id, long_url))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Short ID already exists.")
    return {"short_url": f"https://url-shortner-tt8q.onrender.com/{short_id}"}

@app.get("/{short_id}")
async def redirect_to_url(short_id: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT long_url FROM urls WHERE short_id = ?", (short_id,))
        row = cursor.fetchone()
        if row:
            return RedirectResponse(row[0])
        else:
            raise HTTPException(status_code=404, detail="URL not found.")
