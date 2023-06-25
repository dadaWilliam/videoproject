#!/bin/bash
# chmod +x mac_run.sh
# ./mac_run.sh
# /Users/william/videoproject/mac_run.sh

echo "cd /Users/william/videoproject/"
cd /Users/william/videoproject/

echo "source env/bin/activate"
source env/bin/activate

echo "Server is running. Please check."
python manage.py runserver
echo " "
echo "End."
