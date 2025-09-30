# beedev-portal

**Note: This is a local copy pulled from the BeeDev Services GitHub account for local development and testing. This repository is NOT connected to the original BeeDev Services GitHub account. To push changes to the original BeeDev Services repository, you would need access to that remote repository.**

requirements.txt contains all current packages needed as of 9/29/25
pip freeze > requirements.txt (to create/update file)

To update your env with the required packages run:
pip install -r requirements.txt

Flush data in db
python manage.py flush --no-input

# On Mac weasyPrint may cause run issues:
brew update
brew install pkg-config cairo pango gdk-pixbuf libffi harfbuzz fribidi
# (optional but harmless)
brew install libpng jpeg libxml2
pip install -U --force-reinstall weasyprint cairocffi



# May need to install the following for deployment:
sudo apt-get update
sudo apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi8 libxml2 libjpeg62-turbo libpng16-16 fonts-dejavu-core


# Superuser for local branch on Christopher J's machine is:
username: chris_j
password: QueenBeesCrew@24

## Git Remote Configuration
This project has two remotes configured:

- **origin**: `git@github.com:BeeDevServices-BaseSites/beedev-portal.git` (BeeDev Services official repository)
- **momo**: `git@github.com:ChristopherJ1987/BeeDev-Services.git` (Christopher's personal repository)

### Push Commands:
- To push to BeeDev Services: `git push origin [branch-name]`
- To push to personal repo: `git push momo [branch-name]`
- Current branch: `userApp`

### Example Usage:
```bash
# Push current changes to personal repo
git push momo userApp

# Push current changes to BeeDev Services repo
git push origin userApp
```