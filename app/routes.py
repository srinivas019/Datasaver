from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/register")
def register_page(request: Request):

    # Check if user is logged in
    if "user" not in request.session:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Open register page
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )