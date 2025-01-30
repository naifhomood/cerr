@echo off
echo Creating scheduled task for Excel-JSON sync...

REM Create the scheduled task
schtasks /create /tn "ExcelJsonSync" /tr "python \"%~dp0sync.py\"" /sc minute /mo 5 /f

echo Task created successfully! It will run every 5 minutes.
