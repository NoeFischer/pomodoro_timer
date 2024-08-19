import json
import os
import subprocess
import sys
from datetime import datetime

import rumps


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Settings:
    def __init__(self, settings_file="pomodoro_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "work_duration": 25,
            "break_duration": 5,
            "long_break_duration": 15,
            "pomodoros_until_long_break": 4,
        }
        self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            self.save_settings()  # Create default settings file
        with open(self.settings_file, "r") as f:
            settings = json.load(f)
        self.work_duration = settings.get(
            "work_duration", self.default_settings["work_duration"]
        )
        self.break_duration = settings.get(
            "break_duration", self.default_settings["break_duration"]
        )
        self.long_break_duration = settings.get(
            "long_break_duration", self.default_settings["long_break_duration"]
        )
        self.pomodoros_until_long_break = settings.get(
            "pomodoros_until_long_break",
            self.default_settings["pomodoros_until_long_break"],
        )

    def save_settings(self):
        settings = {
            "work_duration": self.work_duration,
            "break_duration": self.break_duration,
            "long_break_duration": self.long_break_duration,
            "pomodoros_until_long_break": self.pomodoros_until_long_break,
        }
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)


class PomodoroApp(rumps.App):
    def __init__(self):
        super(PomodoroApp, self).__init__("⏲︎")
        settings_file = resource_path("pomodoro_settings.json")
        self.settings = Settings(settings_file)
        self.timer = rumps.Timer(self.update_timer, 1)
        self.reset_timer()
        self.pomodoros_completed = 0

        self.menu = [
            "Start Pomodoro",
            "Start Short Break",
            "Start Long Break",
            None,
            "Reset Timer",
            rumps.MenuItem("Settings", callback=None),
        ]

        self.menu["Settings"].add(
            rumps.MenuItem(
                f"Work Duration: {self.settings.work_duration} min",
                callback=self.set_work_duration,
            )
        )
        self.menu["Settings"].add(
            rumps.MenuItem(
                f"Break Duration: {self.settings.break_duration} min",
                callback=self.set_break_duration,
            )
        )
        self.menu["Settings"].add(
            rumps.MenuItem(
                f"Long Break Duration: {self.settings.long_break_duration} min",
                callback=self.set_long_break_duration,
            )
        )
        self.menu["Settings"].add(
            rumps.MenuItem(
                f"Pomodoros until Long Break: {self.settings.pomodoros_until_long_break}",
                callback=self.set_pomodoros_until_long_break,
            )
        )

    def reset_timer(self):
        self.time_left = self.settings.work_duration * 60
        self.is_running = False
        self.is_break = False
        self.title = "🍅"

    @rumps.clicked("Start Pomodoro")
    def start_pomodoro(self, _):
        self.reset_timer()
        self.start_timer()

    @rumps.clicked("Start Short Break")
    def start_break(self, _):
        self.time_left = self.settings.break_duration * 60
        self.is_break = True
        self.start_timer()

    @rumps.clicked("Start Long Break")
    def start_long_break(self, _):
        self.time_left = self.settings.long_break_duration * 60
        self.is_break = True
        self.start_timer()

    def start_timer(self):
        if not self.is_running:
            self.timer.start()
            self.is_running = True
            self.menu["Start Pomodoro"].title = "Pause"
        else:
            self.timer.stop()
            self.is_running = False
            self.menu["Start Pomodoro"].title = "Resume"

    @rumps.clicked("Reset Timer")
    def reset_timer_clicked(self, _):
        self.reset_timer()
        self.timer.stop()
        self.menu["Start Pomodoro"].title = "Start Pomodoro"

    def play_sound(self):
        sound_file = "/System/Library/Sounds/Glass.aiff"
        subprocess.run(["afplay", sound_file])

    def update_timer(self, _):
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.title = f"{mins:02d}:{secs:02d}"
        if self.time_left <= 0:
            self.timer.stop()
            self.play_sound()
            if not self.is_break:
                self.pomodoros_completed += 1
                if (
                    self.pomodoros_completed % self.settings.pomodoros_until_long_break
                    == 0
                ):
                    rumps.notification(
                        "Pomodoro",
                        "Time for a long break!",
                        "Great job completing a set!",
                    )
                else:
                    rumps.notification("Pomodoro", "Time for a break!", "Good work!")
                if self.current_task:
                    self.tasks.append(
                        {
                            "task": self.current_task,
                            "completed": datetime.now().isoformat(),
                        }
                    )
                    self.save_tasks()
            else:
                rumps.notification("Break", "Break's over!", "Time to focus!")
            self.reset_timer()

    def set_work_duration(self, sender):
        response = rumps.Window(
            title="Set Work Duration",
            message=f"Enter work duration in minutes (current: {self.settings.work_duration}):",
            default_text=str(self.settings.work_duration),
            dimensions=(200, 20),
        ).run()
        if response.clicked:
            try:
                new_duration = (
                    int(response.text) if response.text else self.settings.work_duration
                )
                if new_duration > 0:
                    self.settings.work_duration = new_duration
                    sender.title = f"Work Duration: {self.settings.work_duration} min"
                    self.settings.save_settings()
                else:
                    raise ValueError
            except ValueError:
                rumps.alert("Invalid input. Please enter a positive number.")

    def set_break_duration(self, sender):
        response = rumps.Window(
            title="Set Break Duration",
            message=f"Enter break duration in minutes (current: {self.settings.break_duration}):",
            default_text=str(self.settings.break_duration),
            dimensions=(200, 20),
        ).run()
        if response.clicked:
            try:
                new_duration = (
                    int(response.text)
                    if response.text
                    else self.settings.break_duration
                )
                if new_duration > 0:
                    self.settings.break_duration = new_duration
                    sender.title = f"Break Duration: {self.settings.break_duration} min"
                    self.settings.save_settings()
                else:
                    raise ValueError
            except ValueError:
                rumps.alert("Invalid input. Please enter a positive number.")

    def set_long_break_duration(self, sender):
        response = rumps.Window(
            title="Set Long Break Duration",
            message=f"Enter long break duration in minutes (current: {self.settings.long_break_duration}):",
            default_text=str(self.settings.long_break_duration),
            dimensions=(200, 20),
        ).run()
        if response.clicked:
            try:
                new_duration = (
                    int(response.text)
                    if response.text
                    else self.settings.long_break_duration
                )
                if new_duration > 0:
                    self.settings.long_break_duration = new_duration
                    sender.title = (
                        f"Long Break Duration: {self.settings.long_break_duration} min"
                    )
                    self.settings.save_settings()
                else:
                    raise ValueError
            except ValueError:
                rumps.alert("Invalid input. Please enter a positive number.")

    def set_pomodoros_until_long_break(self, sender):
        response = rumps.Window(
            title="Set Pomodoros Until Long Break",
            message=f"Enter number of Pomodoros until long break (current: {self.settings.pomodoros_until_long_break}):",
            default_text=str(self.settings.pomodoros_until_long_break),
            dimensions=(200, 20),
        ).run()
        if response.clicked:
            try:
                new_value = (
                    int(response.text)
                    if response.text
                    else self.settings.pomodoros_until_long_break
                )
                if new_value > 0:
                    self.settings.pomodoros_until_long_break = new_value
                    sender.title = f"Pomodoros until Long Break: {self.settings.pomodoros_until_long_break}"
                    self.settings.save_settings()
                else:
                    raise ValueError
            except ValueError:
                rumps.alert("Invalid input. Please enter a positive number.")


if __name__ == "__main__":
    PomodoroApp().run()
