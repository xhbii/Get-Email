# Email to Markdown Skill - Claude Code Integration

## Overview

This guide explains how to configure Claude Code (Trae IDE) to use the email-to-markdown skill for fetching emails from your mailbox and converting them to Markdown format.

## Prerequisites

- Claude Code
- Python 3.7+
- Gmail account with IMAP enabled and App Password generated

## Setup Steps

### 1. Configure Your Email Credentials

Edit `get_email.py` and update the `config` dictionary with your email settings:

```python
config = {
    'emailProvider': 'gmail',
    'emailAddress': 'your.email@gmail.com',
    'emailPassword': 'your_app_password',  # Gmail: Use App Password
    'imapServer': 'imap.gmail.com',
    'imapPort': 993,
    'folder': 'INBOX',
    'searchCriteria': 'ALL',
    'savePath': './emails', # none/whitelist/blacklist
    'maxEmails': 8,
    'filterMode': 'none',
    'filterList': []
}
```

### 2. Install Dependencies

```bash
pip install mailparser beautifulsoup4
```

### 3. Test the Script

```bash
python3 get_email.py
```

## Using with Claude Code

### Method 1: Run Directly

You can ask Claude to run the email fetch script:

```
"Please run the email fetch script to get my latest emails"
```

### Method 2: Configure as a Tool

To make this skill available in Claude Code, you can:

1. **Create a custom command** in Claude Code:
   - Use `/email` or similar custom command
   - Point it to run `python3 get_email.py`

2. **Add to Claude Code config** (if supported):
   ```json
   {
     "skills": {
       "email-to-markdown": {
         "command": "python3 /path/to/get_email.py",
         "description": "Fetch emails and convert to Markdown"
       }
     }
   }
   ```

### Method 3: Call from Conversation

When you need to fetch emails, simply describe your requirement to Claude:

- "Get my latest 5 emails from Gmail"
- "Fetch unread emails and save as Markdown"
- "Download emails from this week"

Claude will understand the intent based on the SKILL.md description and help you use the script.

## Skill Configuration

The skill is defined in `SKILL.md` with:

- **Name**: `email-to-markdown`
- **Trigger**: When user needs to fetch emails and save as Markdown
- **Capabilities**:
  - Connect to Gmail via IMAP
  - Search emails with various criteria
  - Parse email content (plain text / HTML)
  - Convert HTML to Markdown
  - Save attachments

## Output

After running, emails are saved to `./emails/` directory:

```
emails/
├── 20260220_123456_subject1.md
├── 20260220_123456_subject1/
│   └── attachment.pdf
└── 20260220_123457_subject2.md
```

## Search Criteria Examples

| Criteria | Description | Usage |
|----------|-------------|-------|
| `ALL` | All emails | Default |
| `UNSEEN` | Unread emails | `searchCriteria: 'UNSEEN'` |
| `SINCE "01-Feb-2026"` | Emails since date | Date filter |
| `FROM "sender@example.com"` | From specific sender | Sender filter |

## Filter Mode

Filter emails by whitelist or blacklist:

```python
config = {
    'filterMode': 'blacklist',  # none / whitelist / blacklist
    'filterList': ['JPM', 'Jefferies', 'newsletter']
}
```

| Mode | Description |
|------|-------------|
| `none` | No filter, process all emails |
| `whitelist` | Only process emails containing keywords |
| `blacklist` | Skip emails containing keywords |

**Example:**
```python
# Only process emails from academic sources
'filterMode': 'whitelist',
'filterList': ['arxiv', 'paper', 'research'],

# Skip marketing emails
'filterMode': 'blacklist',
'filterList': ['promotion', 'deal', 'discount'],
```

## Troubleshooting

### Gmail Authentication Error
- Enable 2-Factor Authentication
- Generate an App Password: https://myaccount.google.com/apppasswords

### IMAP Not Enabled
- Go to Gmail Settings → Forwarding and POP/IMAP → Enable IMAP

### Connection Timeout
- Check firewall/network settings
- Try different `imapPort` (993 for SSL)

## Files

- `get_email.py` - Main script
- `SKILL.md` - Skill definition for Claude Code
- `email-api-reference.md` - API documentation
- `emails/` - Output directory for downloaded emails
