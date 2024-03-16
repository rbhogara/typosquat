from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
async def handle_form(request: Request, input_field: str = Form(...)):
    return templates.TemplateResponse("response.html", {"request": request, "input_data": input_field})
