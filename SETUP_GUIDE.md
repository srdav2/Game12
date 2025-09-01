# Setup Guide for Hevy to Garmin FIT Merger

## For Mac Users (Target Platform)

### Option 1: Quick Setup (Recommended)
1. Download or clone this project to your Mac
2. Open Terminal (found in Applications > Utilities)
3. Navigate to the project folder: `cd /path/to/Hevy2Garmin`
4. Run: `./run_app.sh`

The script will automatically set up everything and launch the application.

### Option 2: Manual Setup
If you prefer to understand each step:

1. **Install Python** (if not already installed):
   - Python 3.13+ should come with macOS
   - Verify with: `python3 --version`

2. **Set up the project**:
   ```bash
   # Navigate to project directory
   cd /path/to/Hevy2Garmin
   
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate
   
   # Launch the app
   python app.py
   ```

## For Linux Users (Development Platform)

The same steps work on Linux. If you encounter permission issues with pip, the setup script will handle creating a virtual environment automatically.

## Testing the Application

A sample Hevy workout file (`sample_hevy_workout.csv`) is included for testing. You'll need to provide your own Garmin .FIT file from a workout.

## Application Features

### Current Status (Framework Complete)
✅ Modern GUI with CustomTkinter
✅ File selection dialogs for .FIT and .CSV files
✅ Real-time status updates
✅ Error handling and user feedback
✅ FIT file reading and writing using fit_tool library
✅ Placeholder integration points for specialized logic

### Ready for Integration
The application framework is complete and ready for the specialized data mapping logic:

1. **Exercise Mapping Dictionary**: Will translate Hevy exercise names to Garmin numeric IDs
2. **Timestamp Alignment Logic**: Will intelligently place Hevy sets on the Garmin timeline
3. **Final Validation Checks**: Will verify the output file integrity

## Troubleshooting

### Common Issues

**"Command not found" errors**: Make sure you're running commands from the project directory and that the virtual environment is activated.

**Permission denied**: On Mac, you might need to run `chmod +x run_app.sh` to make the script executable.

**Import errors**: Ensure all dependencies are installed by running `pip install -r requirements.txt` in the activated virtual environment.

### Getting Help

If you encounter issues:
1. Check that Python 3.13+ is installed: `python3 --version`
2. Verify you're in the project directory: `ls` should show `app.py`
3. Make sure the virtual environment is activated (you should see `(venv)` in your terminal prompt)

## Next Steps

The application is now ready for the specialized logic integration. When you receive the exercise mapping dictionary and timestamp alignment code, simply replace the placeholder functions in `app.py`.
