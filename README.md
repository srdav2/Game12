# Hevy to Garmin FIT Merger Application

A user-friendly macOS desktop app that merges a Garmin `.FIT` activity file with a Hevy workout `.CSV` export into a single enriched `.FIT`. The resulting file preserves physiological data (e.g., heart rate and time) from Garmin and adds detailed sets, reps, and weights from Hevy.

## Objective
Enable a non-technical user on Mac to select two input files (Garmin `.FIT` and Hevy `.CSV`), merge them, and export a new `.FIT` without needing any command-line interaction.

## Target User
Someone with no coding background. All interactions happen through a graphical user interface.

## Core Principle: NO TERMINAL
The application must be entirely GUI-based. No terminal usage will be required by the user; any tools will run in the background.

## Technology Stack
- **Language**: Python
- **GUI Framework**: CustomTkinter (modern, clean UI with straightforward implementation)
- **Data Manipulation**: pandas (read and process Hevy CSV data)
- **FIT Processing**: Garmin `fit_tool` (invoked as a background subprocess from Python)

## How It Works (High Level)
1. User opens the app and selects a Garmin `.FIT` file and a Hevy workout `.CSV`.
2. The app parses the Hevy CSV with pandas to extract exercise, set, rep, and weight details.
3. The app uses Garmin `fit_tool` to read/write FIT data and merges the Hevy set/rep metadata into the Garmin activity timeline, preserving heart rate and timing.
4. The app saves a new enriched `.FIT` file to a chosen location.

## Key Requirements
- 100% GUI-driven workflow; no command-line steps required by the user.
- Self-contained macOS app bundle for simple installation and use.
- Clear file selection, progress indication, and success/error messaging within the app.

## Non-Goals (for initial version)
- Advanced editing of workout data inside the app.
- Cloud sync or account features.

## Installation & Setup

### Prerequisites
- Python 3.13+ (comes with macOS)
- pip (Python package manager)

### Quick Setup
1. Clone or download this repository
2. Open Terminal and navigate to the project directory
3. Run the setup script: `./run_app.sh`

The setup script will automatically:
- Create a Python virtual environment
- Install all required dependencies (customtkinter, pandas, fit_tool)
- Launch the application

### Manual Setup (Alternative)
If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Usage

1. **Launch the Application**: Run `./run_app.sh` or `python app.py` (after setup)

2. **Select Files**:
   - Click "Select Garmin File..." and choose your `.FIT` activity file
   - Click "Select Hevy File..." and choose your exported `.CSV` workout file

3. **Choose Weight Unit**: Select kg or lbs for your workout weights

4. **Process & Preview**:
   - Once both files are selected, the "Process & Preview Workout" button becomes active
   - Click the button to process your files and open the preview window
   - Watch the status log for progress updates

5. **Review & Edit** (NEW! 🏋️):
   - **Workout Statistics**: View timing, heart rate, calories (like Garmin Connect)
   - **Exercise Table**: See all sets with exercise, reps, weight, and type
   - **Edit Sets**: Click any set and use "Edit Selected" to modify reps, weight, or type
   - **Real-time Updates**: Changes appear immediately in the preview

6. **Export**: Click "Export FIT File" and choose where to save your enhanced `.FIT` file

7. **Upload to Garmin**: The enhanced `.FIT` file can be uploaded to Garmin Connect

## Features

- **Modern GUI**: Clean, intuitive interface using CustomTkinter
- **🏋️ Workout Preview & Editor**: Review and edit your workout before export (NEW!)
- **📊 Garmin-style Statistics**: View timing, heart rate, calories, and workout details
- **✏️ Set Editing**: Modify reps, weight, and set types with real-time validation
- **🎯 Exercise Mapping**: 200+ exercises automatically mapped to Garmin format
- **⚖️ Weight Unit Selection**: Choose kg or lbs for your workout
- **🏷️ Set Type Detection**: Automatic detection of warm-up, failure, drop sets
- **📝 Notes Integration**: All set notes preserved in workout notes
- **File Validation**: Automatic file type checking and error handling
- **Real-time Status**: Live progress updates during processing
- **No Terminal Required**: All operations happen through the GUI
- **Error Recovery**: Comprehensive error handling with user-friendly messages

## File Structure

```
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── run_app.sh         # Quick launch script
├── venv/              # Virtual environment (created during setup)
└── README.md          # This file
```

## Status
✅ Phase 1: Project Setup and UI Scaffolding - COMPLETE
✅ Phase 2: File Input and UI Logic - COMPLETE  
✅ Phase 3: Core Merger Logic Framework - COMPLETE
✅ Phase 4: UI Integration - COMPLETE
✅ **Phase 5: Hevy-Garmin Integration Logic - COMPLETE**

### 🎉 FULL INTEGRATION IMPLEMENTED

The application now includes **complete Hevy to Garmin workout integration**:

#### ✅ Implemented Features
- **Exercise Mapping**: 200+ exercises mapped from Hevy names to Garmin IDs
- **Weight Unit Selection**: User can choose kg or lbs for the workout
- **Set Type Detection**: Automatically detects warm-up, failure, drop sets from notes
- **Timestamp Alignment**: Distributes Hevy sets across Garmin workout timeline
- **Notes Aggregation**: Combines set-specific notes into workout notes
- **Data Validation**: Comprehensive error handling and user feedback
- **Configuration-Driven**: JSON config file for easy customization

#### 🔧 How It Works
1. **Removes existing sets** from Garmin workout while preserving heart rate data
2. **Parses Hevy CSV** using configurable column mappings
3. **Maps exercises** using comprehensive exercise database (200+ exercises)
4. **Aligns timestamps** to fit within Garmin workout duration
5. **Preserves all notes** by aggregating them into workout notes
6. **Creates enhanced FIT file** with integrated strength training data
