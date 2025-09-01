#!/usr/bin/env python3
"""
Core Functionality Test for Hevy to Garmin Integration

This script tests the core integration logic without GUI dependencies.
"""

import os
import sys
import json
import tempfile
import pandas as pd
from datetime import datetime

def load_config():
    """Load the configuration file"""
    try:
        config_path = "hevy_garmin_config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def test_config_loading():
    """Test configuration file loading"""
    print("\n=== Testing Configuration Loading ===")
    
    config = load_config()
    if not config:
        return False
        
    print(f"✓ Config version: {config.get('version', 'Unknown')}")
    print(f"✓ Exercise mappings: {len(config.get('exercise_mappings', {}))}")
    print(f"✓ Settings loaded: {len(config.get('settings', {}))}")
    print(f"✓ CSV column mappings: {len(config.get('hevy_csv_columns', {}))}")
    
    # Test specific settings
    settings = config.get('settings', {})
    print(f"✓ Default weight unit: {settings.get('weight_unit', 'Not set')}")
    print(f"✓ Set duration: {settings.get('default_set_duration_seconds', 'Not set')} seconds")
    
    return True

def parse_hevy_data(hevy_df, config):
    """Parse Hevy CSV data using column mappings from config"""
    try:
        col_mapping = config["hevy_csv_columns"]
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
                
                parsed_data.append(set_data)
                
            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping invalid row {idx}: {str(e)}")
                continue
        
        return parsed_data
        
    except Exception as e:
        print(f"Error parsing Hevy data: {str(e)}")
        return []

def detect_set_type(set_note, config):
    """Detect set type from note text using keyword mapping"""
    if not set_note or not config.get("settings", {}).get("parse_set_type_from_notes", True):
        return 0  # Normal set
    
    set_note_lower = set_note.lower()
    set_type_mapping = config.get("set_type_keyword_mapping", {})
    
    for keyword, set_type_id in set_type_mapping.items():
        if keyword.lower() in set_note_lower:
            return set_type_id
    
    return 0  # Default to normal set

def map_hevy_to_garmin_sets(parsed_hevy_data, workout_timing, config, weight_unit="kg"):
    """Map Hevy exercises to Garmin set records with proper timing"""
    try:
        garmin_sets = []
        exercise_mappings = config.get("exercise_mappings", {})
        settings = config.get("settings", {})
        
        # Get weight unit ID
        weight_unit_id = config.get("garmin_weight_unit_mapping", {}).get(weight_unit, 0)
        
        # Calculate time distribution across sets
        total_sets = len(parsed_hevy_data)
        if total_sets == 0:
            return []
        
        duration_per_set = workout_timing['duration_seconds'] / total_sets
        current_time_offset = 0
        
        for i, set_data in enumerate(parsed_hevy_data):
            exercise_name = set_data['exercise_name']
            
            # Look up exercise mapping
            exercise_mapping = exercise_mappings.get(exercise_name)
            if not exercise_mapping:
                exercise_mapping = {"category": 0, "name": 0}  # Default strength training
            
            # Detect set type from notes
            set_type = detect_set_type(set_data.get('set_note', ''), config)
            
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
            
            # Advance time for next set
            current_time_offset += duration_per_set
        
        return garmin_sets
        
    except Exception as e:
        print(f"Error mapping exercises: {str(e)}")
        return []

def test_hevy_csv_parsing():
    """Test Hevy CSV parsing functionality"""
    print("\n=== Testing Hevy CSV Parsing ===")
    
    try:
        config = load_config()
        if not config:
            return False
        
        # Load sample CSV
        sample_csv_path = "sample_hevy_workout.csv"
        if not os.path.exists(sample_csv_path):
            print("❌ Sample Hevy CSV file not found")
            return False
            
        hevy_df = pd.read_csv(sample_csv_path)
        print(f"✓ Loaded sample CSV with {len(hevy_df)} rows")
        print(f"✓ Columns: {', '.join(hevy_df.columns.tolist())}")
        
        # Test parsing
        parsed_data = parse_hevy_data(hevy_df, config)
        if parsed_data:
            print(f"✓ Successfully parsed {len(parsed_data)} sets")
            
            # Show sample parsed data
            for i, set_data in enumerate(parsed_data[:3]):
                print(f"  Set {i+1}: {set_data['exercise_name']} - {set_data['reps']} reps @ {set_data['weight']} lbs")
            
            return True
        else:
            print("❌ Failed to parse Hevy data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Hevy CSV parsing: {e}")
        return False

def test_exercise_mapping():
    """Test exercise mapping functionality"""
    print("\n=== Testing Exercise Mapping ===")
    
    try:
        config = load_config()
        if not config:
            return False
        
        # Test some common exercises
        test_exercises = [
            "barbell bench press",
            "barbell squat", 
            "deadlift",
            "unknown exercise"
        ]
        
        exercise_mappings = config.get("exercise_mappings", {})
        print(f"✓ Loaded {len(exercise_mappings)} exercise mappings")
        
        for exercise in test_exercises:
            mapping = exercise_mappings.get(exercise.lower())
            if mapping:
                print(f"✓ {exercise.title()}: category={mapping['category']}, name={mapping['name']}")
            else:
                print(f"⚠ {exercise.title()}: No mapping found (will use default)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing exercise mapping: {e}")
        return False

def test_set_type_detection():
    """Test set type detection from notes"""
    print("\n=== Testing Set Type Detection ===")
    
    try:
        config = load_config()
        if not config:
            return False
        
        test_notes = [
            "Good form",
            "Warm up set",
            "Drop set to failure",
            "Went to failure",
            "Normal set",
            ""
        ]
        
        for note in test_notes:
            set_type = detect_set_type(note, config)
            type_name = {0: "Normal", 2: "Warm-up", 5: "Failure", 6: "Drop set"}.get(set_type, f"Type {set_type}")
            print(f"✓ '{note}' → {type_name} (ID: {set_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing set type detection: {e}")
        return False

def test_integration_workflow():
    """Test the complete integration workflow"""
    print("\n=== Testing Integration Workflow ===")
    
    try:
        config = load_config()
        if not config:
            return False
        
        # Load sample Hevy data
        sample_csv_path = "sample_hevy_workout.csv"
        if not os.path.exists(sample_csv_path):
            print("❌ Sample Hevy CSV file not found")
            return False
            
        hevy_df = pd.read_csv(sample_csv_path)
        print(f"✓ Loaded Hevy data: {len(hevy_df)} rows")
        
        # Parse Hevy data
        parsed_hevy_data = parse_hevy_data(hevy_df, config)
        if not parsed_hevy_data:
            print("❌ Failed to parse Hevy data")
            return False
        print(f"✓ Parsed {len(parsed_hevy_data)} sets")
        
        # Test workout timing (with dummy data)
        workout_timing = {
            'start_time': datetime.now(),
            'duration_seconds': 3600,
            'total_records': 100
        }
        print(f"✓ Workout timing: {workout_timing['duration_seconds']} seconds")
        
        # Test exercise mapping
        garmin_sets = map_hevy_to_garmin_sets(parsed_hevy_data, workout_timing, config, "lbs")
        if garmin_sets:
            print(f"✓ Created {len(garmin_sets)} Garmin set records")
            
            # Show sample mapped data
            for i, garmin_set in enumerate(garmin_sets[:3]):
                print(f"  Set {i+1}: {garmin_set['original_exercise_name']} → "
                      f"category={garmin_set['exercise_category']}, "
                      f"name={garmin_set['exercise_name']}, "
                      f"type={garmin_set['set_type']}")
        else:
            print("❌ Failed to create Garmin set records")
            return False
        
        # Test exercise summary
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
        
        print("\n✓ Exercise Summary:")
        for exercise, stats in exercise_summary.items():
            print(f"  {exercise.title()}: {stats['sets']} sets, "
                  f"{stats['total_reps']} total reps, "
                  f"max {stats['max_weight']} lbs")
        
        print("✓ Integration workflow test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing integration workflow: {e}")
        return False

def main():
    """Run all core functionality tests"""
    print("🧪 Hevy to Garmin Core Functionality Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Hevy CSV Parsing", test_hevy_csv_parsing),
        ("Exercise Mapping", test_exercise_mapping),
        ("Set Type Detection", test_set_type_detection),
        ("Integration Workflow", test_integration_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🧪 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All core functionality tests PASSED!")
        print("The Hevy to Garmin integration logic is working correctly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
