@echo off
title PILL RED Command Center
echo ======================================================================
echo                  PILL RED COMMAND CENTER INTERFACE
echo                           PILLRED-SPEC-1.0
echo ======================================================================
echo.
echo Starting local Command Center server at http://127.0.0.1:8080 ...
start "" "http://127.0.0.1:8080"
python command_center/server.py 8080
pause
