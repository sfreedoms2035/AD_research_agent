#!/usr/bin/env python3
"""
Google Drive Token Renewal Script

This script helps you renew your Google Drive authentication token.
Run this when you need to refresh your Google Drive access.
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google Drive API scope
SCOPES = ["https://www.googleapis.com/auth/drive"]

def renew_google_drive_token():
    """Renew Google Drive authentication token."""
    
    print("Google Drive Token Renewal")
    print("=" * 30)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ Error: credentials.json not found!")
        print("\nTo get credentials.json:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download credentials.json and place it in this directory")
        return False
    
    creds = None
    
    # Check if token.json exists
    if os.path.exists('token.json'):
        print("📋 Found existing token.json - attempting to refresh...")
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            # Try to refresh the token
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing existing token...")
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
            else:
                print("ℹ️  Token is still valid, no refresh needed.")
                
        except Exception as e:
            print(f"⚠️  Could not refresh token: {e}")
            print("🔄 Will create new token...")
            creds = None
    
    # If no valid credentials, create new ones
    if not creds or not creds.valid:
        print("🔐 Creating new authentication token...")
        try:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ New token created successfully!")
        except Exception as e:
            print(f"❌ Error creating new token: {e}")
            return False
    
    # Save the credentials for the next run
    try:
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("💾 Token saved to token.json")
        print("✅ Token renewal complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False

def check_current_token():
    """Check the current token status."""
    
    if not os.path.exists('token.json'):
        print("📋 No token.json found - you need to create a new token")
        return False
    
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        print("📊 Current Token Status:")
        print(f"   Valid: {creds.valid}")
        print(f"   Expired: {creds.expired}")
        
        if creds.expiry:
            print(f"   Expires: {creds.expiry}")
        
        return creds.valid
        
    except Exception as e:
        print(f"❌ Error reading token: {e}")
        return False

def main():
    """Main function."""
    
    print("Google Drive Authentication Manager")
    print("=" * 35)
    
    # Check current token
    print("\n1. Checking current token...")
    current_valid = check_current_token()
    
    if current_valid:
        print("\n✅ Current token is valid - no action needed")
        response = input("\nDo you want to force renewal anyway? (y/N): ").strip().lower()
        if response != 'y':
            return
    
    # Renew token
    print("\n2. Renewing token...")
    success = renew_google_drive_token()
    
    if success:
        print("\n🎉 Token renewal completed successfully!")
        print("You can now use the research agent with Google Drive upload.")
    else:
        print("\n❌ Token renewal failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
