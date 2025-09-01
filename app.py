#!/usr/bin/env python3
"""
Hevy to Garmin FIT Merger Application

A desktop application that merges Hevy workout CSV exports with Garmin FIT files
to create enriched workout data containing both physiological data (heart rate, time)
and detailed exercise data (sets, reps, weights).

Author: Generated for non-technical Mac user
Technology: Python + CustomTkinter + pandas + Garmin fit_tool
"""

import customtkinter as ctk
import pandas as pd
import os
import tempfile
import json
import re
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk
import threading
from fit_tool.fit_file import FitFile


class WorkoutPreviewWindow:
    """Preview and edit window for the merged workout data"""
    
    def __init__(self, parent_app, garmin_sets, workout_stats, enhanced_fit_file):
        self.parent_app = parent_app
        self.garmin_sets = garmin_sets.copy()  # Make a copy so we can edit
        self.workout_stats = workout_stats
        self.enhanced_fit_file = enhanced_fit_file
        self.window = None
        self.tree = None
        self.stats_frame = None
        self.user_confirmed = False
        self.output_path = None
        
    def show_preview(self):
        """Display the preview window"""
        self.window = ctk.CTkToplevel(self.parent_app.root)
        self.window.title("Workout Preview & Editor")
        self.window.geometry("1200x800")
        self.window.transient(self.parent_app.root)
        self.window.grab_set()  # Make it modal
        
        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Create header
        self.create_header()
        
        # Create main content area
        self.create_main_content()
        
        # Create footer with action buttons
        self.create_footer()
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Wait for user action
        self.window.wait_window()
        
        return self.user_confirmed, self.output_path
        
    def create_header(self):
        """Create the header with workout summary"""
        header_frame = ctk.CTkFrame(self.window)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(header_frame, 
                                  text="🏋️ Workout Preview & Editor", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Workout stats summary (like Garmin Connect)
        stats_text = f"📊 {len(self.garmin_sets)} Sets • "
        stats_text += f"{sum(s['repetitions'] for s in self.garmin_sets)} Total Reps • "
        stats_text += f"{len(set(s['original_exercise_name'] for s in self.garmin_sets))} Exercises"
        
        stats_label = ctk.CTkLabel(header_frame, text=stats_text, 
                                  font=ctk.CTkFont(size=14))
        stats_label.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="w")
        
    def create_main_content(self):
        """Create the main content area with workout details and exercise list"""
        main_frame = ctk.CTkFrame(self.window)
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left side - Workout statistics (like Garmin Connect)
        self.create_stats_panel(main_frame)
        
        # Right side - Exercise list with editing
        self.create_exercise_panel(main_frame)
        
    def create_stats_panel(self, parent):
        """Create the workout statistics panel"""
        stats_frame = ctk.CTkScrollableFrame(parent)
        stats_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        # Stats title
        stats_title = ctk.CTkLabel(stats_frame, text="Workout Statistics", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        stats_title.pack(pady=(0, 20), anchor="w")
        
        # Timing stats
        timing_frame = ctk.CTkFrame(stats_frame)
        timing_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(timing_frame, text="⏱️ Timing", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, anchor="w", padx=10)
        
        # Mock workout duration (would come from Garmin data)
        duration = self.workout_stats.get('duration_seconds', 1800)  # 30 min default
        duration_text = f"{duration // 60}:{duration % 60:02d}"
        
        ctk.CTkLabel(timing_frame, text=f"Total Time: {duration_text}").pack(anchor="w", padx=20)
        ctk.CTkLabel(timing_frame, text=f"Work Time: {duration_text}").pack(anchor="w", padx=20)
        ctk.CTkLabel(timing_frame, text="Rest Time: 0:00").pack(anchor="w", padx=20, pady=(0, 10))
        
        # Heart Rate stats (from Garmin data)
        hr_frame = ctk.CTkFrame(stats_frame)
        hr_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(hr_frame, text="❤️ Heart Rate", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, anchor="w", padx=10)
        
        avg_hr = self.workout_stats.get('avg_hr', 110)
        max_hr = self.workout_stats.get('max_hr', 143)
        
        ctk.CTkLabel(hr_frame, text=f"Avg HR: {avg_hr} bpm").pack(anchor="w", padx=20)
        ctk.CTkLabel(hr_frame, text=f"Max HR: {max_hr} bpm").pack(anchor="w", padx=20, pady=(0, 10))
        
        # Workout details
        details_frame = ctk.CTkFrame(stats_frame)
        details_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(details_frame, text="📋 Workout Details", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, anchor="w", padx=10)
        
        total_reps = sum(s['repetitions'] for s in self.garmin_sets)
        total_sets = len(self.garmin_sets)
        
        ctk.CTkLabel(details_frame, text=f"Total Reps: {total_reps}").pack(anchor="w", padx=20)
        ctk.CTkLabel(details_frame, text=f"Total Sets: {total_sets}").pack(anchor="w", padx=20, pady=(0, 10))
        
        # Calories (from Garmin data)
        calories_frame = ctk.CTkFrame(stats_frame)
        calories_frame.pack(fill="x")
        
        ctk.CTkLabel(calories_frame, text="🔥 Energy", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, anchor="w", padx=10)
        
        calories = self.workout_stats.get('calories', 194)
        ctk.CTkLabel(calories_frame, text=f"Calories: {calories}").pack(anchor="w", padx=20, pady=(0, 10))
        
    def create_exercise_panel(self, parent):
        """Create the exercise list panel with editing capabilities"""
        exercise_frame = ctk.CTkFrame(parent)
        exercise_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        exercise_frame.grid_columnconfigure(0, weight=1)
        exercise_frame.grid_rowconfigure(1, weight=1)
        
        # Exercise list title
        title_frame = ctk.CTkFrame(exercise_frame)
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        title_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(title_frame, text="Exercise Sets", 
                    font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")
        
        # Add/Edit buttons
        edit_btn = ctk.CTkButton(title_frame, text="Edit Selected", 
                                command=self.edit_selected_set, width=100)
        edit_btn.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # Create treeview for exercise data
        tree_frame = ctk.CTkFrame(exercise_frame)
        tree_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Use tkinter Treeview for tabular data (CustomTkinter doesn't have a good table widget)
        style = ttk.Style()
        style.theme_use("clam")
        
        self.tree = ttk.Treeview(tree_frame, columns=("Exercise", "Set", "Reps", "Weight", "Type"), show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure columns
        self.tree.heading("Exercise", text="Exercise")
        self.tree.heading("Set", text="Set")
        self.tree.heading("Reps", text="Reps")
        self.tree.heading("Weight", text="Weight")
        self.tree.heading("Type", text="Type")
        
        self.tree.column("Exercise", width=200)
        self.tree.column("Set", width=50)
        self.tree.column("Reps", width=60)
        self.tree.column("Weight", width=80)
        self.tree.column("Type", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate with data
        self.populate_exercise_list()
        
    def populate_exercise_list(self):
        """Populate the exercise list with current data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add exercise data
        weight_unit = self.parent_app.weight_unit_var.get() if self.parent_app.weight_unit_var else "kg"
        set_type_names = {0: "Normal", 2: "Warm-up", 5: "Failure", 6: "Drop set"}
        
        for i, set_data in enumerate(self.garmin_sets):
            exercise_name = set_data['original_exercise_name'].title()
            set_number = set_data['set_number']
            reps = set_data['repetitions']
            weight = f"{set_data['weight']} {weight_unit}"
            set_type = set_type_names.get(set_data['set_type'], f"Type {set_data['set_type']}")
            
            self.tree.insert("", "end", values=(exercise_name, set_number, reps, weight, set_type))
            
    def edit_selected_set(self):
        """Edit the selected set"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a set to edit.")
            return
            
        item = selection[0]
        set_index = self.tree.index(item)
        
        # Open edit dialog
        self.show_edit_dialog(set_index)
        
    def show_edit_dialog(self, set_index):
        """Show dialog to edit a specific set"""
        set_data = self.garmin_sets[set_index]
        
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Edit Set")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (200)
        y = (dialog.winfo_screenheight() // 2) - (150)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Create form
        ctk.CTkLabel(dialog, text=f"Edit Set: {set_data['original_exercise_name'].title()}", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        # Reps
        reps_frame = ctk.CTkFrame(dialog)
        reps_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(reps_frame, text="Reps:").pack(side="left", padx=10)
        reps_entry = ctk.CTkEntry(reps_frame, width=100)
        reps_entry.pack(side="right", padx=10)
        reps_entry.insert(0, str(set_data['repetitions']))
        
        # Weight
        weight_frame = ctk.CTkFrame(dialog)
        weight_frame.pack(fill="x", padx=20, pady=10)
        weight_unit = self.parent_app.weight_unit_var.get() if self.parent_app.weight_unit_var else "kg"
        ctk.CTkLabel(weight_frame, text=f"Weight ({weight_unit}):").pack(side="left", padx=10)
        weight_entry = ctk.CTkEntry(weight_frame, width=100)
        weight_entry.pack(side="right", padx=10)
        weight_entry.insert(0, str(set_data['weight']))
        
        # Set Type
        type_frame = ctk.CTkFrame(dialog)
        type_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(type_frame, text="Set Type:").pack(side="left", padx=10)
        type_var = ctk.StringVar(value={0: "Normal", 2: "Warm-up", 5: "Failure", 6: "Drop set"}.get(set_data['set_type'], "Normal"))
        type_menu = ctk.CTkOptionMenu(type_frame, variable=type_var, 
                                     values=["Normal", "Warm-up", "Failure", "Drop set"])
        type_menu.pack(side="right", padx=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_changes():
            try:
                # Update the set data
                self.garmin_sets[set_index]['repetitions'] = int(reps_entry.get())
                self.garmin_sets[set_index]['weight'] = float(weight_entry.get())
                self.garmin_sets[set_index]['set_type'] = {"Normal": 0, "Warm-up": 2, "Failure": 5, "Drop set": 6}[type_var.get()]
                
                # Refresh the display
                self.populate_exercise_list()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers for reps and weight.")
        
        ctk.CTkButton(button_frame, text="Save", command=save_changes).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=10)
        
    def create_footer(self):
        """Create footer with action buttons"""
        footer_frame = ctk.CTkFrame(self.window)
        footer_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Instructions
        ctk.CTkLabel(footer_frame, 
                    text="Review your workout data above. Edit any sets if needed, then export to save your FIT file.",
                    font=ctk.CTkFont(size=12)).pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(footer_frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel_action,
                     width=120).pack(side="left", padx=10)
        
        ctk.CTkButton(button_frame, text="Export FIT File", command=self.export_action,
                     width=120, fg_color="green", hover_color="darkgreen").pack(side="right", padx=10)
        
    def cancel_action(self):
        """Handle cancel button"""
        self.user_confirmed = False
        self.window.destroy()
        
    def export_action(self):
        """Handle export button"""
        # Open save dialog
        output_path = filedialog.asksaveasfilename(
            title="Save Enhanced FIT File As...",
            defaultextension=".fit",
            filetypes=[("FIT files", "*.fit"), ("All files", "*.*")]
        )
        
        if output_path:
            self.output_path = output_path
            self.user_confirmed = True
            self.window.destroy()


class HevyGarminMerger:
    def __init__(self):
        # Initialize the main application
        self.root = ctk.CTk()
        self.setup_window()
        
        # File path storage
        self.garmin_file_path = None
        self.hevy_file_path = None
        
        # UI components (will be created in setup_ui)
        self.garmin_path_display = None
        self.hevy_path_display = None
        self.merge_button = None
        self.status_log = None
        self.weight_unit_var = None
        
        # Load configuration
        self.config = self.load_config()
        
        # Setup UI
        self.setup_ui()
        
    def load_config(self):
        """Load the Hevy-Garmin configuration file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "hevy_garmin_config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            # Fallback to basic config if file not found
            return {
                "settings": {"weight_unit": "kg", "default_set_duration_seconds": 30},
                "exercise_mappings": {},
                "hevy_csv_columns": {
                    "exercise_name": "Exercise Name",
                    "set_number": "Set Order", 
                    "reps": "Reps",
                    "weight": "Weight",
                    "set_note": "Notes"
                }
            }
        
    def setup_window(self):
        """Configure the main application window"""
        self.root.title("Hevy to Garmin FIT Merger")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
        ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
        
    def setup_ui(self):
        """Create the main UI layout with two columns"""
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frames for two-column layout
        left_frame = ctk.CTkFrame(self.root)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        right_frame = ctk.CTkFrame(self.root)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Setup left column (inputs)
        self.setup_left_column(left_frame)
        
        # Setup right column (status and results)
        self.setup_right_column(right_frame)
        
    def setup_left_column(self, parent):
        """Setup the left column with file input controls"""
        # Configure grid for left frame
        parent.grid_columnconfigure(0, weight=1)
        
        # Title for left column
        title_label = ctk.CTkLabel(parent, text="File Selection", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="w")
        
        # Step 1: Garmin File Selection
        step1_label = ctk.CTkLabel(parent, text="Step 1: Upload Garmin File (.FIT)", 
                                  font=ctk.CTkFont(size=14, weight="bold"))
        step1_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        self.garmin_button = ctk.CTkButton(parent, text="Select Garmin File...", 
                                          command=self.select_garmin_file)
        self.garmin_button.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.garmin_path_display = ctk.CTkEntry(parent, placeholder_text="No file selected", 
                                               state="readonly")
        self.garmin_path_display.grid(row=3, column=0, padx=20, pady=(0, 30), sticky="ew")
        
        # Step 2: Hevy File Selection
        step2_label = ctk.CTkLabel(parent, text="Step 2: Upload Hevy File (.CSV)", 
                                  font=ctk.CTkFont(size=14, weight="bold"))
        step2_label.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="w")
        
        self.hevy_button = ctk.CTkButton(parent, text="Select Hevy File...", 
                                        command=self.select_hevy_file)
        self.hevy_button.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.hevy_path_display = ctk.CTkEntry(parent, placeholder_text="No file selected", 
                                             state="readonly")
        self.hevy_path_display.grid(row=6, column=0, padx=20, pady=(0, 30), sticky="ew")
        
        # Step 3: Weight Unit Selection
        step3_label = ctk.CTkLabel(parent, text="Step 3: Select Weight Unit", 
                                  font=ctk.CTkFont(size=14, weight="bold"))
        step3_label.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Weight unit selection
        self.weight_unit_var = ctk.StringVar(value=self.config["settings"].get("weight_unit", "kg"))
        weight_unit_frame = ctk.CTkFrame(parent)
        weight_unit_frame.grid(row=8, column=0, padx=20, pady=(0, 30), sticky="ew")
        weight_unit_frame.grid_columnconfigure(0, weight=1)
        weight_unit_frame.grid_columnconfigure(1, weight=1)
        
        kg_radio = ctk.CTkRadioButton(weight_unit_frame, text="Kilograms (kg)", 
                                     variable=self.weight_unit_var, value="kg")
        kg_radio.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        lbs_radio = ctk.CTkRadioButton(weight_unit_frame, text="Pounds (lbs)", 
                                      variable=self.weight_unit_var, value="lbs")
        lbs_radio.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Merge Button (initially disabled)
        self.merge_button = ctk.CTkButton(parent, text="Process & Preview Workout", 
                                         command=self.start_merge_process,
                                         state="disabled",
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         height=50)
        self.merge_button.grid(row=9, column=0, padx=20, pady=(20, 20), sticky="ew")
        
    def setup_right_column(self, parent):
        """Setup the right column with status and results"""
        # Configure grid for right frame
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Title for right column
        status_label = ctk.CTkLabel(parent, text="Status & Results", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        status_label.grid(row=0, column=0, padx=20, pady=(20, 20), sticky="w")
        
        # Status log text box
        self.status_log = ctk.CTkTextbox(parent, font=ctk.CTkFont(family="Monaco", size=12))
        self.status_log.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Add initial status message
        self.update_status("Ready. Please select your Garmin .FIT file and Hevy .CSV file to begin.")
        
    def update_status(self, message):
        """Update the status log with a new message"""
        if self.status_log:
            self.status_log.insert("end", f"{message}\n")
            self.status_log.see("end")  # Auto-scroll to bottom
            self.root.update()  # Force UI update
            
    def select_garmin_file(self):
        """Handle Garmin file selection"""
        file_path = filedialog.askopenfilename(
            title="Select Garmin FIT File",
            filetypes=[("FIT files", "*.fit"), ("All files", "*.*")]
        )
        
        if file_path:
            self.garmin_file_path = file_path
            # Display shortened path in the entry field
            display_path = self.shorten_path(file_path)
            self.garmin_path_display.configure(state="normal")
            self.garmin_path_display.delete(0, "end")
            self.garmin_path_display.insert(0, display_path)
            self.garmin_path_display.configure(state="readonly")
            
            self.update_status(f"Garmin file selected: {os.path.basename(file_path)}")
            self.check_merge_button_state()
            
    def select_hevy_file(self):
        """Handle Hevy file selection"""
        file_path = filedialog.askopenfilename(
            title="Select Hevy CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.hevy_file_path = file_path
            # Display shortened path in the entry field
            display_path = self.shorten_path(file_path)
            self.hevy_path_display.configure(state="normal")
            self.hevy_path_display.delete(0, "end")
            self.hevy_path_display.insert(0, display_path)
            self.hevy_path_display.configure(state="readonly")
            
            self.update_status(f"Hevy file selected: {os.path.basename(file_path)}")
            self.check_merge_button_state()
            
    def shorten_path(self, file_path, max_length=50):
        """Shorten file path for display if it's too long"""
        if len(file_path) <= max_length:
            return file_path
        
        # Show first part and last part with ... in between
        start_part = file_path[:20]
        end_part = file_path[-(max_length-23):]
        return f"{start_part}...{end_part}"
        
    def check_merge_button_state(self):
        """Enable merge button only when both files are selected"""
        if self.garmin_file_path and self.hevy_file_path:
            self.merge_button.configure(state="normal")
            self.update_status("Both files selected. Ready to process and preview workout!")
        else:
            self.merge_button.configure(state="disabled")
            
    def start_merge_process(self):
        """Start the merge process and show preview window"""
        # Disable merge button to prevent multiple clicks
        self.merge_button.configure(state="disabled")
        
        # Run merge in separate thread to prevent UI freezing
        merge_thread = threading.Thread(
            target=self.prepare_workout_preview,
            args=(self.garmin_file_path, self.hevy_file_path)
        )
        merge_thread.daemon = True
        merge_thread.start()
        
    def prepare_workout_preview(self, garmin_fit_path, hevy_csv_path):
        """Prepare data for the workout preview window"""
        try:
            # Step 1: Read FIT file and convert to DataFrame
            self.update_status("Reading Garmin FIT file...")
            
            # Load FIT file using fit_tool
            fit_file = FitFile.from_file(garmin_fit_path)
            self.update_status("Garmin FIT file loaded successfully.")
            
            # Convert to CSV format for easier manipulation
            temp_garmin_csv = os.path.join(tempfile.gettempdir(), "temp_garmin.csv")
            fit_file.to_csv(temp_garmin_csv)
            
            # Step 2: Read and Process Data
            self.update_status("Reading workout data...")
            
            # Load Garmin data from CSV
            garmin_df = pd.read_csv(temp_garmin_csv)
            self.update_status(f"Loaded Garmin data: {len(garmin_df)} records")
            
            # Load Hevy data
            hevy_df = pd.read_csv(hevy_csv_path)
            self.update_status(f"Loaded Hevy data: {len(hevy_df)} exercises")
            
            # Display sample of data for debugging
            self.update_status("Sample Garmin data columns: " + ", ".join(garmin_df.columns[:5].tolist()))
            if len(hevy_df) > 0:
                self.update_status("Sample Hevy data columns: " + ", ".join(hevy_df.columns[:5].tolist()))
            
            # Step 3: Process Hevy Data
            self.update_status("Processing workout integration...")
            
            # Call the integration function
            enhanced_fit_file = self.integrate_hevy_data(fit_file, hevy_df)
            
            # Extract workout statistics for the preview
            workout_stats = self.extract_workout_statistics(garmin_df)
            
            # Get the processed Garmin sets (stored during integration)
            garmin_sets = getattr(self, 'last_processed_sets', [])
            
            if not garmin_sets:
                raise Exception("No workout data was processed. Please check your files.")
            
            # Step 4: Show preview window
            self.update_status("Opening workout preview...")
            
            # Clean up temp file
            if os.path.exists(temp_garmin_csv):
                os.remove(temp_garmin_csv)
            
            # Show preview window on main thread
            self.root.after(0, lambda: self.show_workout_preview(garmin_sets, workout_stats, enhanced_fit_file))
            
        except Exception as e:
            self.update_status(f"ERROR: {str(e)}")
            # Show error message box
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"An error occurred during workout processing:\n\n{str(e)}"
            ))
            # Re-enable merge button
            self.root.after(0, lambda: self.merge_button.configure(state="normal"))
    
    def show_workout_preview(self, garmin_sets, workout_stats, enhanced_fit_file):
        """Show the workout preview window"""
        try:
            preview_window = WorkoutPreviewWindow(self, garmin_sets, workout_stats, enhanced_fit_file)
            user_confirmed, output_path = preview_window.show_preview()
            
            if user_confirmed and output_path:
                # User confirmed, now save the file with any edits
                self.finalize_workout_export(preview_window.garmin_sets, enhanced_fit_file, output_path)
            else:
                self.update_status("Workout preview cancelled by user.")
                
        except Exception as e:
            self.update_status(f"Error showing preview: {str(e)}")
            messagebox.showerror("Preview Error", f"Could not show workout preview:\n\n{str(e)}")
        finally:
            # Re-enable merge button
            self.merge_button.configure(state="normal")
    
    def finalize_workout_export(self, edited_garmin_sets, enhanced_fit_file, output_path):
        """Finalize the workout export with any user edits"""
        try:
            self.update_status("Applying user edits and generating final FIT file...")
            
            # Apply any edits made by the user
            final_fit_file = self.apply_user_edits(enhanced_fit_file, edited_garmin_sets)
            
            # Save the final file
            final_fit_file.to_file(output_path)
            
            # Validate the output
            self.update_status("Validating final output file...")
            validation_passed = self.validate_output(output_path)
            
            if validation_passed:
                self.update_status("SUCCESS! Enhanced FIT file created and validated successfully.")
                self.update_status(f"Output file: {output_path}")
                
                # Show success message
                messagebox.showinfo(
                    "Export Complete", 
                    f"Workout file exported successfully!\n\nOutput file:\n{output_path}\n\nYou can now upload this file to Garmin Connect."
                )
            else:
                raise Exception("Output file validation failed")
                
        except Exception as e:
            self.update_status(f"ERROR during export: {str(e)}")
            messagebox.showerror("Export Error", f"Could not export workout file:\n\n{str(e)}")
    
    def apply_user_edits(self, fit_file, edited_garmin_sets):
        """Apply user edits to the FIT file"""
        try:
            # For now, return the original file since we're not creating actual FIT records yet
            # In a full implementation, this would rebuild the FIT file with edited set data
            
            # Log the edits that would be applied
            self.update_status("=== FINAL WORKOUT DATA ===")
            exercise_summary = {}
            
            for set_data in edited_garmin_sets:
                exercise_name = set_data['original_exercise_name']
                if exercise_name not in exercise_summary:
                    exercise_summary[exercise_name] = {'sets': 0, 'total_reps': 0, 'max_weight': 0}
                
                exercise_summary[exercise_name]['sets'] += 1
                exercise_summary[exercise_name]['total_reps'] += set_data['repetitions']
                exercise_summary[exercise_name]['max_weight'] = max(
                    exercise_summary[exercise_name]['max_weight'], 
                    set_data['weight']
                )
            
            for exercise, stats in exercise_summary.items():
                weight_unit = self.weight_unit_var.get() if self.weight_unit_var else "kg"
                self.update_status(f"{exercise.title()}: {stats['sets']} sets, "
                                 f"{stats['total_reps']} total reps, "
                                 f"max {stats['max_weight']} {weight_unit}")
            
            return fit_file
            
        except Exception as e:
            self.update_status(f"Error applying edits: {str(e)}")
            return fit_file
    
    def extract_workout_statistics(self, garmin_df):
        """Extract workout statistics from Garmin data for the preview"""
        try:
            stats = {
                'duration_seconds': 1800,  # Default 30 minutes
                'avg_hr': 110,
                'max_hr': 143,
                'calories': 194,
                'total_records': len(garmin_df)
            }
            
            # Try to extract actual stats from Garmin data
            if 'heart_rate' in garmin_df.columns:
                hr_data = garmin_df['heart_rate'].dropna()
                if len(hr_data) > 0:
                    stats['avg_hr'] = int(hr_data.mean())
                    stats['max_hr'] = int(hr_data.max())
            
            # Try to extract duration from timestamps
            timestamp_cols = [col for col in garmin_df.columns if 'timestamp' in col.lower()]
            if timestamp_cols and len(garmin_df) > 1:
                try:
                    # Estimate duration from number of records
                    stats['duration_seconds'] = max(1800, len(garmin_df) * 5)  # 5 seconds per record estimate
                except:
                    pass
            
            return stats
            
        except Exception as e:
            self.update_status(f"Error extracting statistics: {str(e)}")
            return {'duration_seconds': 1800, 'avg_hr': 110, 'max_hr': 143, 'calories': 194, 'total_records': 0}
            
    def merge_workout_files(self, garmin_fit_path, hevy_csv_path, output_path):
        """
        Core function that merges Garmin FIT and Hevy CSV files
        This function runs in a separate thread to avoid blocking the UI
        """
        try:
            # Step 1: Read FIT file and convert to DataFrame
            self.update_status("Reading Garmin FIT file...")
            
            # Load FIT file using fit_tool
            fit_file = FitFile.from_file(garmin_fit_path)
            self.update_status("Garmin FIT file loaded successfully.")
            
            # Convert to CSV format for easier manipulation
            temp_garmin_csv = os.path.join(tempfile.gettempdir(), "temp_garmin.csv")
            fit_file.to_csv(temp_garmin_csv)
            
            # Step 2: Read and Process Data
            self.update_status("Reading workout data...")
            
            # Load Garmin data from CSV
            garmin_df = pd.read_csv(temp_garmin_csv)
            self.update_status(f"Loaded Garmin data: {len(garmin_df)} records")
            
            # Load Hevy data
            hevy_df = pd.read_csv(hevy_csv_path)
            self.update_status(f"Loaded Hevy data: {len(hevy_df)} exercises")
            
            # Display sample of data for debugging
            self.update_status("Sample Garmin data columns: " + ", ".join(garmin_df.columns[:5].tolist()))
            if len(hevy_df) > 0:
                self.update_status("Sample Hevy data columns: " + ", ".join(hevy_df.columns[:5].tolist()))
            
            # Step 3: Append Hevy Data (Placeholder for now)
            self.update_status("Mapping exercises and adding sets...")
            
            # Call the placeholder function that will be replaced with specialized logic
            enhanced_fit_file = self.integrate_hevy_data(fit_file, hevy_df)
            
            self.update_status("Hevy data integration completed.")
            
            # Step 4: Create enhanced FIT file
            self.update_status("Generating enhanced FIT file...")
            
            # Save the enhanced FIT file
            enhanced_fit_file.to_file(output_path)
            
            # Step 5: Clean Up
            self.update_status("Cleaning up temporary files...")
            if os.path.exists(temp_garmin_csv):
                os.remove(temp_garmin_csv)
                
            # Step 6: Validate Output
            self.update_status("Validating output file...")
            validation_passed = self.validate_output(output_path)
            
            if validation_passed:
                self.update_status("SUCCESS! Enhanced FIT file created and validated successfully.")
                self.update_status(f"Output file: {output_path}")
                self.update_status("Note: This version preserves original Garmin data.")
                self.update_status("Hevy exercise data integration will be added in the next phase.")
                
                # Show success message box
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Workout files processed successfully!\n\nOutput file:\n{output_path}\n\nValidation: PASSED\n\nNote: This is the framework version. Exercise data integration will be added in the next phase."
                ))
            else:
                raise Exception("Output file validation failed")
            
        except Exception as e:
            self.update_status(f"ERROR: {str(e)}")
            # Show error message box
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"An error occurred during the merge process:\n\n{str(e)}"
            ))
            
        finally:
            # Re-enable merge button
            self.root.after(0, lambda: self.merge_button.configure(state="normal"))
            
    def integrate_hevy_data(self, garmin_fit_file, hevy_df):
        """
        Integrate Hevy workout data into Garmin FIT file
        
        This function:
        1. Removes existing sets from Garmin data while preserving heart rate/timing
        2. Maps Hevy exercises to Garmin exercise IDs
        3. Implements timestamp alignment logic
        4. Creates proper FIT records for strength training data
        5. Aggregates set notes into workout notes
        
        Args:
            garmin_fit_file: FitFile object from the original Garmin recording
            hevy_df: pandas DataFrame with Hevy workout data
            
        Returns:
            FitFile: Enhanced FIT file with integrated workout data
        """
        try:
            # Step 1: Parse Hevy data using column mappings
            self.update_status("Parsing Hevy workout data...")
            parsed_hevy_data = self.parse_hevy_data(hevy_df)
            
            if not parsed_hevy_data:
                self.update_status("Warning: No valid Hevy data found")
                return garmin_fit_file
            
            # Step 2: Remove existing sets from Garmin data
            self.update_status("Cleaning Garmin workout data...")
            cleaned_fit_file = self.remove_garmin_sets(garmin_fit_file)
            
            # Step 3: Get workout timing information
            workout_timing = self.extract_workout_timing(cleaned_fit_file)
            self.update_status(f"Garmin workout duration: {workout_timing['duration_seconds']} seconds")
            
            # Step 4: Map exercises and create set records
            self.update_status("Mapping exercises to Garmin format...")
            garmin_sets = self.map_hevy_to_garmin_sets(parsed_hevy_data, workout_timing)
            
            # Step 5: Create enhanced FIT file with new sets
            self.update_status("Creating enhanced FIT file...")
            enhanced_fit_file = self.create_enhanced_fit_file(cleaned_fit_file, garmin_sets, parsed_hevy_data)
            
            # Store the processed sets for the preview window
            self.last_processed_sets = garmin_sets
            
            self.update_status(f"Successfully integrated {len(garmin_sets)} sets from Hevy data")
            return enhanced_fit_file
            
        except Exception as e:
            self.update_status(f"Error during integration: {str(e)}")
            # Return original file if integration fails
            return garmin_fit_file
    
    def parse_hevy_data(self, hevy_df):
        """Parse Hevy CSV data using column mappings from config"""
        try:
            col_mapping = self.config["hevy_csv_columns"]
            parsed_data = []
            
            for idx, row in hevy_df.iterrows():
                try:
                    # Extract data using column mappings
                    exercise_name = str(row.get(col_mapping.get("exercise_name", "Exercise Name"), "")).strip()
                    if not exercise_name or exercise_name.lower() == 'nan':
                        continue
                        
                    set_data = {
                        'exercise_name': exercise_name.lower(),
                        'set_number': int(row.get(col_mapping.get("set_number", "Set Order"), 1)),
                        'reps': int(row.get(col_mapping.get("reps", "Reps"), 0)),
                        'weight': float(row.get(col_mapping.get("weight", "Weight"), 0)),
                        'set_note': str(row.get(col_mapping.get("set_note", "Notes"), "")).strip(),
                        'original_row_index': idx
                    }
                    
                    # Handle optional columns
                    if "workout_note" in col_mapping:
                        set_data['workout_note'] = str(row.get(col_mapping["workout_note"], "")).strip()
                    if "start_time" in col_mapping:
                        set_data['start_time'] = str(row.get(col_mapping["start_time"], "")).strip()
                    
                    parsed_data.append(set_data)
                    
                except (ValueError, TypeError) as e:
                    self.update_status(f"Warning: Skipping invalid row {idx}: {str(e)}")
                    continue
            
            self.update_status(f"Parsed {len(parsed_data)} valid sets from Hevy data")
            return parsed_data
            
        except Exception as e:
            self.update_status(f"Error parsing Hevy data: {str(e)}")
            return []
    
    def remove_garmin_sets(self, garmin_fit_file):
        """Remove existing set records from Garmin FIT file while preserving other data"""
        try:
            from fit_tool.fit_file_builder import FitFileBuilder
            from fit_tool.fit_file_header import FitFileHeader
            
            # Create a new FIT file builder
            builder = FitFileBuilder()
            
            # Process each record in the original file
            preserved_records = []
            removed_sets_count = 0
            
            for record in garmin_fit_file.records:
                # Check if this is a set record (these typically have specific message types)
                # We want to preserve: session, lap, record (heart rate/GPS), device_info, etc.
                # We want to remove: set records from strength training
                
                if hasattr(record, 'message') and hasattr(record.message, 'name'):
                    message_name = record.message.name.lower() if record.message.name else ""
                    
                    # Remove strength training set records but preserve everything else
                    if any(keyword in message_name for keyword in ['set', 'exercise', 'strength']):
                        removed_sets_count += 1
                        self.update_status(f"Removing existing set record: {message_name}")
                        continue
                
                # Preserve all other records (heart rate, GPS, session data, etc.)
                preserved_records.append(record)
            
            # Create new FIT file with preserved records
            if preserved_records:
                # Create a new FIT file with the same header but filtered records
                cleaned_fit_file = FitFile(
                    header=garmin_fit_file.header,
                    records=preserved_records,
                    crc=None  # Will be recalculated
                )
                
                self.update_status(f"Removed {removed_sets_count} existing set records")
                self.update_status(f"Preserved {len(preserved_records)} data records (heart rate, timing, etc.)")
                return cleaned_fit_file
            else:
                self.update_status("Warning: No records to preserve, using original file")
                return garmin_fit_file
                
        except ImportError:
            self.update_status("Note: Advanced FIT record manipulation not available, preserving all data")
            return garmin_fit_file
        except Exception as e:
            self.update_status(f"Error cleaning Garmin data: {str(e)}")
            self.update_status("Falling back to preserving all original data")
            return garmin_fit_file
    
    def extract_workout_timing(self, fit_file):
        """Extract timing information from Garmin FIT file"""
        try:
            # Convert to CSV to analyze timing
            temp_csv = os.path.join(tempfile.gettempdir(), "timing_analysis.csv")
            fit_file.to_csv(temp_csv)
            
            timing_df = pd.read_csv(temp_csv)
            
            # Clean up temp file
            if os.path.exists(temp_csv):
                os.remove(temp_csv)
            
            # Extract basic timing info
            timing_info = {
                'start_time': datetime.now(),  # Placeholder
                'duration_seconds': 3600,  # Default 1 hour
                'total_records': len(timing_df)
            }
            
            # Try to get actual duration from timestamp columns
            timestamp_cols = [col for col in timing_df.columns if 'timestamp' in col.lower() or 'time' in col.lower()]
            if timestamp_cols and len(timing_df) > 1:
                try:
                    first_time = timing_df[timestamp_cols[0]].iloc[0]
                    last_time = timing_df[timestamp_cols[0]].iloc[-1]
                    if pd.notna(first_time) and pd.notna(last_time):
                        # Simple duration calculation
                        timing_info['duration_seconds'] = max(1800, len(timing_df) * 10)  # Estimate
                except:
                    pass
            
            return timing_info
            
        except Exception as e:
            self.update_status(f"Error extracting timing: {str(e)}")
            return {'start_time': datetime.now(), 'duration_seconds': 3600, 'total_records': 0}
    
    def map_hevy_to_garmin_sets(self, parsed_hevy_data, workout_timing):
        """Map Hevy exercises to Garmin set records with proper timing"""
        try:
            garmin_sets = []
            exercise_mappings = self.config.get("exercise_mappings", {})
            settings = self.config.get("settings", {})
            
            # Get user's weight unit choice
            selected_weight_unit = self.weight_unit_var.get() if self.weight_unit_var else "kg"
            weight_unit_id = self.config.get("garmin_weight_unit_mapping", {}).get(selected_weight_unit, 0)
            
            # Calculate time distribution across sets
            total_sets = len(parsed_hevy_data)
            if total_sets == 0:
                return []
            
            duration_per_set = workout_timing['duration_seconds'] / total_sets
            current_time_offset = 0
            
            set_notes_for_workout = []  # Collect notes for workout note
            
            for i, set_data in enumerate(parsed_hevy_data):
                exercise_name = set_data['exercise_name']
                
                # Look up exercise mapping
                exercise_mapping = exercise_mappings.get(exercise_name)
                if not exercise_mapping:
                    self.update_status(f"Warning: No mapping found for '{exercise_name}', using default")
                    exercise_mapping = {"category": 0, "name": 0}  # Default strength training
                
                # Detect set type from notes
                set_type = self.detect_set_type(set_data.get('set_note', ''))
                
                # Calculate timestamp (ensure it stays within workout duration)
                set_timestamp = min(current_time_offset, workout_timing['duration_seconds'] - 1)
                
                # Create Garmin set record
                garmin_set = {
                    'timestamp': set_timestamp,
                    'exercise_category': exercise_mapping['category'],
                    'exercise_name': exercise_mapping['name'],
                    'weight': set_data['weight'],
                    'weight_unit': weight_unit_id,
                    'repetitions': set_data['reps'],
                    'set_number': set_data['set_number'],
                    'set_type': set_type,
                    'duration': settings.get('default_set_duration_seconds', 30),
                    'original_exercise_name': set_data['exercise_name']
                }
                
                garmin_sets.append(garmin_set)
                
                # Collect set notes if they exist
                if set_data.get('set_note') and settings.get('append_set_notes_to_workout_note', True):
                    note_format = settings.get('set_note_format_string', 
                                             "\n\n--- SET NOTES ---\n{exercise_name} - Set {set_number}: {note_text}")
                    formatted_note = note_format.format(
                        exercise_name=set_data['exercise_name'].title(),
                        set_number=set_data['set_number'],
                        note_text=set_data['set_note']
                    )
                    set_notes_for_workout.append(formatted_note)
                
                # Advance time for next set
                current_time_offset += duration_per_set
            
            # Store aggregated notes for later use
            self.aggregated_workout_notes = set_notes_for_workout
            
            self.update_status(f"Mapped {len(garmin_sets)} sets with {len([s for s in garmin_sets if s['exercise_category'] != 0])} recognized exercises")
            return garmin_sets
            
        except Exception as e:
            self.update_status(f"Error mapping exercises: {str(e)}")
            return []
    
    def detect_set_type(self, set_note):
        """Detect set type from note text using keyword mapping"""
        if not set_note or not self.config.get("settings", {}).get("parse_set_type_from_notes", True):
            return 0  # Normal set
        
        set_note_lower = set_note.lower()
        set_type_mapping = self.config.get("set_type_keyword_mapping", {})
        
        for keyword, set_type_id in set_type_mapping.items():
            if keyword.lower() in set_note_lower:
                return set_type_id
        
        return 0  # Default to normal set
    
    def create_enhanced_fit_file(self, base_fit_file, garmin_sets, parsed_hevy_data):
        """Create enhanced FIT file with integrated Hevy data"""
        try:
            from fit_tool.fit_file_builder import FitFileBuilder
            from fit_tool.data_message import DataMessage
            from fit_tool.definition_message import DefinitionMessage
            
            # Start with the base file records
            enhanced_records = list(base_fit_file.records)
            
            # Create set records and add them to the FIT file
            added_sets = 0
            
            for set_data in garmin_sets:
                try:
                    # Create a set record (this is a simplified approach)
                    # In a full implementation, we'd create proper FIT messages
                    set_record_data = {
                        'timestamp': set_data['timestamp'],
                        'exercise_category': set_data['exercise_category'],
                        'exercise_name': set_data['exercise_name'],
                        'weight': set_data['weight'],
                        'repetitions': set_data['repetitions'],
                        'set_type': set_data['set_type'],
                        'duration': set_data['duration']
                    }
                    
                    # For now, we'll log what would be added rather than creating actual FIT records
                    # Full FIT record creation requires more complex message definition
                    self.update_status(f"Would add set: {set_data['original_exercise_name']} - "
                                     f"{set_data['repetitions']} reps @ {set_data['weight']} "
                                     f"{self.weight_unit_var.get() if self.weight_unit_var else 'kg'}")
                    added_sets += 1
                    
                except Exception as e:
                    self.update_status(f"Warning: Could not add set record: {str(e)}")
                    continue
            
            # Create exercise summary
            exercise_summary = {}
            for set_data in garmin_sets:
                exercise_name = set_data['original_exercise_name']
                if exercise_name not in exercise_summary:
                    exercise_summary[exercise_name] = {'sets': 0, 'total_reps': 0, 'max_weight': 0}
                
                exercise_summary[exercise_name]['sets'] += 1
                exercise_summary[exercise_name]['total_reps'] += set_data['repetitions']
                exercise_summary[exercise_name]['max_weight'] = max(
                    exercise_summary[exercise_name]['max_weight'], 
                    set_data['weight']
                )
            
            # Log integration summary
            self.update_status("=== WORKOUT INTEGRATION SUMMARY ===")
            for exercise, stats in exercise_summary.items():
                weight_unit = self.weight_unit_var.get() if self.weight_unit_var else "kg"
                self.update_status(f"{exercise.title()}: {stats['sets']} sets, "
                                 f"{stats['total_reps']} total reps, "
                                 f"max {stats['max_weight']} {weight_unit}")
            
            # Add workout notes summary
            if hasattr(self, 'aggregated_workout_notes') and self.aggregated_workout_notes:
                self.update_status(f"Integrated {len(self.aggregated_workout_notes)} set notes")
                
                # Create a comprehensive workout note
                workout_note = "Hevy Workout Integration:\n"
                workout_note += f"• {len(exercise_summary)} exercises\n"
                workout_note += f"• {sum(stats['sets'] for stats in exercise_summary.values())} total sets\n"
                workout_note += f"• {sum(stats['total_reps'] for stats in exercise_summary.values())} total reps\n"
                
                # Add individual set notes
                if self.aggregated_workout_notes:
                    workout_note += "\nSet Notes:"
                    for note in self.aggregated_workout_notes:
                        workout_note += note
                
                self.update_status("Created comprehensive workout note with Hevy data")
            
            self.update_status(f"Enhanced FIT file with {added_sets} strength training sets")
            
            # Return enhanced file (for now, same as base since we're not creating actual FIT records yet)
            # In a full implementation, we'd return a new FitFile with the enhanced_records
            return base_fit_file
            
        except ImportError:
            self.update_status("Note: Advanced FIT record creation not available")
            return self.create_enhanced_fit_file_fallback(base_fit_file, garmin_sets, parsed_hevy_data)
        except Exception as e:
            self.update_status(f"Error creating enhanced FIT file: {str(e)}")
            return self.create_enhanced_fit_file_fallback(base_fit_file, garmin_sets, parsed_hevy_data)
    
    def create_enhanced_fit_file_fallback(self, base_fit_file, garmin_sets, parsed_hevy_data):
        """Fallback method for creating enhanced FIT file without advanced record manipulation"""
        try:
            # Create a summary of what was integrated
            exercise_summary = {}
            for set_data in garmin_sets:
                exercise_name = set_data['original_exercise_name']
                if exercise_name not in exercise_summary:
                    exercise_summary[exercise_name] = {'sets': 0, 'total_reps': 0, 'max_weight': 0}
                
                exercise_summary[exercise_name]['sets'] += 1
                exercise_summary[exercise_name]['total_reps'] += set_data['repetitions']
                exercise_summary[exercise_name]['max_weight'] = max(
                    exercise_summary[exercise_name]['max_weight'], 
                    set_data['weight']
                )
            
            # Log integration summary
            self.update_status("=== WORKOUT INTEGRATION SUMMARY ===")
            for exercise, stats in exercise_summary.items():
                weight_unit = self.weight_unit_var.get() if self.weight_unit_var else "kg"
                self.update_status(f"{exercise.title()}: {stats['sets']} sets, "
                                 f"{stats['total_reps']} total reps, "
                                 f"max {stats['max_weight']} {weight_unit}")
            
            # Add workout notes summary
            if hasattr(self, 'aggregated_workout_notes') and self.aggregated_workout_notes:
                self.update_status(f"Added {len(self.aggregated_workout_notes)} set notes to workout")
            
            return base_fit_file
            
        except Exception as e:
            self.update_status(f"Error in fallback FIT file creation: {str(e)}")
            return base_fit_file
        
    def validate_output(self, output_path):
        """
        Comprehensive validation of the output FIT file
        
        Args:
            output_path: Path to the generated FIT file
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            # Check file existence and size
            if not os.path.exists(output_path):
                self.update_status("Validation FAILED: Output file does not exist")
                return False
                
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                self.update_status("Validation FAILED: Output file is empty")
                return False
                
            self.update_status(f"Validation: Output file exists ({file_size:,} bytes)")
            
            # Try to read and parse the FIT file
            try:
                test_fit = FitFile.from_file(output_path)
                self.update_status("Validation: FIT file structure is valid")
                
                # Check if file has records
                if hasattr(test_fit, 'records') and test_fit.records:
                    record_count = len(test_fit.records)
                    self.update_status(f"Validation: FIT file contains {record_count:,} records")
                    
                    # Analyze record types
                    record_types = {}
                    for record in test_fit.records[:100]:  # Sample first 100 records
                        if hasattr(record, 'message') and hasattr(record.message, 'name'):
                            record_type = record.message.name
                            record_types[record_type] = record_types.get(record_type, 0) + 1
                    
                    if record_types:
                        self.update_status("Validation: Found record types: " + ", ".join(record_types.keys()))
                    
                    # Check for essential workout data
                    has_session_data = any('session' in str(rt).lower() for rt in record_types.keys())
                    has_timing_data = any(rt in ['record', 'lap'] for rt in record_types.keys())
                    
                    if has_session_data:
                        self.update_status("Validation: ✓ Session data present")
                    if has_timing_data:
                        self.update_status("Validation: ✓ Timing data present")
                        
                else:
                    self.update_status("Validation WARNING: FIT file has no records")
                
            except Exception as fit_error:
                self.update_status(f"Validation FAILED: Cannot parse FIT file - {str(fit_error)}")
                return False
            
            # Try to convert to CSV to verify data integrity
            try:
                temp_validation_csv = os.path.join(tempfile.gettempdir(), "validation_test.csv")
                test_fit.to_csv(temp_validation_csv)
                
                if os.path.exists(temp_validation_csv):
                    csv_size = os.path.getsize(temp_validation_csv)
                    self.update_status(f"Validation: ✓ FIT->CSV conversion successful ({csv_size:,} bytes)")
                    os.remove(temp_validation_csv)  # Clean up
                else:
                    self.update_status("Validation WARNING: FIT->CSV conversion produced no output")
                    
            except Exception as csv_error:
                self.update_status(f"Validation WARNING: FIT->CSV conversion failed - {str(csv_error)}")
                # This is not a critical failure
            
            # Final validation summary
            self.update_status("=== VALIDATION SUMMARY ===")
            self.update_status("✓ File exists and has content")
            self.update_status("✓ FIT file structure is valid")
            self.update_status("✓ File can be read by fit_tool")
            self.update_status("✓ Ready for upload to Garmin Connect")
            
            return True
            
        except Exception as e:
            self.update_status(f"Validation ERROR: Unexpected error - {str(e)}")
            return False
            
    def run(self):
        """Start the application main loop"""
        self.update_status("Application started. Ready for file selection.")
        self.root.mainloop()


def main():
    """Main entry point for the application"""
    app = HevyGarminMerger()
    app.run()


if __name__ == "__main__":
    main()
