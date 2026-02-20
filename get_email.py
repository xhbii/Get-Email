#!/usr/bin/env python3

import os
import re
import base64
import imaplib
import datetime
from email.header import decode_header
from bs4 import BeautifulSoup
import mailparser

config = {
    'emailProvider': 'gmail',
    'emailAddress': 'test@gmail.com',
    'emailPassword': 'abcd abcd abcd abcd',
    'imapServer': 'imap.gmail.com',
    'imapPort': 993,
    'folder': 'INBOX',
    'searchCriteria': 'ALL',
    'savePath': './emails',
    'maxEmails': 8,
    'filterMode': 'whitelist',
    'filterList': ['JPM']
}


def decode_str(s):
    value, charset = decode_header(s)[0]
    if isinstance(value, bytes):
        return value.decode(charset or 'utf-8')
    return value


def html_to_markdown(html_content):
    if not html_content:
        return ''
        
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
            
        for table in soup.find_all('table'):
            pass
            
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if src:
                if src.startswith('cid:'):
                    img_tag = f"![{alt or 'Image'}]({src})"
                elif src.startswith('data:image'):
                    img_tag = f"![{alt or 'Image'}]({src})"
                else:
                    img_tag = f"![{alt or 'Image'}]({src})"
                
                img.replace_with(img_tag)
                
        for p in soup.find_all('p'):
            p.append('\n\n')
            
        for h1 in soup.find_all('h1'):
            h1.insert(0, '# ')
            h1.append('\n')
            
        for h2 in soup.find_all('h2'):
            h2.insert(0, '## ')
            h2.append('\n')
            
        for h3 in soup.find_all('h3'):
            h3.insert(0, '### ')
            h3.append('\n')
            
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                li.insert(0, '- ')
                
        for ol in soup.find_all('ol'):
            for i, li in enumerate(ol.find_all('li')):
                li.insert(0, f"{i+1}. ")
                
        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.get_text()
            if href and text:
                a.replace_with(f"[{text}]({href})")
        
        markdown = soup.get_text()
        
        markdown = re.sub(r'\n\s*\n', '\n\n', markdown)
        markdown = re.sub(r'\s+', ' ', markdown).strip()
        
        return markdown
        
    except Exception as e:
        print(f"HTML to Markdown error: {e}")
        return html_content


def parse_email_with_mailparser(email_path):
    try:
        msg = mailparser.parse_from_file(email_path)
        return msg
    except Exception as e:
        print(f"Parse email failed: {e}")
        return None


def save_email_as_markdown(email_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    msg = parse_email_with_mailparser(email_path)
    
    if not msg:
        return None
        
    subject = msg.subject
    if subject is None:
        subject = "No Subject"
        
    safe_subject = re.sub(r'[\\/*?:"<>|]', '_', str(subject))
    
    try:
        if msg.date:
            timestamp = msg.date.strftime('%Y%m%d_%H%M%S')
        else:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    except:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
    filename = f"{timestamp}_{safe_subject}.md"
    output_path = os.path.join(output_dir, filename)
    
    md_content = []
    
    md_content.append(f"# {subject}\n")
    
    md_content.append("## Sender Info")
    if msg.from_:
        md_content.append(f"- **From**: {msg.from_[0][0]} ({msg.from_[0][1]})")
    if msg.to:
        recipients = []
        for name, email in msg.to:
            if name and email:
                recipients.append(f"{name} ({email})")
            elif email:
                recipients.append(email)
        if recipients:
            md_content.append(f"- **To**: {', '.join(recipients)}")
    if msg.date:
        md_content.append(f"- **Date**: {msg.date}")
    
    md_content.append("\n## Email Body")
    
    if msg.text_plain:
        md_content.append(msg.text_plain[0])
    elif msg.text_html:
        md_content.append(html_to_markdown(msg.text_html[0]))
    
    if msg.attachments:
        md_content.append("\n## Attachments")
        for att in msg.attachments:
            md_content.append(f"- [{att['filename']}]({os.path.join(os.path.splitext(filename)[0], att['filename'])})")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    if msg.attachments:
        att_dir = os.path.join(output_dir, os.path.splitext(filename)[0])
        os.makedirs(att_dir, exist_ok=True)
        
        for att in msg.attachments:
            att_path = os.path.join(att_dir, att['filename'])
            payload = att['payload']
            
            try:
                if isinstance(payload, str):
                    try:
                        decoded_data = base64.b64decode(payload)
                        with open(att_path, 'wb') as f:
                            f.write(decoded_data)
                    except Exception:
                        with open(att_path, 'w', encoding='utf-8') as f:
                            f.write(payload)
                elif isinstance(payload, bytes):
                    try:
                        decoded_data = base64.b64decode(payload)
                        with open(att_path, 'wb') as f:
                            f.write(decoded_data)
                    except Exception:
                        with open(att_path, 'wb') as f:
                            f.write(payload)
                else:
                    with open(att_path, 'w', encoding='utf-8') as f:
                        f.write(str(payload))
            except Exception as e:
                print(f"Save attachment failed {att['filename']}: {e}")
                continue
    
    return output_path


def should_process_email(email_sender, email_subject):
    filter_mode = config.get('filterMode', 'none')
    filter_list = config.get('filterList', [])
    
    if filter_mode == 'none' or not filter_list:
        return True
    
    email_lower = email_sender.lower() if email_sender else ''
    subject_lower = email_subject.lower() if email_subject else ''
    
    for keyword in filter_list:
        keyword_lower = keyword.lower()
        if keyword_lower in email_lower or keyword_lower in subject_lower:
            return filter_mode == 'whitelist'
    
    return filter_mode == 'blacklist'


def main():
    print("=== Email Fetch and Convert Tool ===")
    
    os.makedirs(config['savePath'], exist_ok=True)
    
    existing_files = set(f for f in os.listdir(config['savePath']) if f.endswith('.md'))
    print(f"Existing email files: {len(existing_files)}")
    
    try:
        print(f"Connecting to {config['emailProvider']} mail server...")
        
        mail = imaplib.IMAP4_SSL(config['imapServer'], config['imapPort'])
        
        mail.login(config['emailAddress'], config['emailPassword'])
        print("Login successful")
        
        result, data = mail.select(config['folder'])
        if result != 'OK':
            print(f"Failed to select folder: {data}")
            return
            
        print(f"Current folder: {config['folder']}")
        
        print(f"Searching emails (max {config['maxEmails']})...")
        result, email_ids = mail.search(None, config['searchCriteria'])
        
        if result == 'OK' and email_ids[0]:
            email_id_list = email_ids[0].split()
            
            if config['maxEmails'] and len(email_id_list) > config['maxEmails']:
                email_id_list = email_id_list[-config['maxEmails']:]
            
            print(f"Found {len(email_id_list)} emails to process")
            
            for email_id in email_id_list:
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if result != 'OK' or not msg_data:
                        continue
                    
                    raw_email = msg_data[0][1]
                    
                    temp_path = 'temp_email.eml'
                    with open(temp_path, 'wb') as f:
                        f.write(raw_email)
                    
                    msg = mailparser.parse_from_file(temp_path)
                    
                    email_sender = msg.from_[0][1] if msg and msg.from_ else ''
                    email_subject = msg.subject or ''
                    
                    if not should_process_email(email_sender, email_subject):
                        filter_mode = config.get('filterMode', 'none')
                        print(f"Filtered out ({filter_mode}): {email_subject[:50]}...")
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        continue
                    
                    print(f"Processing email...")
                    
                    output_path = save_email_as_markdown(temp_path, config['savePath'])
                    
                    if output_path:
                        filename = os.path.basename(output_path)
                        
                        if filename in existing_files:
                            print(f"Email already exists, skip: {filename}")
                            if os.path.exists(output_path):
                                os.remove(output_path)
                        else:
                            print(f"Saved to: {output_path}")
                            existing_files.add(filename)
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
                except Exception as e:
                    import traceback
                    print(f"Process email failed: {e}")
                    print(f"Traceback: {traceback.format_exc()}")
                    continue
        
        print("\n=== Processing Complete ===")
        
    except Exception as e:
        print(f"Connect or process failed: {e}")
        
    finally:
        try:
            mail.logout()
        except:
            pass


if __name__ == "__main__":
    main()
