#!/bin/bash
# chmod +x kill_migrate.sh
# ./kill_migrate.sh
# Check if gunicorn is running. Repeat the check every 5 seconds until it is.
while ! (pstree -ap | grep -q "gunicorn")
do
    echo "Waiting for gunicorn to start..."
    sleep 5
done


# Find gunicorn processes
processes=$(pstree -ap | grep gunicorn)

# Check if any processes were found
if [[ -z "$processes" ]]; then
    echo "No gunicorn processes found."
else
    echo "Found gunicorn processes. "

    # Kill gunicorn processes
    echo "Killing them now."
    pkill -f gunicorn
    echo "Waiting 2 s now."
    sleep 2
fi

echo "Change to the project directory"
echo "/home/sites/edu.iamdada.xyz"
# Navigate to the directory
cd /home/sites/edu.iamdada.xyz

# Activate the virtual environment
echo "Activate the virtual environment"
source env/bin/activate

echo "Waiting 1 s now."
sleep 1

# Navigate to the project directory
echo "/home/sites/edu.iamdada.xyz/videoproject-master"
cd /home/sites/edu.iamdada.xyz/videoproject-master

# Check for "-install" command-line argument
if [[ $1 == "-install" ]]; then
    echo "Running installments."
    pip3 install -r requirements.txt
else
    echo "No installments, delaying script for 1 s."
    sleep 1
fi

# Run Django commands
python3 manage.py makemigrations
echo "Waiting 2 s now."
sleep 2
python3 manage.py migrate
echo "Waiting 2 s now."
sleep 2


echo "/home/sites/edu.iamdada.xyz/videoproject-master"
cd /home/sites/edu.iamdada.xyz/videoproject-master

echo "Run gunicorn"
# Run gunicorn
nohup /home/sites/edu.iamdada.xyz/env/bin/gunicorn --bind unix:/tmp/xueba.ca.socket videoproject.wsgi:application &

echo "Gunicorn process started."
