import json
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import pygame
from datetime import datetime
import os
from resource_manager import resource_manager

CONFIG_FILE = "app_config.enc"

def load_json_files():
    json_files = {
        "dictionary": "dictionary.enc",
        "tempo": "tempo.enc",
        "expression": "expression.enc",
        "dynamics": "dynamics.enc",
        "general": "general.enc",
        "articulation": "articulation.enc",
        "signs": "signs.enc"
    }
    data = {}
    for key, file_name in json_files.items():
        json_str = resource_manager.decrypt_file(file_name)
        try:
            data[key] = json.loads(json_str)
        except json.JSONDecodeError:
            data[key] = {}
    return data

class App:                          
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.initialize_sound()
        self.load_data()
        self.load_test_history()
        if not hasattr(self, 'is_dark_theme'):
            self.initialize_theme()
        self.create_persistent_widgets()
        self.create_main_menu()

    def setup_window(self):
        self.root.title("Grade 5 Musical Terms")
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = int((screen_width/2) - (window_width/2))
        y_coordinate = int((screen_height/2) - (window_height/2))
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    def initialize_sound(self):
        pygame.mixer.init()
        self.master_volume = tk.DoubleVar(value=1.0)
        self.click_volume = tk.DoubleVar(value=1.0)
        self.correct_volume = tk.DoubleVar(value=1.0)
        self.incorrect_volume = tk.DoubleVar(value=1.0)
        self.typing_volume = tk.DoubleVar(value=1.0)
        self.click_sound = pygame.mixer.Sound(resource_manager.decrypt_file("click.enc"))
        self.correct_sound = pygame.mixer.Sound(resource_manager.decrypt_file("correct.enc"))
        self.wrong_sound = pygame.mixer.Sound(resource_manager.decrypt_file("wrong.enc"))
        self.typing_sound = pygame.mixer.Sound(resource_manager.decrypt_file("keytype.enc"))
        self.backspace_sound = pygame.mixer.Sound(resource_manager.decrypt_file("backspace.enc"))
        self.space_sound = pygame.mixer.Sound(resource_manager.decrypt_file("spacebar.enc"))

    def play_click_sound(self):
        volume = self.click_volume.get() * self.master_volume.get()
        self.click_sound.set_volume(volume)
        self.click_sound.play()

    def play_typing_sound(self, event):
        volume = self.typing_volume.get() * self.master_volume.get()
        if event.keysym == 'BackSpace':
            self.backspace_sound.set_volume(volume)
            self.backspace_sound.play()
        elif event.keysym == 'space':
            self.space_sound.set_volume(volume)
            self.space_sound.play()
        elif event.char.isalnum():
            self.typing_sound.set_volume(volume)
            self.typing_sound.play()

    def create_button(self, parent, text, command, **kwargs):
        def button_clicked():
            self.play_click_sound()
            command()
        return tk.Button(parent, text=text, command=button_clicked, **kwargs)

    def load_data(self):
        self.data = load_json_files()
        self.current_test_data = None
        self.correct_answers = 0
        self.total_questions = 0

    def initialize_theme(self):
        self.is_dark_theme = True
        self.apply_dark_theme()

    def apply_dark_theme(self):
        self.root.configure(bg='black')
        self.button_bg = '#333333'
        self.button_fg = 'white'
        self.label_fg = 'white'
        self.entry_bg = 'darkgray'
        self.entry_fg = 'black'
        self.update_theme_colors()

    def apply_light_theme(self):
        self.root.configure(bg='white')
        self.button_bg = 'lightgray'
        self.button_fg = 'black'
        self.label_fg = 'black'
        self.entry_bg = 'white'
        self.entry_fg = 'black'
        self.update_theme_colors()

    def update_theme_colors(self):
        if hasattr(self, 'persistent_frame') and self.persistent_frame.winfo_exists():
            self.persistent_frame.configure(bg=self.root['bg'])
            if hasattr(self, 'theme_button'):
                self.theme_button.configure(bg=self.button_bg, fg=self.button_fg)
            if hasattr(self, 'settings_button'):
                self.settings_button.configure(bg=self.button_bg, fg=self.button_fg)
        if hasattr(self, 'main_menu_frame') and self.main_menu_frame.winfo_exists():
            self.main_menu_frame.configure(bg=self.root['bg'])
            for widget in self.main_menu_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=self.root['bg'], fg=self.label_fg)
                elif isinstance(widget, tk.Button):
                    widget.configure(bg=self.button_bg, fg=self.button_fg)

    def toggle_theme(self):
        if self.is_dark_theme:
            self.apply_light_theme()
        else:
            self.apply_dark_theme()
        self.is_dark_theme = not self.is_dark_theme
        self.save_test_history()
        self.update_theme_button()

    def update_theme_button(self):
        theme_icon = "🌞" if self.is_dark_theme else "🌙"
        self.theme_button.config(text=f"{theme_icon} Theme")

    def create_persistent_widgets(self):
        self.persistent_frame = tk.Frame(self.root, bg=self.root['bg'])
        self.persistent_frame.pack(fill='x', pady=5, padx=5)
        self.theme_button = self.create_button(
            self.persistent_frame, 
            text="🌓 Toggle Theme", 
            command=self.toggle_theme,
            font=("Times", 12),
            bg=self.button_bg,
            fg=self.button_fg
        )
        self.theme_button.pack(side='left', padx=5)
        self.settings_button = self.create_button(
            self.persistent_frame, 
            text="⚙ Settings", 
            command=self.show_settings_menu,
            font=("Times", 12),
            bg=self.button_bg,
            fg=self.button_fg
        )
        self.settings_button.pack(side='right', padx=5)

    def create_main_menu(self):
        self.clear_window()
        self.main_menu_frame = tk.Frame(self.root, bg=self.root['bg'])
        self.main_menu_frame.pack(expand=True, fill='both')
        tk.Label(self.main_menu_frame, text="--- Musical Terms.exe ---", 
                font=("Times", 24), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        self.create_button(
            self.main_menu_frame, 
            text="Start Test", 
            command=self.start_test_menu, 
            width=30, 
            font=("Times", 16), 
            bg=self.button_bg, 
            fg=self.button_fg
        ).pack(pady=5, expand=True)
        self.create_button(
            self.main_menu_frame, 
            text="View Dictionary", 
            command=self.view_dictionary_menu, 
            width=30, 
            font=("Times", 16), 
            bg=self.button_bg, 
            fg=self.button_fg
        ).pack(pady=5, expand=True)
        self.create_button(
            self.main_menu_frame, 
            text="Test History",
            command=self.view_test_history, 
            width=30, 
            font=("Times", 16), 
            bg=self.button_bg, 
            fg=self.button_fg
        ).pack(pady=5, expand=True)
        self.create_button(
            self.main_menu_frame, 
            text="Exit", 
            command=self.root.quit, 
            width=30, 
            font=("Times", 16), 
            bg=self.button_bg, 
            fg=self.button_fg
        ).pack(pady=5, expand=True)

    def start_test_menu(self):
        self.clear_window()
        tk.Label(self.root, text="--- Start Test ---", font=("Times", 24), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        self.create_button(self.root, text="Complete Test", 
                          command=lambda: self.run_test(self.data["dictionary"], "Complete Test"), 
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)
        self.create_button(self.root, text="Test by Parts", command=self.test_by_parts_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)
        self.create_button(self.root, text="Back", command=self.create_main_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)

    def test_by_parts_menu(self):
        self.clear_window()
        tk.Label(self.root, text="--- Test by Parts ---", font=("Times", 24), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        parts = {
            "Tempo": "tempo",
            "Expression": "expression",
            "Dynamics": "dynamics",
            "General": "general",
            "Articulation": "articulation",
            "Signs": "signs"
        }
        for part_name, part_key in parts.items():
            self.create_button(self.root, text=part_name, 
                              command=lambda k=part_key, n=part_name: self.run_test(self.data[k], n),
                              width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)
        self.create_button(self.root, text="Back", command=self.start_test_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)

    def run_test(self, test_data, test_type="Unknown"):
        self.clear_window()
        self.current_test_data = list(test_data.items())
        self.current_test_type = test_type
        random.shuffle(self.current_test_data)
        self.correct_answers = 0
        self.total_questions = len(self.current_test_data)
        self.current_question_number = 0
        self.next_question()

    def next_question(self):
        if not self.current_test_data:
            self.show_results()
            return
        self.clear_window()
        self.current_question_number += 1
        progress_text = f"Question {self.current_question_number}/{self.total_questions}"
        tk.Label(self.root, text=progress_text, font=("Times", 14), 
                bg=self.root['bg'], fg=self.label_fg).pack(pady=5, anchor='nw')
        self.current_question = self.current_test_data.pop()
        key, value = self.current_question
        tk.Label(self.root, text=f"What is the meaning of '{key}'?", font=("Times", 20), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        self.answer_entry = tk.Entry(self.root, width=60, font=("Times", 16), bg=self.entry_bg, fg=self.entry_fg)
        self.answer_entry.pack(pady=10, expand=True)
        self.answer_entry.bind("<Return>", lambda event: self.check_answer())
        self.answer_entry.bind("<Key>", lambda e: self.play_typing_sound(e))
        self.answer_entry.focus_set()
        self.create_button(self.root, text="Submit", command=self.check_answer,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)
        self.create_button(self.root, text="Exit Test", command=self.create_main_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)
        self.root.bind('<Escape>', lambda event: self.create_main_menu())

    def check_answer(self):
        user_answer = self.answer_entry.get().strip()
        key, correct_answer = self.current_question
        if user_answer.lower() == correct_answer.lower():
            self.correct_answers += 1
            volume = self.correct_volume.get() * self.master_volume.get()
            self.correct_sound.set_volume(volume)
            self.correct_sound.play()
            messagebox.showinfo("Correct!", "✅ Correct!")
        else:
            volume = self.incorrect_volume.get() * self.master_volume.get()
            self.wrong_sound.set_volume(volume)
            self.wrong_sound.play()
            messagebox.showinfo("Incorrect", f"❌ Incorrect. The correct answer is: {correct_answer}")
        self.next_question()

    def show_results(self):
        test_record = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'test_type': self.current_test_type,
            'score': f"{self.correct_answers}/{self.total_questions}",
            'percentage': f"{(self.correct_answers/self.total_questions)*100:.1f}%"
        }
        self.test_history.append(test_record)
        self.save_test_history()
        self.clear_window()
        tk.Label(self.root, text="Test Complete!", font=("Times", 24), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        tk.Label(self.root, text=f"Score: {self.correct_answers}/{self.total_questions}", font=("Times", 20), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        self.create_button(self.root, text="Back to Main Menu", command=self.create_main_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)

    def view_dictionary_menu(self):
        self.clear_window()
        tk.Label(self.root, text="--- View Dictionary ---", font=("Times", 24), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        self.create_button(self.root, text="View Complete Dictionary", command=lambda: self.show_dictionary(self.data["dictionary"]),
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)
        self.create_button(self.root, text="View by Parts", command=self.view_by_parts_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)
        self.create_button(self.root, text="Back", command=self.create_main_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)

    def view_by_parts_menu(self):
        self.clear_window()
        tk.Label(self.root, text="--- View by Parts ---", font=("Times", 24), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        parts = {
            "Tempo": "tempo",
            "Expression": "expression",
            "Dynamics": "dynamics",
            "General": "general",
            "Articulation": "articulation",
            "Signs": "signs"
        }
        for part_name, part_key in parts.items():
            self.create_button(self.root, text=part_name, command=lambda k=part_key: self.show_dictionary(self.data[k]),
                             width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)
        self.create_button(self.root, text="Back", command=self.view_dictionary_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, expand=True)

    def show_dictionary(self, dictionary):
        self.clear_window()
        tk.Label(self.root, text="Dictionary Content", font=("Times", 24), bg=self.root['bg'], fg=self.label_fg).pack(pady=10, expand=True)
        search_frame = tk.Frame(self.root, bg=self.root['bg'])
        search_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(search_frame, text="Search:", font=("Times", 16), bg=self.root['bg'], fg=self.label_fg).pack(side="left", padx=10)
        search_entry = tk.Entry(search_frame, font=("Times", 16), bg=self.entry_bg, fg=self.entry_fg)
        search_entry.pack(side="left", fill="x", expand=True, padx=10)
        search_entry.bind("<Key>", lambda e: self.play_typing_sound(e))
        content_frame = tk.Frame(self.root, bg=self.root['bg'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        text_widget = tk.Text(content_frame, wrap="word", font=("Courier", 14), bg=self.root['bg'], fg=self.label_fg)
        text_widget.pack(pady=10, padx=10, fill="both", expand=True)
        text_widget.tag_configure("bold", font=("Courier", 14, "bold"), foreground=self.label_fg)
        def update_search(*args):
            search_term = search_entry.get().strip().lower()
            text_widget.config(state="normal")
            text_widget.delete(1.0, "end")
            max_key_length = max(len(key) for key in dictionary.keys())
            for key, value in dictionary.items():
                if search_term in key.lower() or search_term in value.lower():
                    formatted_key = f"{key:<{max_key_length}}"
                    text_widget.insert("end", f"{formatted_key} = ", "bold")
                    text_widget.insert("end", f"{value}\n")
            text_widget.config(state="disabled")
        search_entry.bind('<KeyRelease>', update_search)
        update_search()
        self.create_button(content_frame, text="Back", command=self.view_dictionary_menu,
                          width=30, font=("Times", 16), bg=self.button_bg, fg=self.button_fg).pack(pady=5, side="bottom")

    def view_test_history(self):
        self.clear_window()
        tk.Label(self.root, text="Test History", font=("Times", 24), 
                bg=self.root['bg'], fg=self.label_fg).pack(pady=10)
        canvas = tk.Canvas(self.root, bg=self.root['bg'])
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.root['bg'])
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        ))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        for record in reversed(self.test_history):
            frame = tk.Frame(scroll_frame, bg=self.root['bg'])
            frame.pack(fill='x', pady=5, padx=20)
            tk.Label(frame, text=record['date'], width=18, anchor='w',
                    font=("Courier", 12), bg=self.root['bg'], fg=self.label_fg).pack(side='left')
            tk.Label(frame, text=record['test_type'], width=20, anchor='w',
                    font=("Courier", 12), bg=self.root['bg'], fg=self.label_fg).pack(side='left')
            tk.Label(frame, text=record['score'], width=8, anchor='w',
                    font=("Courier", 12), bg=self.root['bg'], fg=self.label_fg).pack(side='left')
            tk.Label(frame, text=record['percentage'], width=8,
                    font=("Courier", 12), bg=self.root['bg'], fg=self.label_fg).pack(side='left')
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        button_frame = tk.Frame(self.root, bg=self.root['bg'])
        button_frame.pack(pady=10)
        self.create_button(button_frame, text="Back", command=self.create_main_menu,
                          width=15, font=("Times", 14), bg=self.button_bg, fg=self.button_fg).pack(side='left', padx=10)
        self.create_button(button_frame, text="Clear History", command=self.clear_test_history,
                          width=15, font=("Times", 14), bg="#ff4444", fg="white").pack(side='left', padx=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            if widget != self.persistent_frame:
                widget.destroy()

    def load_test_history(self):
        self.master_volume = tk.DoubleVar(value=1.0)
        self.click_volume = tk.DoubleVar(value=1.0)
        self.correct_volume = tk.DoubleVar(value=1.0)
        self.incorrect_volume = tk.DoubleVar(value=1.0)
        self.typing_volume = tk.DoubleVar(value=1.0)
        try:
            if os.path.exists(CONFIG_FILE):
                config_data = resource_manager.decrypt_file(CONFIG_FILE)
                config = json.loads(config_data)
                if config.get('theme') == 'light':
                    self.apply_light_theme()
                    self.is_dark_theme = False
                else:
                    self.apply_dark_theme()
                    self.is_dark_theme = True
                self.master_volume.set(float(config.get('master_volume', 1.0)))
                self.click_volume.set(float(config.get('click_volume', 1.0)))
                self.correct_volume.set(float(config.get('correct_volume', 1.0)))
                self.incorrect_volume.set(float(config.get('incorrect_volume', 1.0)))
                self.typing_volume.set(float(config.get('typing_volume', 1.0)))

            if os.path.exists('test_history.enc'):
                history_data = resource_manager.decrypt_file('test_history.enc')
                if history_data.strip():
                    self.test_history = json.loads(history_data)
                else:
                    self.test_history = []
            else:
                self.test_history = []

        except Exception as e:
            print(f"Error loading data: {str(e)}")
            self.test_history = []

    def save_test_history(self):
        config_data = {
            'theme': 'dark' if self.is_dark_theme else 'light',
            'master_volume': self.master_volume.get(),
            'click_volume': self.click_volume.get(),
            'correct_volume': self.correct_volume.get(),
            'incorrect_volume': self.incorrect_volume.get(),
            'typing_volume': self.typing_volume.get()
        }
        try:
            with open(CONFIG_FILE, 'w') as file:
                json.dump(config_data, file)
        except Exception as e:
            print(f"Error saving config: {e}")
        
        try:
            with open('test_history.enc', 'wb') as file:
                json.dump(self.test_history, file)
        except Exception as e:
            print(f"Error saving history: {e}")

    def show_settings_menu(self):
        self.original_volumes = {
            'master': self.master_volume.get(),
            'click': self.click_volume.get(),
            'correct': self.correct_volume.get(),
            'incorrect': self.incorrect_volume.get(),
            'typing': self.typing_volume.get()
        }
        self.clear_window()
        self.create_settings_menu()

    def create_settings_menu(self):
        self.clear_window()
        tk.Label(self.root, text="Settings", font=("Times", 24), 
                bg=self.root['bg'], fg=self.label_fg).pack(pady=10)
        
        volume_frame = tk.Frame(self.root, bg=self.root['bg'])
        volume_frame.pack(pady=10)

        tk.Label(volume_frame, text="Master Volume:", bg=self.root['bg'], fg=self.label_fg).grid(row=0, column=0, sticky='w')
        tk.Scale(volume_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                variable=self.master_volume, bg=self.root['bg'], fg=self.label_fg).grid(row=0, column=1, padx=10)

        tk.Label(volume_frame, text="Button Clicks:", bg=self.root['bg'], fg=self.label_fg).grid(row=1, column=0, sticky='w')
        tk.Scale(volume_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                variable=self.click_volume, bg=self.root['bg'], fg=self.label_fg).grid(row=1, column=1, padx=10)

        tk.Label(volume_frame, text="Correct Sounds:", bg=self.root['bg'], fg=self.label_fg).grid(row=2, column=0, sticky='w')
        tk.Scale(volume_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                variable=self.correct_volume, bg=self.root['bg'], fg=self.label_fg).grid(row=2, column=1, padx=10)

        tk.Label(volume_frame, text="Incorrect Sounds:", bg=self.root['bg'], fg=self.label_fg).grid(row=3, column=0, sticky='w')
        tk.Scale(volume_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                variable=self.incorrect_volume, bg=self.root['bg'], fg=self.label_fg).grid(row=3, column=1, padx=10)

        tk.Label(volume_frame, text="Typing Sounds:", bg=self.root['bg'], fg=self.label_fg).grid(row=4, column=0, sticky='w')
        tk.Scale(volume_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal',
                variable=self.typing_volume, bg=self.root['bg'], fg=self.label_fg).grid(row=4, column=1, padx=10)

        button_frame = tk.Frame(self.root, bg=self.root['bg'])
        button_frame.pack(pady=20)
        
        self.create_button(button_frame, text="Save", command=self.save_settings,
                          width=15, font=("Times", 14), bg="#4CAF50", fg="white").pack(side='left', padx=10)
        
        self.create_button(button_frame, text="Cancel", command=self.cancel_settings,
                          width=15, font=("Times", 14), bg="#f44336", fg="white").pack(side='left', padx=10)

    def save_settings(self):
        self.save_test_history()
        self.create_main_menu()

    def cancel_settings(self):
        self.master_volume.set(self.original_volumes['master'])
        self.click_volume.set(self.original_volumes['click'])
        self.correct_volume.set(self.original_volumes['correct'])
        self.incorrect_volume.set(self.original_volumes['incorrect'])
        self.typing_volume.set(self.original_volumes['typing'])
        self.create_main_menu()

    def clear_test_history(self):
        if messagebox.askyesno("Confirm Clear", "Delete ALL test history?\nThis cannot be undone!"):
            self.test_history = []
            self.save_test_history()
            messagebox.showinfo("Cleared", "All test history has been deleted")
            self.view_test_history()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()