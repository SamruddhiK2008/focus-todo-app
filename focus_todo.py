import customtkinter as ctk
import time
import threading
import random
from datetime import datetime, date
import json
import os
from plyer import notification  # Import plyer notification

# ----------------------------- CONFIG ----------------------------- #
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Focus To-Do")
root.geometry("600x900")

# Default durations (can be customized)
study_duration = 25 * 60
short_break = 5 * 60
long_break = 15 * 60

sessions_completed = 0
streaks = 0
is_running = False
remaining_time = 0
focus_mode = False
theme_mode = ctk.StringVar(value="light")
tasks = []

# For persistent tasks
TASKS_FILE = "tasks.json"
REPORT_FILE = f"report_{date.today()}.txt"

# ----------------------------- FUNCTIONS ----------------------------- #

def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f)

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            loaded = json.load(f)
            for task in loaded:
                task_listbox.insert("end", task)
                tasks.append(task)

def generate_daily_report():
    with open(REPORT_FILE, "w") as f:
        f.write(f"Date: {date.today()}\n")
        f.write(f"Sessions Completed: {sessions_completed}\n")
        f.write("Tasks:\n")
        for t in tasks:
            f.write(f"- {t}\n")

def update_timer():
    global remaining_time, is_running, sessions_completed, streaks
    while remaining_time > 0 and is_running:
        mins, secs = divmod(remaining_time, 60)
        timer_label.configure(text=f"{int(mins):02d}:{int(secs):02d}")
        progress.set((study_duration - remaining_time) / study_duration)
        root.update()
        time.sleep(1)
        remaining_time -= 1

    if remaining_time == 0 and is_running:
        sessions_completed += 1
        streaks += 1
        update_streaks()
        motivation_label.configure(text="Break Time!")
        generate_daily_report()
        
        # Desktop notification when session ends
        notification.notify(
            title="Focus To-Do",
            message="Session complete! Take a break.",
            timeout=10  # Notification will be visible for 10 seconds
        )
        
        is_running = False

def start_session():
    global is_running, remaining_time, study_duration
    if not is_running:
        try:
            mins = int(study_entry.get())
            study_duration = mins * 60
        except ValueError:
            study_duration = 25 * 60
        remaining_time = study_duration
        is_running = True
        motivation_label.configure(text=random.choice(motivation_quotes))
        threading.Thread(target=update_timer, daemon=True).start()

def stop_session():
    global is_running
    is_running = False
    motivation_label.configure(text="Session stopped. Take a deep breath!")

def update_streaks():
    streak_label.configure(text=f"Streak: {streaks} Sessions")

def toggle_theme():
    current = theme_mode.get()
    if current == "light":
        ctk.set_appearance_mode("dark")
        theme_mode.set("dark")
        timer_label.configure(text_color="white")
        theme_button.configure(text="Light Mode")
    elif current == "dark":
        theme_mode.set("light")
        ctk.set_appearance_mode("light")
        timer_label.configure(text_color="black")
        theme_button.configure(text="Dark Mode")

def add_task():
    task = task_entry.get()
    if task:
        formatted = f"[ ] {task}"
        task_listbox.insert("end", formatted)
        tasks.append(formatted)
        save_tasks()
        task_entry.delete(0, 'end')

def clear_tasks():
    tasks.clear()
    task_listbox.delete(0.0, 'end')
    save_tasks()

def mark_task_done():
    content = task_listbox.get("0.0", "end").splitlines()
    task_listbox.delete("0.0", "end")
    tasks.clear()
    for line in content:
        if line.startswith("[ ]"):
            updated = line.replace("[ ]", "[x]")
        else:
            updated = line
        task_listbox.insert("end", updated)
        tasks.append(updated)
    save_tasks()

def toggle_focus_mode():
    global focus_mode
    focus_mode = not focus_mode
    if focus_mode:
        motivation_label.configure(text="Focus Mode: Activated!")
        root.configure(fg_color="#f0f0f0")
    else:
        motivation_label.configure(text="Focus Mode: Deactivated.")
        root.configure(fg_color="#ffffff")

# ----------------------------- UI ----------------------------- #
timer_label = ctk.CTkLabel(root, text="25:00", font=("Helvetica", 40), text_color="black")
timer_label.pack(pady=10)

progress = ctk.CTkProgressBar(root, width=400)
progress.set(0)
progress.pack(pady=10)

motivation_label = ctk.CTkLabel(root, text="", font=("Arial", 14), wraplength=500)
motivation_label.pack(pady=10)

# Custom time entries
time_frame = ctk.CTkFrame(root)
time_frame.pack(pady=5)

study_label = ctk.CTkLabel(time_frame, text="Study (min):", font=("Arial", 12))
study_label.grid(row=0, column=0, padx=5)
study_entry = ctk.CTkEntry(time_frame, width=60)
study_entry.insert(0, "25")
study_entry.grid(row=0, column=1, padx=5)

# Buttons
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10)

start_button = ctk.CTkButton(button_frame, text="Start Session", command=start_session)
start_button.grid(row=0, column=0, padx=5)

stop_button = ctk.CTkButton(button_frame, text="Stop", command=stop_session)
stop_button.grid(row=0, column=1, padx=5)

theme_button = ctk.CTkButton(button_frame, text="Dark Mode", command=toggle_theme)
theme_button.grid(row=0, column=2, padx=5)

focus_mode_button = ctk.CTkButton(button_frame, text="Focus Mode", command=toggle_focus_mode)
focus_mode_button.grid(row=0, column=3, padx=5)

# To-Do List Section
todo_label = ctk.CTkLabel(root, text="To-Do List", font=("Arial", 16))
todo_label.pack(pady=5)

task_entry = ctk.CTkEntry(root, width=300, font=("Arial", 14))
task_entry.pack(pady=5)

task_button_frame = ctk.CTkFrame(root)
task_button_frame.pack()

add_task_button = ctk.CTkButton(task_button_frame, text="Add Task", command=add_task)
add_task_button.grid(row=0, column=0, padx=5)

done_task_button = ctk.CTkButton(task_button_frame, text="Mark Done", command=mark_task_done)
done_task_button.grid(row=0, column=1, padx=5)

clear_task_button = ctk.CTkButton(task_button_frame, text="Clear All", command=clear_tasks)
clear_task_button.grid(row=0, column=2, padx=5)

task_listbox = ctk.CTkTextbox(root, width=500, height=200, font=("Arial", 14))
task_listbox.pack(pady=10)

streak_label = ctk.CTkLabel(root, text="Streak: 0 Sessions", font=("Arial", 14))
streak_label.pack(pady=5)

motivation_quotes = [
    "Keep going! You're doing great!",
    "Stay focused, you're almost there!",
    "Don't stop! Your effort will pay off!",
    "Every minute counts! Keep pushing!",
    "Believe in yourself and keep going!",
]

load_tasks()
root.mainloop()