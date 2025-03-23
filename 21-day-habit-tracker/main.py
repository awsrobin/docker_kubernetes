from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from datetime import datetime
import json
import os

# Initialize FastAPI app
app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# File to store user data
USER_DATA_FILE = "users.json"



@app.get("/debug-css")
async def debug_css():
    return FileResponse("static/style.css")

# Load user data from file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If the file is empty or contains invalid JSON, return an empty dictionary
            return {}
    return {}

# Save user data to file
def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Homepage
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Register page (GET request)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Register user (POST request)
@app.post("/register", response_class=RedirectResponse)
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    target: str = Form(...)
):
    users = load_users()
    if email in users:
        raise HTTPException(status_code=400, detail="User already exists!")

    users[email] = {
        "name": name,
        "password": password,
        "target": target,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "progress": []
    }
    save_users(users)
    return RedirectResponse(url="/login", status_code=303)

# Login page (GET request)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login user (POST request)
@app.post("/login", response_class=RedirectResponse)
@app.post("/login", response_class=RedirectResponse)
async def login_user(
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        # Load users from the file
        users = load_users()
        print(f"Loaded users: {users}")  # Debug: Print loaded users

        # Check if the email exists in the users dictionary
        if email not in users:
            print(f"Email '{email}' not found in users.")  # Debug
            raise HTTPException(status_code=400, detail="Invalid email or password!")

        # Check if the password matches
        if users[email]["password"] != password:
            print(f"Incorrect password for email '{email}'.")  # Debug
            raise HTTPException(status_code=400, detail="Invalid email or password!")

        # Redirect to the dashboard if login is successful
        return RedirectResponse(url=f"/dashboard/{email}", status_code=303)

    except Exception as e:
        print(f"Error during login: {e}")  # Debug: Print any unexpected errors
        raise HTTPException(status_code=500, detail="Internal Server Error")
# Dashboard page
@app.post("/check-target/{email}", response_class=RedirectResponse)
async def check_target(email: str, target_status: str = Form(...)):
    try:
        # Load users from the file
        users = load_users()
        print(f"Loaded users: {users}")  # Debug: Print loaded users

        # Check if the user exists
        user = users.get(email)
        if not user:
            print(f"User with email '{email}' not found.")  # Debug
            raise HTTPException(status_code=404, detail="User not found!")

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Update progress based on the selected radio button
        if target_status == "yes":

            if today not in user["progress"]:
                user["progress"].append(today)
        else:
            if today in user["progress"]:
                user["progress"].remove(today)

        # Save updated user data
        save_users(users)

        # Redirect back to the dashboard with the target status
        return RedirectResponse(url=f"/dashboard/{email}?target_status={target_status}", status_code=303)

    except Exception as e:
        print(f"Error in check-target route: {e}")  # Debug: Print any unexpected errors
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/dashboard/{email}", response_class=HTMLResponse)
async def dashboard(request: Request, email: str, target_status: str = None):
    try:
        # Load users from the file
        users = load_users()
        print(f"Loaded users: {users}")  # Debug: Print loaded users

        # Check if the user exists
        user = users.get(email)
        if not user:
            print(f"User with email '{email}' not found.")  # Debug
            raise HTTPException(status_code=404, detail="User not found!")

        # Calculate days passed and days left
        start_date = datetime.strptime(user["start_date"], "%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")  # Get today's date as a string
        days_passed = (datetime.now() - start_date).days
        days_left = max(0, 21 - days_passed)

        # Render the dashboard template
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "days_passed": days_passed,
                "days_left": days_left,
                "today": today,  # Pass today's date to the template
                "email": email,  # Pass email for the track progress form
                "target_status": target_status  # Pass target status to the template
            }
        )

    except Exception as e:
        print(f"Error in dashboard route: {e}")  # Debug: Print any unexpected errors
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Track progress
@app.post("/track/{email}")
async def track_progress(email: str):
    users = load_users()
    user = users.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")

    today = datetime.now().strftime("%Y-%m-%d")
    if today in user["progress"]:
        return {"message": "You've already logged your progress for today!"}

    user["progress"].append(today)
    save_users(users)
    return {"message": "Great job! Progress logged for today."}

# Group users by target
@app.get("/groups", response_class=HTMLResponse)
async def group_users(request: Request):
    users = load_users()
    groups = {}

    for email, user in users.items():
        target = user["target"]
        if target not in groups:
            groups[target] = []
        groups[target].append(user["name"])

    return templates.TemplateResponse("groups.html", {"request": request, "groups": groups})

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)