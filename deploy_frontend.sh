#!/bin/bash

#Open the frontend folder
cd frontend

# Run npm install
npm install

# Run npm run build
npm run build

# Move files to Nginx www folder
nginx_www_folder="/var/www/html"


# Check if the Nginx www folder exists
if [ ! -d "$nginx_www_folder" ]; then
    echo "Nginx www folder '$nginx_www_folder' not found."
    exit 1
fi

# Delete contents of Nginx www folder
echo "Deleting contents of Nginx www folder..."
rm -rf "$nginx_www_folder"/*

# Move contents of build folder to Nginx www folder
echo "Moving files to Nginx www folder..."
mv dist/* "$nginx_www_folder"

# Print success message
echo "Deployment completed successfully!"
