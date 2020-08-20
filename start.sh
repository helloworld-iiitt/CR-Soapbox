echo "Installing dependencies..."
pip3 install -r requirements.txt
echo "Checking  Backup files"
if [ -d "database" ]
then
    echo "Database folder found"
else
    mkdir "database"
    echo "Database folder created"
fi
if [ -f "dbbackup/teleBot.sqlite" ]
then
    rm "database/teleBot.sqlite"
    cp "dbbackup/teleBot.sqlite" "database/teleBot.sqlite"
    echo "Backup Restored"
elif [ -f "database/teleBot.sqlite" ]
then
    mkdir "dbbackup"
    echo "Backup folder created"
    cp "database/teleBot.sqlite" "dbbackup/teleBot.sqlite"
    echo "Present Database Backup completed"
else 
    mkdir "dbbackup"
    echo "Created Database Backup folder"
fi
echo "initialising the bot..."
python pyFiles/CR_ALT.py
cp "database/teleBot.sqlite" "dbbackup/teleBot.sqlite"
echo "Database Backup completed"