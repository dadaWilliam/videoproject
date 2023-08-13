#!/bin/bash
# chmod +x mac_run.sh
# ./mac_run.sh
# /Users/william/videoproject/mac_run.sh

echo "cd /Users/william/videoproject/"
cd /Users/william/videoproject/

echo "source env/bin/activate"
source env/bin/activate

# Check for "-install" command-line argument
if [[ $1 == "-install" ]]; then
    echo "Running installments."
    pip3 install -r requirements.txt
elif [[ $1 == "-m" ]]; then
    echo "make migrations"
    python manage.py makemigrations
    echo "migrate"
    python manage.py migrate

else
    echo "No installments and migrations, delaying script for 1 s."
    sleep 1
fi

echo "Server is running. Please check."
python manage.py runserver
echo " "
echo "End."
