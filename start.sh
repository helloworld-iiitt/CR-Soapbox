echo "Installing dependencies..."
pip3 install -r requirements.txt
if [ -d "database" ]
then
    echo "Database folder found"
else
    mkdir "database"
    echo "Database folder created"
fi
if [ -d "dbbackup" ]
then
    echo "Database backup folder found"
else
    mkdir "dbbackup"
    echo "Database backup folder created"
fi
if [ -f "dbbackup/teleBot.sqlite" ]
then
    if [ -f "database/teleBot.sqlite" ]
    then
        rm "database/teleBot.sqlite"
    fi
    cp "dbbackup/teleBot.sqlite" "database/teleBot.sqlite"
    echo "Backup Restored"
elif [ -f "database/teleBot.sqlite" ]
then
    cp "database/teleBot.sqlite" "dbbackup/teleBot.sqlite"
    echo "Present Database Backup completed"
fi
echo "initialising the bot..."
python pyFiles/CR_ALT.py
if [ -f "database/teleBot.sqlite" ]
then
rm "dbbackup/teleBot.sqlite"
fi
cp "database/teleBot.sqlite" "dbbackup/teleBot.sqlite"
echo "Database Backup completed"