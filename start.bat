@echo off
echo Initializing LUKA MP3 v2...
cd /d "%~dp0"

:: Ensure yt-dlp is up to date for YouTube's latest changes
echo Checking for updates...
py -m pip install -q -U yt-dlp

:: Start the python backend in a separate command window
start "LUKA MP3 Server" py app.py

:: Wait a couple of seconds for the server to start
timeout /t 2 /nobreak >nul

:: Open the app in the user's currently opened browser
tasklist /FI "IMAGENAME eq chrome.exe" 2>NUL | find /I /N "chrome.exe">NUL
if "%ERRORLEVEL%"=="0" (
    start chrome http://127.0.0.1:5000/
    goto done
)

tasklist /FI "IMAGENAME eq msedge.exe" 2>NUL | find /I /N "msedge.exe">NUL
if "%ERRORLEVEL%"=="0" (
    start msedge http://127.0.0.1:5000/
    goto done
)

tasklist /FI "IMAGENAME eq firefox.exe" 2>NUL | find /I /N "firefox.exe">NUL
if "%ERRORLEVEL%"=="0" (
    start firefox http://127.0.0.1:5000/
    goto done
)

tasklist /FI "IMAGENAME eq brave.exe" 2>NUL | find /I /N "brave.exe">NUL
if "%ERRORLEVEL%"=="0" (
    start brave http://127.0.0.1:5000/
    goto done
)

:: Fallback to the default web browser
start http://127.0.0.1:5000/

:done
echo LUKA MP3 started! Enjoy your music.
exit
