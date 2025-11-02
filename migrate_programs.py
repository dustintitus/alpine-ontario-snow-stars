#!/usr/bin/env python3
"""
Migration script to update programs from old structure to new racing age groups.
This script:
1. Identifies teams associated with old programs
2. Removes old programs (only if safe to do so)
3. Creates new programs (U12, U14, U16, U18/U21) if they don't exist
"""

import os
import sys
from flask import Flask
from models import db, Program, Team, Club

# Old program names to remove
OLD_PROGRAMS = [
    'Snowflakes',
    'High Flyers',
    'Trail Blazers',
    'LIT',
    'Adult',
    'Terrain Park'
]

# New programs to create
NEW_PROGRAMS = [
    ('U12', 'Under 12 racing program', 'weekly', 8, 'saturday'),
    ('U14', 'Under 14 racing program', 'weekly', 8, 'saturday'),
    ('U16', 'Under 16 racing program', 'daily', 8, None),
    ('U18/U21', 'Under 18/21 racing program', 'daily', 10, None)
]

def migrate_programs():
    """Migrate programs from old structure to new racing age groups"""
    app = Flask(__name__)
    
    # Load configuration
    env = os.environ.get('FLASK_ENV', 'development')
    from config import config
    app.config.from_object(config.get(env, config['development']))
    
    db.init_app(app)
    
    with app.app_context():
        print("=" * 60)
        print("Program Migration Script")
        print("=" * 60)
        print()
        
        # Step 1: Check for teams associated with old programs
        print("Step 1: Checking for teams associated with old programs...")
        teams_to_update = []
        
        for old_program_name in OLD_PROGRAMS:
            old_program = Program.query.filter_by(name=old_program_name).first()
            if old_program:
                teams = Team.query.filter_by(program_id=old_program.id).all()
                if teams:
                    print(f"  ⚠️  Found {len(teams)} team(s) associated with '{old_program_name}':")
                    for team in teams:
                        print(f"     - {team.name} (ID: {team.id})")
                        teams_to_update.append((team, old_program_name))
        
        if teams_to_update:
            print()
            print("⚠️  WARNING: There are teams associated with old programs!")
            print("   These teams need to be reassigned to new programs before migration.")
            print("   You can either:")
            print("   1. Reassign teams manually in the admin interface, or")
            print("   2. Delete these teams if they're no longer needed")
            print()
            response = input("Do you want to continue? This will fail if teams still exist. (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                return False
            
            # Double-check that teams were handled
            remaining_teams = []
            for old_program_name in OLD_PROGRAMS:
                old_program = Program.query.filter_by(name=old_program_name).first()
                if old_program:
                    teams = Team.query.filter_by(program_id=old_program.id).all()
                    remaining_teams.extend(teams)
            
            if remaining_teams:
                print(f"❌ ERROR: Still {len(remaining_teams)} team(s) associated with old programs!")
                print("   Please reassign or delete these teams first:")
                for team in remaining_teams:
                    print(f"   - {team.name} (ID: {team.id})")
                return False
        
        print("✓ No teams blocking migration")
        print()
        
        # Step 2: Remove old programs
        print("Step 2: Removing old programs...")
        removed_count = 0
        for old_program_name in OLD_PROGRAMS:
            old_program = Program.query.filter_by(name=old_program_name).first()
            if old_program:
                # Double-check no teams are associated
                teams = Team.query.filter_by(program_id=old_program.id).all()
                if teams:
                    print(f"  ⚠️  Skipping '{old_program_name}' - still has {len(teams)} team(s)")
                    continue
                
                print(f"  🗑️  Removing '{old_program_name}'...")
                db.session.delete(old_program)
                removed_count += 1
        
        if removed_count > 0:
            db.session.commit()
            print(f"✓ Removed {removed_count} old program(s)")
        else:
            print("✓ No old programs to remove (or they're still in use)")
        print()
        
        # Step 3: Create new programs
        print("Step 3: Creating new programs...")
        created_count = 0
        for program_name, description, freq_type, freq_value, freq_days in NEW_PROGRAMS:
            existing = Program.query.filter_by(name=program_name).first()
            if existing:
                print(f"  ✓ '{program_name}' already exists")
            else:
                print(f"  ➕ Creating '{program_name}'...")
                new_program = Program(
                    name=program_name,
                    description=description,
                    frequency_type=freq_type,
                    frequency_value=freq_value,
                    frequency_days=freq_days
                )
                db.session.add(new_program)
                created_count += 1
        
        if created_count > 0:
            db.session.commit()
            print(f"✓ Created {created_count} new program(s)")
        else:
            print("✓ All new programs already exist")
        print()
        
        # Step 4: Summary
        print("=" * 60)
        print("Migration Summary")
        print("=" * 60)
        all_programs = Program.query.all()
        print(f"Total programs in database: {len(all_programs)}")
        print("\nCurrent programs:")
        for program in sorted(all_programs, key=lambda p: p.name):
            teams_count = len(program.teams)
            print(f"  - {program.name}: {teams_count} team(s)")
        print()
        print("✅ Migration completed successfully!")
        print()
        
        return True

if __name__ == '__main__':
    try:
        success = migrate_programs()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

