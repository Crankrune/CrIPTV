@echo off
SETLOCAL

ECHO ======================================
ECHO  Synchronizing Local Repository
ECHO ======================================

REM --- Step 1: Check for uncommitted changes before pulling ---
ECHO.
ECHO Checking for local changes...
git diff --quiet || (
    ECHO.
    ECHO WARNING: You have uncommitted local changes.
    ECHO Please commit or stash your changes before pulling.
    ECHO   - To commit: git commit -am "Your message"
    ECHO   - To stash: git stash save "Your message"
    ECHO.
    PAUSE
    EXIT /B 1
)

ECHO No uncommitted changes detected. Proceeding with pull.

REM --- Step 2: Pull the latest changes from the remote ---
ECHO.
ECHO Pulling latest changes from origin/main...
git pull origin main
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO ERROR: Git pull failed. Please resolve any issues.
    PAUSE
    EXIT /B 1
)
ECHO Local repository is now up-to-date.

REM --- Step 3: Run main.py to update local generated files ---
ECHO.
ECHO Running main.py to update local generated playlists (without committing)...
python main.py
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO ERROR: main.py execution failed.
    PAUSE
    EXIT /B 1
)
ECHO main.py executed successfully.

REM --- Step 4: Show status for locally generated files ---
ECHO.
ECHO Local file status after running main.py:
git status --porcelain output/playlists/ output/youtube_epg.xml
ECHO (Note: The GitHub Actions workflow handles committing these generated files.)

ECHO.
ECHO Synchronization complete.
PAUSE
ENDLOCAL
EXIT /B 0