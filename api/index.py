"""
Vercel serverless function entry point in api/ directory
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment
os.environ['FLASK_ENV'] = 'production'

# Import the Flask app
from app import app, db, User, Program, Club, Team, Division
from werkzeug.security import generate_password_hash
from datetime import date

# Initialize database on cold start (production-safe)
def initialize_database():
    """Initialize database with tables and sample data"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Create divisions
            print("Creating divisions...")
            south_division = Division.query.filter_by(name='Southern Ontario Division').first()
            if not south_division:
                south_division = Division(name='Southern Ontario Division', description='Southern Ontario Division')
                db.session.add(south_division)
            
            north_division = Division.query.filter_by(name='Northern Ontario Division').first()
            if not north_division:
                north_division = Division(name='Northern Ontario Division', description='Northern Ontario Division')
                db.session.add(north_division)
            
            db.session.flush()
            
            # Create Alpine Ontario club
            print("Creating clubs...")
            aoa_club = Club.query.filter_by(name='Alpine Ontario').first()
            if not aoa_club:
                aoa_club = Club(name='Alpine Ontario', description='Provincial sport organization')
                db.session.add(aoa_club)
                db.session.flush()
            
            # Always create users (for production database, only create if they don't exist)
            print("Creating users...")
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin123', method='pbkdf2:sha256'),
                    user_type='admin',
                    full_name='System Administrator',
                    club_id=aoa_club.id if aoa_club else None
                )
                db.session.add(admin_user)
            
            coach_user = User.query.filter_by(username='coach1').first()
            if not coach_user:
                coach_user = User(
                    username='coach1',
                    email='coach@example.com',
                    password_hash=generate_password_hash('coach123', method='pbkdf2:sha256'),
                    user_type='coach',
                    full_name='Coach Johnson'
                )
                db.session.add(coach_user)
                db.session.flush()
            
            # Create programs
            print("Creating programs...")
            programs_data = [
                ('U12', 'Under 12 racing program', 'weekly', 8, 'saturday'),
                ('U14', 'Under 14 racing program', 'weekly', 8, 'saturday'),
                ('U16', 'Under 16 racing program', 'daily', 8, None),
                ('U18/U21', 'Under 18/21 racing program', 'daily', 10, None)
            ]
            
            for program_name, description, freq_type, freq_value, freq_days in programs_data:
                if not Program.query.filter_by(name=program_name).first():
                    program = Program(
                        name=program_name,
                        description=description,
                        frequency_type=freq_type,
                        frequency_value=freq_value,
                        frequency_days=freq_days
                    )
                    db.session.add(program)
            
            db.session.flush()
            
            # Create student if coach exists
            student_user = User.query.filter_by(username='athlete1').first()
            if not student_user and coach_user:
                u12_program = Program.query.filter_by(name='U12').first()
                if u12_program:
                    demo_team = Team.query.filter_by(name='U12 Demo Team').first()
                    if not demo_team:
                        demo_team = Team(
                            name='U12 Demo Team',
                            program_id=u12_program.id,
                            coach_id=coach_user.id,
                            team_type='team',
                            club_id=aoa_club.id if aoa_club else None
                        )
                        db.session.add(demo_team)
                        db.session.flush()
                    
                    south_division = Division.query.filter_by(name='Southern Ontario Division').first()
                    student_user = User(
                        username='athlete1',
                        email='athlete@example.com',
                        password_hash=generate_password_hash('athlete123', method='pbkdf2:sha256'),
                        user_type='student',
                        full_name='John Doe',
                        participates_snow_stars=True,
                        coach_id=coach_user.id,
                        team_id=demo_team.id if demo_team else None,
                        program_id=u12_program.id,
                        division_id=south_division.id if south_division else None,
                        club_id=aoa_club.id if aoa_club else None
                    )
                    db.session.add(student_user)
            
            db.session.commit()
            print("✓ Users, clubs, and programs created")
            print("✓ Database initialization complete")
            return True
            
    except Exception as e:
        import traceback
        print(f"Database initialization error: {e}")
        print(traceback.format_exc())
        return False

# Initialize database
initialize_database()

# Export the app for Vercel (@vercel/python handler expects 'app')
__all__ = ['app']
