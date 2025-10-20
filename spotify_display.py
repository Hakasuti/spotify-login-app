import requests
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
from screeninfo import get_monitors

# Spotify credentials
client_id = "fb40226434c943999dff6693260742ce"
client_secret = "a2abde1b748b45a2baf2a7d315f1d9b3"
refresh_token = "AQB5xcl0o3Qq4YdfHwMuZ4R74IgR09UUoC6Q00TKWEaGeGpqNotbsCUjrYarhDj0wcsZmAdcUKz4LHAayjlfYg4Snuts5WOUYmo9nFkUFxwMj101LCxOn0IQSy4CZJD3k7Q"

def get_access_token():
    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    })
    return response.json().get("access_token")

def get_current_track(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
    if response.status_code == 200 and response.json().get("item"):
        return response.json()["item"]
    return None

from PIL import ImageEnhance

def update_display(track):
    album_url = track["album"]["images"][0]["url"]
    img_data = requests.get(album_url).content
    img = Image.open(BytesIO(img_data))

    # Resize to fit second monitor while preserving aspect ratio
    monitor = get_monitors()[1]
    screen_width = monitor.width
    screen_height = monitor.height
    img_ratio = img.width / img.height
    screen_ratio = screen_width / screen_height

    if img_ratio > screen_ratio:
        new_width = screen_width
        new_height = int(screen_width / img_ratio)
    else:
        new_height = screen_height
        new_width = int(screen_height * img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Simulate fade-in by gradually increasing brightness
    for i in range(1, 11):
        enhancer = ImageEnhance.Brightness(img)
        faded = enhancer.enhance(i / 10)
        photo = ImageTk.PhotoImage(faded)
        canvas.delete("all")
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2
        canvas.create_image(x, y, anchor="nw", image=photo)
        canvas.image = photo
        root.update()
        root.after(30)  # 30ms delay between frames


# GUI setup
monitor = get_monitors()[1]  # second monitor
root = tk.Tk()
root.configure(bg="black")
root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
root.overrideredirect(True)
root.focus_set()
root.bind("<Escape>", lambda e: root.destroy())

canvas = tk.Canvas(root, bg="black", highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)

# Main loop
access_token = get_access_token()
last_track_id = None

def poll():
    global last_track_id
    track = get_current_track(access_token)
    if track:
        current_id = track["id"]
        if current_id != last_track_id:
            update_display(track)
            last_track_id = current_id
    root.after(1000, poll)

poll()
root.mainloop()
