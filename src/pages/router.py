from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(
    tags=["Pages"],
)

templates = Jinja2Templates(directory="nginx/templates")


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})