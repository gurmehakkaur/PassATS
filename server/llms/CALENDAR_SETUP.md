# Google Calendar MCP Setup Guide

## Step 1: Get Google Calendar API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Calendar API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app"
   - Download the JSON file
   - Rename it to `credentials.json`
   - Place it in `d:\Side Projects\PassATS\server\` directory

## Step 2: Install Dependencies

```bash
cd d:\Side Projects\PassATS\server\llms
pip install -r requirements.txt
```

## Step 3: First-Time Authentication

When you first use the calendar feature:
1. A browser window will open
2. Sign in with your Google account
3. Grant calendar access permissions
4. A `token.pickle` file will be created automatically
5. Future requests will use this token (no browser needed)

## Step 4: Usage in Chat

You can now use natural language to manage your calendar:

**Examples:**
- "Schedule a meeting with Sarah tomorrow at 2pm"
- "What's on my calendar this week?"
- "Add a reminder for project deadline on Friday"
- "Cancel my 3pm meeting"
- "Move my dentist appointment to next Tuesday"

## Step 5: Calendar Tools Available

The AI can now:
- ✅ View upcoming events
- ✅ Create new events
- ✅ Update existing events
- ✅ Delete events
- ✅ Search events by keyword
- ✅ Suggest optimal meeting times

## Troubleshooting

**Error: credentials.json not found**
- Make sure you downloaded and placed credentials.json in the server folder

**Error: Token expired**
- Delete `token.pickle` and re-authenticate

**Error: Permission denied**
- Make sure you granted calendar access during OAuth flow

## Security Notes

- `credentials.json` contains your OAuth client secrets
- `token.pickle` contains your access token
- **Add both to `.gitignore`** to avoid committing them
- Never share these files publicly
