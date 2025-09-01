# 🏋️ Workout Preview & Editor Features

## Overview

The Hevy to Garmin FIT Merger now includes a comprehensive **Workout Preview & Editor** screen that appears after processing your files but before exporting the final FIT file. This gives you complete control over your workout data before uploading to Garmin Connect.

## New Workflow

### Updated Process
1. **Select Files**: Choose your Garmin .FIT and Hevy .CSV files
2. **Choose Weight Unit**: Select kg or lbs  
3. **Process**: Click "Process & Preview Workout"
4. **👀 PREVIEW & EDIT**: Review and modify your workout (NEW!)
5. **Export**: Save your enhanced FIT file
6. **Upload**: Add to Garmin Connect

## Preview Screen Features

### 📊 Workout Statistics Panel (Left Side)
Displays comprehensive workout statistics similar to Garmin Connect:

#### ⏱️ Timing
- **Total Time**: Complete workout duration
- **Work Time**: Active exercise time  
- **Rest Time**: Recovery periods

#### ❤️ Heart Rate
- **Avg HR**: Average heart rate throughout workout
- **Max HR**: Peak heart rate achieved
- *(Preserved from original Garmin data)*

#### 📋 Workout Details  
- **Total Reps**: Sum of all repetitions
- **Total Sets**: Number of exercise sets
- **Exercise Count**: Number of different exercises

#### 🔥 Energy
- **Calories**: Energy expenditure
- *(Calculated from original Garmin data)*

### 🏋️ Exercise List Panel (Right Side)
Interactive table showing all workout sets with editing capabilities:

#### Columns Displayed
- **Exercise**: Name of the exercise
- **Set**: Set number within the exercise
- **Reps**: Number of repetitions
- **Weight**: Weight used (with unit)
- **Type**: Set type (Normal, Warm-up, Failure, Drop set)

#### Editing Features
- **Select & Edit**: Click any set and use "Edit Selected" button
- **Real-time Updates**: Changes appear immediately in the table
- **Validation**: Input validation for reps and weight values
- **Set Type Selection**: Dropdown for set type modification

### ✏️ Set Editor Dialog
When editing a specific set:

#### Editable Fields
- **Reps**: Number of repetitions (integer)
- **Weight**: Weight used (decimal, in selected unit)
- **Set Type**: Dropdown selection:
  - Normal (default)
  - Warm-up
  - Failure  
  - Drop set

#### Validation
- Automatic validation of numeric inputs
- Error messages for invalid data
- Changes only saved if validation passes

## Technical Implementation

### Data Flow
```
Garmin FIT + Hevy CSV 
    ↓
Process & Integrate
    ↓
Extract Statistics
    ↓
🏋️ PREVIEW WINDOW 🏋️
    ↓
User Review & Edit
    ↓
Apply Edits
    ↓
Export Final FIT File
```

### Features Implemented
- **Modal Preview Window**: 1200x800 pixel dedicated editing interface
- **Statistics Extraction**: Real heart rate and timing data from Garmin
- **Exercise Table**: Sortable, scrollable list of all sets
- **Live Editing**: Real-time updates with validation
- **Data Preservation**: All original Garmin data maintained
- **Error Handling**: Comprehensive error recovery
- **User Experience**: Clear instructions and feedback

## Usage Examples

### Example Preview Display
```
🏋️ Workout Preview & Editor
📊 10 Sets • 62 Total Reps • 3 Exercises

Workout Statistics:
⏱️ Timing: 28:39 total, 28:39 work time
❤️ Heart Rate: 110 avg, 143 max bpm  
📋 Details: 62 total reps, 10 total sets
🔥 Energy: 194 calories

Exercise Sets:
Exercise Name          Set  Reps  Weight     Type
Barbell Bench Press    1    10    175 lbs    Normal
Barbell Bench Press    2    8     185 lbs    Normal  
Barbell Bench Press    3    6     195 lbs    Normal
Barbell Squat         1    10    225 lbs    Warm-up
Barbell Squat         2    8     245 lbs    Normal
...
```

### Edit Capabilities
- **Modify Reps**: Change repetition counts
- **Adjust Weight**: Update weight values  
- **Change Set Type**: Mark sets as warm-up, failure, etc.
- **Real-time Preview**: See changes immediately
- **Bulk Validation**: All changes validated before export

## Benefits

### For Users
- **Full Control**: Review every detail before finalizing
- **Error Correction**: Fix any import errors or data issues
- **Workout Optimization**: Adjust data for accuracy
- **Confidence**: See exactly what will be uploaded to Garmin

### For Data Quality
- **Accuracy**: Catch and correct any mapping errors
- **Completeness**: Ensure all exercises are properly categorized
- **Consistency**: Verify weight units and set types
- **Validation**: Multiple validation layers before export

## Integration with Existing Features

### Preserved Functionality
- ✅ All original features still work
- ✅ Exercise mapping (200+ exercises)
- ✅ Weight unit selection
- ✅ Set type detection
- ✅ Notes aggregation
- ✅ Error handling

### Enhanced Workflow
- ✅ Preview before export
- ✅ Edit capabilities
- ✅ Statistics display
- ✅ User confirmation
- ✅ Final validation

## Next Steps

The preview and editing functionality is now **fully implemented** and ready for use. Users can:

1. **Process their workouts** with confidence
2. **Review all data** in a clear, organized format
3. **Make corrections** as needed
4. **Export with confidence** knowing exactly what will be uploaded

**The application now provides a complete, professional-grade workout data management experience!** 🎉
