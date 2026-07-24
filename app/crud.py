import hashlib
import hmac
import secrets

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import SessionLocal
from app.models import User

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000
    ).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def verify_password(password: str, stored_password: str) -> bool:
    if stored_password.startswith("pbkdf2_sha256$"):
        _, salt, stored_digest = stored_password.split("$")
        computed_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120000
        ).hex()
        return hmac.compare_digest(computed_digest, stored_digest)

    return hmac.compare_digest(password, stored_password)


@router.get("/")
def root():
    return RedirectResponse(url="/login", status_code=303)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "message": "Invalid Credentials"
            }
        )

    if not verify_password(password, user.password):
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "message": "Invalid Credentials"
            }
        )

    request.session["user"] = user.email

    return RedirectResponse(url="/home", status_code=303)


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@router.post("/register")
def register_user(
    request: Request,
    name: str = Form(...),
    rollno: int = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...)
):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "Email already exists"
            }
        )

    existing_rollno = db.query(User).filter(
        User.rollno == rollno
    ).first()

    if existing_rollno:
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "message": "Roll number already exists"
            }
        )

    user = User(
        name=name,
        rollno=rollno,
        email=email,
        phone=phone,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.close()

    return RedirectResponse(url="/login", status_code=303)


@router.get("/home")
def home(request: Request):

    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()

    users = db.query(User).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "users": users,
            "email": request.session["user"]
        }
    )


@router.get("/edit/{rollno}")
def edit_page(request: Request, rollno: int):

    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()

    user = db.query(User).filter(
        User.rollno == rollno
    ).first()

    db.close()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    if user.email != request.session["user"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to edit this user"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={
            "user": user
        }
    )


@router.post("/update/{rollno}")
def update_user(
    request: Request,
    rollno: int,
    name: str = Form(...),
    new_rollno: int = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...)
):

    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()

    user = db.query(User).filter(
        User.rollno == rollno
    ).first()

    if user is None:
        db.close()

        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    if user.email != request.session["user"]:
        db.close()

        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this user"
        )

    duplicate_email = db.query(User).filter(
        User.email == email,
        User.rollno != rollno
    ).first()

    if duplicate_email:
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "user": user,
                "message": "Email already exists"
            }
        )

    duplicate_rollno = db.query(User).filter(
        User.rollno == new_rollno,
        User.rollno != rollno
    ).first()

    if duplicate_rollno:
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "user": user,
                "message": "Roll number already exists"
            }
        )

    user.name = name
    user.rollno = new_rollno
    user.email = email
    user.phone = phone
    user.password = hash_password(password)

    db.commit()
    db.refresh(user)
    db.close()

    return RedirectResponse(url="/home", status_code=303)


@router.post("/delete/{rollno}")
def delete_user(request: Request, rollno: int):

    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()

    user = db.query(User).filter(
        User.rollno == rollno
    ).first()

    if user is None:
        db.close()

        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    if user.email != request.session["user"]:
        db.close()

        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this user"
        )

    db.delete(user)
    db.commit()
    db.close()

    return RedirectResponse(url="/home", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)