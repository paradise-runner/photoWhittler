echo Beginning Package Tear Down

echo removing dist
rm -rf ./dist

echo removing build
rm -rf ./build

echo Package Tear Down Complete

echo Activating python environment
source ./venv/bin/activate

echo Creating App Package
python setup.py py2app
