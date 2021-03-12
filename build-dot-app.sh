echo Beginning Package Tear Down

echo Removing dist
rm -rf ./dist

echo Removing build
rm -rf ./build

echo Removing temp build environment
rm -rf ./.venv

echo Package Tear Down Complete

echo Building temp python environment
python3.9 -m venv .venv

echo Activating python environment
source ./.venv/bin/activate

echo installing required pacakges to build environment
pip install -r build-requirements.txt

echo Creating App Package
python setup.py py2app

echo Removing temp build environment
rm -rf ./.venv

echo Removing existing zip
rm -rf ./Photo Whittler.zip

echo Zipping photo whittler
zip "Photo Whittler.zip" "./dist/Photo Whittler.app"

echo Photo Whittler Creation complete!