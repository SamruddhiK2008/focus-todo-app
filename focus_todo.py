import customtkinter as ctk import time import threading import random from datetime import datetime, date import json import os from plyer import notification

----------------------------- CONFIG -----------------------------

ctk.set_appearance_mode("light") ctk.set_default_color_theme("blue")

root = ctk.CTk() root.title("Focus To-Do") root.geometry("650x1000")

study_duration = 25 * 60 sessions_completed = 0 streaks = 0 is_running = False remaining_time = 0 focus_mode = False

theme_mode = ctk.StringVar(value="light") tasks = [None] * 5  # Fixed slots

TASKS_FILE = "tasks.json" REPORT_FILE = f"report_{date.today()}.txt"

----------------------------- FUNCTIONS -----------------------------

def save_tasks(): with open(TASKS_FILE, "w") as f: json.dump(tasks, f)

def load_tasks(): if os.path.exists(TASKS_FILE): with open(TASKS_FILE, "r") as f: loaded = json.load(f) for i in range(5): if i < len(loaded) and loaded[i]: tasks[i] = loaded[i] display_tasks()

def generate_daily_report(): with open(REPORT_FILE, "w") as f: f.write(f"Date: {date.today()}\n") f.write(f"Sessions Completed: {sessions_completed}\n") f.write("Tasks:\n") for t in tasks: if t: f.write(f"- {t['text']} | Status: {t['status']}\n")

def update_timer(): global remaining_time, is_running, sessions_completed, streaks while remaining_time > 0 and is_running: mins, secs = divmod(remaining_time, 60) timer_label.configure(text=f"{int(mins):02d}:{int(secs):02d}") progress.set((study_duration - remaining_time) / study_duration) root.update() time.sleep(1) remaining_time -= 1

if remaining_time == 0 and is_running:
    sessions_completed += 1
    streaks += 1
    update_streaks()
    motivation_label.configure(text="Break Time!")
    generate_daily_report()
    notification.notify(
        title="Focus To-Do",
        message="Session complete! Take a break.",
        timeout=10
    )
    is_running = False

def start_session(): global is_running, remaining_time, study_duration if not is_running: try: mins = int(study_entry.get()) study_duration = mins * 60 except ValueError: study_duration = 25 * 60 remaining_time = study_duration is_running = True motivation_label.configure(text=random.choice(motivation_quotes)) threading.Thread(target=update_timer, daemon=True).start()

def stop_session(): global is_running is_running = False motivation_label.configure(text="Session stopped. Take a deep breath!")

def update_streaks(): streak_label.configure(text=f"Streak: {streaks} Sessions")

def toggle_theme(): current = theme_mode.get() if current == "light": ctk.set_appearance_mode("dark") theme_mode.set("dark") timer_label.configure(text_color="white") theme_button.configure(text="Light Mode") else: theme_mode.set("light") ctk.set_appearance_mode("light") timer_label.configure(text_color="black") theme_button.configure(text="Dark Mode")

def add_task(): try: slot = int(task_number_entry.get()) - 1 text = task_entry.get() due = task_due_entry.get() if 0 <= slot < 5 and text and due: tasks[slot] = {"text": text, "status": "Pending", "due": due, "completed": ""} save_tasks() display_tasks() task_entry.delete(0, 'end') task_due_entry.delete(0, 'end') except ValueError: pass

def mark_task_done(): try: slot = int(task_number_entry.get()) - 1 if 0 <= slot < 5 and tasks[slot]: tasks[slot]['status'] = "Completed" tasks[slot]['completed'] = str(date.today()) save_tasks() display_tasks() except ValueError: pass

def edit_task(): try: slot = int(edit_num_entry.get()) - 1 new_text = edit_text_entry.get() new_due = edit_date_entry.get() if 0 <= slot < 5 and tasks[slot]: if new_text: tasks[slot]['text'] = new_text if new_due: tasks[slot]['due'] = new_due save_tasks() display_tasks() except ValueError: pass

def remove_task(): try: slot = int(edit_num_entry.get()) - 1 if 0 <= slot < 5: tasks[slot] = None save_tasks() display_tasks() except ValueError: pass

def display_tasks(): task_listbox.delete("0.0", "end") task_listbox.insert("end", "Completed Tasks:\n") for i, t in enumerate(tasks): if t and t['status'] == "Completed": task_listbox.insert("end", f"{i+1}. [x] {t['text']} (Done: {t['completed']})\n") task_listbox.insert("end", "\nPending Tasks:\n") for i, t in enumerate(tasks): if t and t['status'] == "Pending": task_listbox.insert("end", f"{i+1}. [ ] {t['text']} (Due: {t['due']})\n")

def toggle_focus_mode(): global focus_mode focus_mode = not focus_mode if focus_mode: motivation_label.configure(text="Focus Mode: Activated!") root.configure(fg_color="#f0f0f0") else: motivation_label.configure(text="Focus Mode: Deactivated.") root.configure(fg_color="#ffffff")

----------------------------- UI -----------------------------

timer_label = ctk.CTkLabel(root, text="25:00", font=("Helvetica", 40), text_color="black") timer_label.pack(pady=10)

progress = ctk.CTkProgressBar(root, width=400) progress.set(0) progress.pack(pady=10)

motivation_label = ctk.CTkLabel(root, text="", font=("Arial", 14), wraplength=500) motivation_label.pack(pady=10)

Custom time entries

time_frame = ctk.CTkFrame(root) time_frame.pack(pady=5)

study_label = ctk.CTkLabel(time_frame, text="Study (min):") study_label.grid(row=0, column=0, padx=5) study_entry = ctk.CTkEntry(time_frame, width=60) study_entry.insert(0, "25") study_entry.grid(row=0, column=1, padx=5)

Control Buttons

button_frame = ctk.CTkFrame(root) button_frame.pack(pady=10)

start_button = ctk.CTkButton(button_frame, text="Start Session", command=start_session
