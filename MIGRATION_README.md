# Program Migration Guide

This migration script updates the database from the old program structure (Snowflakes, High Flyers, etc.) to the new racing age group programs (U12, U14, U16, U18/U21).

## Prerequisites

1. Make sure you have a backup of your database before running the migration
2. Ensure all teams associated with old programs have been reassigned or deleted

## Running the Migration

### Local Development

1. Activate your virtual environment (if using one):
   ```bash
   source venv/bin/activate  # or your venv activation command
   ```

2. Run the migration script:
   ```bash
   python migrate_programs.py
   ```

3. Follow the prompts. The script will:
   - Check for teams associated with old programs
   - Warn you if teams need to be reassigned
   - Remove old programs (only if safe)
   - Create new programs (U12, U14, U16, U18/U21) if they don't exist

### Production (Vercel)

For Vercel deployments, the database is re-initialized on each cold start via `api/index.py`, so the new programs will be created automatically. However, if you have persistent data:

1. You can run the migration via a Flask route (if you add one temporarily), or
2. Manually delete old programs through the admin "Manage Programs" interface
3. The new programs will be created on the next database initialization

## What the Migration Does

1. **Checks for dependencies**: Identifies any teams still associated with old programs
2. **Removes old programs**: Deletes programs like "Snowflakes", "High Flyers", etc. (only if no teams are associated)
3. **Creates new programs**: Adds U12, U14, U16, and U18/U21 with appropriate settings

## Old Programs Being Removed

- Snowflakes
- High Flyers
- Trail Blazers
- LIT
- Adult
- Terrain Park

## New Programs Being Created

- **U12**: Under 12 racing program (weekly, 8 sessions, Saturday)
- **U14**: Under 14 racing program (weekly, 8 sessions, Saturday)
- **U16**: Under 16 racing program (daily, 8 sessions)
- **U18/U21**: Under 18/21 racing program (daily, 10 sessions)

## Troubleshooting

### Error: "Still X team(s) associated with old programs"

**Solution**: Go to the admin "Manage Teams" page and either:
- Reassign teams to new programs, or
- Delete teams that are no longer needed

### Error: Database connection issues

**Solution**: Check your `DATABASE_URL` environment variable and ensure the database is accessible.

### Migration completes but programs don't appear

**Solution**: Refresh your browser or check the database directly. The new programs should be visible in "Manage Programs".

