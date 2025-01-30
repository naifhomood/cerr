@echo off
echo Updating Git repository...
git add data\certificates.json
git commit -m "تحديث من Excel"
git push origin main
pause
