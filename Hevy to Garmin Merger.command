#!/bin/bash
cd "/Users/stuartdavis/Documents/Hevy2Garmin"

echo "🏋️ Starting Hevy to Garmin FIT Merger..."
echo "Please wait while the application window opens..."

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "📦 Setting up application (first time only)..."
    /opt/homebrew/bin/python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Setup complete!"
else
    source venv/bin/activate
fi

# Launch the application
echo "🚀 Opening application window..."
python app.py

echo ""
echo "Application closed. You can close this window."
echo "Press any key to exit..."
read -n 1
