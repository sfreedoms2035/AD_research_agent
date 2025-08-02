# Google Drive Integration Setup Guide

This guide explains how to set up Google Drive integration for the Automated Driving Research Agent.

## Prerequisites

1. A Google account
2. Access to Google Cloud Console
3. Basic understanding of OAuth 2.0 authentication

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" then "New Project"
3. Enter a project name (e.g., "AD-Research-Agent")
4. Click "Create"

## Step 2: Enable the Google Drive API

1. In the Google Cloud Console, make sure your project is selected
2. Navigate to "APIs & Services" > "Library"
3. Search for "Google Drive API"
4. Click on "Google Drive API" in the search results
5. Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (for personal use)
3. Click "Create"
4. Fill in the required information:
   - App name: "AD Research Agent"
   - User support email: Your Google email
   - Developer contact information: Your Google email
5. Click "Save and Continue"
6. On the Scopes page, click "Add or Remove Scopes"
7. Search for and add the following scope:
   - `https://www.googleapis.com/auth/drive` (See, edit, create, and delete all of your Google Drive files)
8. Click "Update" then "Save and Continue"
9. On the Test users page, add your Google account as a test user
10. Click "Save and Continue" to finish

## Step 4: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. For "Application type", select "Desktop application"
4. Enter a name (e.g., "AD Research Agent Desktop")
5. Click "Create"
6. Click "OK" to close the confirmation dialog
7. Click the download icon (⬇️) next to your new OAuth client ID
8. Save the file as `credentials.json` in the same directory as the research agent

## Step 5: Configure the Research Agent

1. Update the `config.json` file to enable Google Drive upload:

```json
{
  "research_settings": {
    "days_back": 7,
    "top_papers": 10,
    "download_papers": true,
    "save_summaries": true,
    "parallel_workers": 3,
    "upload_to_google_drive": true,
    "google_drive_folder_id": "YOUR_FOLDER_ID_HERE"
  }
}
```

2. To upload to a specific folder, get the folder ID from Google Drive:
   - Open Google Drive in your browser
   - Navigate to the folder where you want to upload results
   - The folder ID is the part of the URL after `/folders/`
   - Example: In `https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j`, the folder ID is `1a2b3c4d5e6f7g8h9i0j`

## Step 6: Install Required Dependencies

Make sure you have all required dependencies installed:

```bash
pip install -r requirements.txt
```

## First-Time Authentication

When you run the agent for the first time with Google Drive enabled:

1. The agent will open a browser window asking you to sign in to your Google account
2. Select the Google account you want to use
3. You may see a warning that the app is not verified - this is normal for apps in development
4. Click "Advanced" then "Go to [your app name] (unsafe)" 
5. Click "Allow" to grant the necessary permissions
6. The authentication token will be saved to `token.json` for future use

## Security Notes

- Keep `credentials.json` and `token.json` secure
- `token.json` contains sensitive authentication information
- If you need to revoke access, go to your Google Account settings > Security > Third-party apps with account access

## Usage

Once set up, the agent will automatically:
1. Create a zip file of the research results
2. Upload it to your Google Drive
3. Clean up the temporary zip file
4. Use the saved token for future uploads (no need to re-authenticate)

## Troubleshooting

If you encounter authentication issues:
1. Delete `token.json` to force re-authentication
2. Make sure `credentials.json` is in the correct location
3. Ensure the Google Drive API is enabled for your project
4. Check that your Google account has sufficient permissions
5. Verify that you've added your account as a test user in the OAuth consent screen
6. Make sure you've configured the OAuth consent screen with the required scopes

## Common Error Solutions

### "access_denied" Error
This typically occurs when:
- The OAuth consent screen is not properly configured
- Your account is not added as a test user
- The required scopes are not added to the consent screen

Solution:
1. Go to Google Cloud Console > APIs & Services > OAuth consent screen
2. Ensure your account is added as a test user
3. Check that the Drive API scope is added
4. Try the authentication process again

### "invalid_client" Error
This occurs when the credentials.json file is invalid or corrupted.

Solution:
1. Download a new credentials.json file from the Google Cloud Console
2. Replace the existing credentials.json file
3. Delete token.json if it exists
4. Try the authentication process again
