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

## Status
Project setup in progress.
