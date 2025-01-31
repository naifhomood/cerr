@echo off
echo Updating Git repository...

echo Pulling latest changes...
git pull origin main

echo Updating local changes...
python sync.py

echo Pushing to GitHub...
git add data\certificates.json
git commit -m "تحديث من Excel"
git push origin main

echo Done!
pause
