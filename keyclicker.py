import tkinter as tk
from tkinter import ttk
import threading
from pynput import mouse
from pynput.keyboard import Listener, Key, Controller as KeyboardController
import time
import os

class MouseClicker:
    def __init__(self, button, interval, stop_event):
        self.button = button
        self.interval = interval
        self.stop_event = stop_event

    def start(self):
        self.perform_mouse_click()

    def perform_mouse_click(self):
        while not self.stop_event.is_set():
            mouse.Controller().press(self.button)
            time.sleep(self.interval)
            mouse.Controller().release(self.button)

class HotkeysApp:
    def __init__(self, master):
        self.master = master
        master.title("Key Clicker (V.1.0)")
        icon = tk.PhotoImage(file="arrow.ico")
        root.iconphoto(True, icon)

        # Create a frame for centering
        center_frame = tk.Frame(master)
        center_frame.pack(expand=True)

        # Radiobuttons for action selection
        self.action_var = tk.StringVar()
        self.key_press_button = ttk.Radiobutton(center_frame, text="Key Press", variable=self.action_var, value="Key Press", command=self.show_input)
        self.mouse_click_button = ttk.Radiobutton(center_frame, text="Mouse Click", variable=self.action_var, value="Mouse Click", command=self.show_mouse_options)

        self.key_press_button.grid(row=0, column=0, padx=5, sticky="w")
        self.mouse_click_button.grid(row=0, column=1, padx=5, sticky="w")

        # Mouse options
        self.mouse_button_var = tk.StringVar()
        self.mouse_button_var.set("Left")  # Default value

        self.mouse_button_label = tk.Label(center_frame, text="Mouse Button")
        self.mouse_button_menu = ttk.Combobox(center_frame, textvariable=self.mouse_button_var, values=["Left", "Right"])

        self.interval_label_mouse = tk.Label(center_frame, text="Interval (ms)")
        self.interval_entry_mouse = tk.Entry(center_frame)

        self.mouse_button_menu.grid(row=1, column=0, columnspan=2, pady=5)
        self.mouse_button_label.grid(row=2, column=0, columnspan=2, pady=5)
        self.interval_label_mouse.grid(row=3, column=0, columnspan=2, pady=5)
        self.interval_entry_mouse.grid(row=4, column=0, columnspan=2, pady=5)

        # Entry for input
        self.input_label = tk.Label(center_frame, text="Key")
        self.input_entry = tk.Entry(center_frame)

        # Entry for interval
        self.interval_label = tk.Label(center_frame, text="Interval (ms)")
        self.interval_entry = tk.Entry(center_frame)

        self.input_label.grid(row=5, column=0, columnspan=2, pady=5)
        self.input_entry.grid(row=6, column=0, columnspan=2, pady=5)
        self.interval_label.grid(row=7, column=0, columnspan=2, pady=5)
        self.interval_entry.grid(row=8, column=0, columnspan=2, pady=5)

        # Buttons for start and stop
        self.start_button = tk.Button(center_frame, text="Start (⏎)", command=self.start_listener)
        self.stop_button = tk.Button(center_frame, text="Stop (⏎)", command=self.stop_listener)

        self.start_button.grid(row=9, column=0, padx=5, pady=10, sticky="e")
        self.stop_button.grid(row=9, column=1, padx=5, pady=10, sticky="w")
        self.stop_button.config(state=tk.DISABLED)

        self.running = False
        self.listener_thread = None
        self.mouse_clicker = None

        # Hide Mouse options, Input, and Interval entries initially
        self.hide_mouse_options()
        self.hide_input()

        self.stop_event = threading.Event()

        # Keyboard listener for Ctrl+1 and Ctrl+2
        self.keyboard_listener = Listener(on_press=self.on_keyboard_press)

    def show_mouse_options(self):
        self.mouse_button_label.grid(row=2, column=0, columnspan=2, pady=5)
        self.mouse_button_menu.grid(row=3, column=0, columnspan=2, pady=5)
        self.interval_label_mouse.grid(row=4, column=0, columnspan=2, pady=5)
        self.interval_entry_mouse.grid(row=5, column=0, columnspan=2, pady=5)

        # Hide Input and Interval entries
        self.hide_input()

    def hide_mouse_options(self):
        self.mouse_button_label.grid_forget()
        self.mouse_button_menu.grid_forget()
        self.interval_label_mouse.grid_forget()
        self.interval_entry_mouse.grid_forget()

    def show_input(self):
        self.input_label.grid(row=5, column=0, columnspan=2, pady=5)
        self.input_entry.grid(row=6, column=0, columnspan=2, pady=5)
        self.interval_label.grid(row=7, column=0, columnspan=2, pady=5)
        self.interval_entry.grid(row=8, column=0, columnspan=2, pady=5)

        # Hide Mouse options
        self.hide_mouse_options()

    def hide_input(self):
        self.input_label.grid_forget()
        self.input_entry.grid_forget()
        self.interval_label.grid_forget()
        self.interval_entry.grid_forget()

    def start_listener(self):
        if not self.running:
            action = self.action_var.get()

            if action == "Key Press":
                user_input = self.input_entry.get()
                interval_str = self.interval_entry.get()
            elif action == "Mouse Click":
                user_input = self.mouse_button_var.get()
                interval_str = self.interval_entry_mouse.get()

            if not user_input or not interval_str.isdigit():
                # Handle invalid input
                return

            interval = int(interval_str) / 1000.0  # convert to seconds

            if action == "Key Press":
                self.listener_thread = threading.Thread(target=self.press_key, args=(user_input, interval))
            elif action == "Mouse Click":
                self.listener_thread = threading.Thread(target=self.click_mouse, args=(user_input, interval))
            else:
                # Handle unknown action
                return

            self.stop_event.clear()  # Clear the stop event flag
            self.listener_thread.start()

            # Add a 3-second delay
            time.sleep(3)

            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Periodically check the thread status and update the GUI
            self.master.after(100, self.check_thread_status)

    def press_key(self, key, interval):
        with Listener(on_press=self.on_press) as listener:
            while not self.stop_event.is_set():
                KeyboardController().press(key)
                time.sleep(interval)
                KeyboardController().release(key)

    def click_mouse(self, button, interval):
        button_mapping = {
            "Left": mouse.Button.left,
            "Right": mouse.Button.right,
            # Add more button mappings as needed
        }

        button_object = button_mapping.get(button, mouse.Button.left)  # Default to left button if not found

        self.mouse_clicker = MouseClicker(button_object, interval, self.stop_event)
        self.mouse_clicker.start()
        self.update_label()

    def is_running(self):
        return self.running

    def update_label(self):
        if self.running:
            self.input_label.config(text=f"Mouse Click: {self.mouse_button_var.get()}")
            self.master.after(100, self.update_label)

    def on_press(self, key):
        if key == Key.esc:
            self.stop_listener()
        else:
            # Update the label text with the key press information
            self.input_label.config(text=f"Key Press: {key.char}")

    def check_thread_status(self):
        if self.listener_thread and self.listener_thread.is_alive():
            self.master.after(100, self.check_thread_status)
        else:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def on_keyboard_press(self, key):
        if key == Key.enter:
            if not self.running:
                self.start_listener()
            else:
                self.stop_listener()

    # Add the stop_listener method
    def stop_listener(self):
        if self.running:
            self.stop_event.set()  # Set the stop event flag
            if self.mouse_clicker:
                self.mouse_clicker.start()  # Stop the mouse clicker thread
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    # Removed the line to destroy the window

if __name__ == "__main__":
    root = tk.Tk()
    app = HotkeysApp(root)

    # Start the keyboard listener
    app.keyboard_listener.start()

    root.geometry("300x300")
    root.mainloop()