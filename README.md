# beedev-portal

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
