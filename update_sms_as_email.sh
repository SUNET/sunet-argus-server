#!/bin/bash

# File path
FILE="/var/opt/argus-server/src/argus/notificationprofile/media/sms_as_email.py"

# Check if the file exists
if [[ -f "$FILE" ]]; then
    # Use sed to modify the content in place
    sed -i.bak 's/message=f"{event.description}"/message=f"[ARGUS] {event.description}"/g' "$FILE"
    
    # Check operation success
    if grep -q 'message=f"[ARGUS] {event.description}"' "$FILE"; then
        echo "The value was successfully updated in $FILE."
    else
        echo "Failed to update the value in $FILE. Please check the script."
    fi
else
    echo "The file $FILE does not exist. Please check the file path."
fi
