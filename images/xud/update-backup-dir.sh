#!/bin/bash

BACKUP_DIR=$1
BACKUP_DIR_VALUE=/root/.xud/.backup-dir-value

if [[ -e $BACKUP_DIR_VALUE ]]; then
    OLD_VALUE=$(cat $BACKUP_DIR_VALUE)
    if [[ $BACKUP_DIR != "$OLD_VALUE" ]]; then
        echo "Backup directory changed from $OLD_VALUE to $BACKUP_DIR."
        echo "$BACKUP_DIR" > "$BACKUP_DIR_VALUE"
        # kill backup daemon
        PID=$(pgrep xud-backup)
        kill "$PID"
    fi
else
    echo "$BACKUP_DIR" > "$BACKUP_DIR_VALUE"
fi
