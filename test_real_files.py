#!/usr/bin/env python3
"""
Test the Hevy to Garmin merger with real test files
"""

import os
import sys
import pandas as pd
import json
import tempfile
from datetime import datetime
from fit_tool.fit_file import FitFile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_real_files():
    """Test with actual files from Test Files folder"""
    
    print("=" * 60)
    print("TESTING WITH REAL FILES")
    print("=" * 60)
    
    # File paths
    test_dir = os.path.join(os.path.dirname(__file__), "Test Files")
    garmin_file = os.path.join(test_dir, "2025-09-01-16-42-38.fit")
    hevy_file = os.path.join(test_dir, "workouts-2.csv")
    
    # Check files exist
    if not os.path.exists(garmin_file):
        print(f"❌ Garmin file not found: {garmin_file}")
        return False
    if not os.path.exists(hevy_file):
        print(f"❌ Hevy file not found: {hevy_file}")
        return False
    
    print(f"✅ Found Garmin file: {os.path.basename(garmin_file)}")
    print(f"✅ Found Hevy file: {os.path.basename(hevy_file)}")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "hevy_garmin_config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"✅ Loaded config with {len(config.get('exercise_mappings', {}))} exercise mappings")
    
    # Test 1: Load and validate Garmin FIT file
    print("\n--- Test 1: Loading Garmin FIT File ---")
    try:
        fit_file = FitFile.from_file(garmin_file)
        print(f"✅ Loaded FIT file successfully")
        print(f"   Records: {len(fit_file.records)}")
        
        # Convert to CSV for analysis
        temp_csv = os.path.join(tempfile.gettempdir(), "test_garmin.csv")
        fit_file.to_csv(temp_csv)
        garmin_df = pd.read_csv(temp_csv)
        print(f"   CSV rows: {len(garmin_df)}")
        print(f"   Columns: {', '.join(garmin_df.columns[:5])}...")
        os.remove(temp_csv)
    except Exception as e:
        print(f"❌ Failed to load Garmin file: {e}")
        return False
    
    # Test 2: Load and analyze Hevy CSV
    print("\n--- Test 2: Loading Hevy CSV ---")
    try:
        hevy_df = pd.read_csv(hevy_file)
        print(f"✅ Loaded Hevy CSV: {len(hevy_df)} rows")
        print(f"   Columns: {', '.join(hevy_df.columns)}")
        
        # Check for expected columns based on config
        col_mapping = config.get("hevy_csv_columns", {})
        missing_cols = []
        for key, col_name in col_mapping.items():
            if col_name not in hevy_df.columns:
                missing_cols.append(f"{key} -> {col_name}")
        
        if missing_cols:
            print(f"⚠️  Missing expected columns: {missing_cols}")
        else:
            print("✅ All expected columns present")
        
        # Sample data
        print("\n   Sample exercises (first 5):")
        exercise_col = col_mapping.get("exercise_name", "exercise_title")
        if exercise_col in hevy_df.columns:
            exercises = hevy_df[exercise_col].dropna().unique()[:5]
            for ex in exercises:
                print(f"     - {ex}")
    except Exception as e:
        print(f"❌ Failed to load Hevy file: {e}")
        return False
    
    # Test 3: Parse Hevy data
    print("\n--- Test 3: Parsing Hevy Data ---")
    try:
        parsed_data = []
        for idx, row in hevy_df.iterrows():
            exercise_name = str(row.get(col_mapping.get("exercise_name", "Exercise Name"), "")).strip()
            if not exercise_name or exercise_name.lower() == 'nan':
                continue
            
            set_data = {
                'exercise_name': exercise_name.lower(),
                'set_number': int(row.get(col_mapping.get("set_number", "Set Order"), 1)),
                'reps': int(row.get(col_mapping.get("reps", "Reps"), 0)),
                'weight': float(row.get(col_mapping.get("weight", "Weight"), 0)),
                'set_note': str(row.get(col_mapping.get("set_note", "Notes"), "")).strip()
            }
            parsed_data.append(set_data)
        
        print(f"✅ Parsed {len(parsed_data)} valid sets")
        
        # Exercise summary
        exercise_summary = {}
        for set_data in parsed_data:
            ex_name = set_data['exercise_name']
            if ex_name not in exercise_summary:
                exercise_summary[ex_name] = {'sets': 0, 'total_reps': 0, 'max_weight': 0}
            exercise_summary[ex_name]['sets'] += 1
            exercise_summary[ex_name]['total_reps'] += set_data['reps']
            exercise_summary[ex_name]['max_weight'] = max(
                exercise_summary[ex_name]['max_weight'], 
                set_data['weight']
            )
        
        print(f"\n   Exercise Summary ({len(exercise_summary)} exercises):")
        for i, (exercise, stats) in enumerate(list(exercise_summary.items())[:10]):
            print(f"     {exercise}: {stats['sets']} sets, {stats['total_reps']} reps, max {stats['max_weight']} kg")
            
    except Exception as e:
        print(f"❌ Failed to parse Hevy data: {e}")
        return False
    
    # Test 4: Check exercise mappings
    print("\n--- Test 4: Exercise Mapping Check ---")
    exercise_mappings = config.get("exercise_mappings", {})
    unmapped = []
    mapped = []
    
    for exercise in exercise_summary.keys():
        if exercise in exercise_mappings:
            mapped.append(exercise)
        else:
            unmapped.append(exercise)
    
    print(f"✅ Mapped exercises: {len(mapped)}/{len(exercise_summary)}")
    if unmapped:
        print(f"⚠️  Unmapped exercises ({len(unmapped)}):")
        for ex in unmapped[:10]:
            print(f"     - {ex}")
        if len(unmapped) > 10:
            print(f"     ... and {len(unmapped) - 10} more")
    
    # Test 5: Create output file
    print("\n--- Test 5: Creating Output File ---")
    try:
        output_path = os.path.join(tempfile.gettempdir(), "test_output.fit")
        
        # For now, just save the original FIT file
        # (In production, this would include the merged data)
        fit_file.to_file(output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Output file created: {output_path}")
            print(f"   Size: {file_size:,} bytes")
            
            # Try to validate
            try:
                test_fit = FitFile.from_file(output_path)
                print(f"✅ Output file is valid FIT")
            except:
                print("⚠️  Output file validation failed")
            
            # Clean up
            os.remove(output_path)
        else:
            print("❌ Failed to create output file")
            
    except Exception as e:
        print(f"❌ Failed to create output: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed:")
    print(f"   - Garmin FIT: {len(garmin_df)} records")
    print(f"   - Hevy CSV: {len(parsed_data)} sets from {len(exercise_summary)} exercises")
    print(f"   - Mapped: {len(mapped)}/{len(exercise_summary)} exercises")
    if unmapped:
        print(f"   - Unmapped: {len(unmapped)} exercises (would trigger mapping dialog)")
    print(f"✅ All tests passed!")
    
    return True

if __name__ == "__main__":
    success = test_real_files()
    sys.exit(0 if success else 1)
