from urllib.parse import urlparse
import dns.resolver

KNOWN_MX_RECORDS = {
    'yahoodns.net': 'Yahoo',
    'mimecast.com': 'Mimecast',
    'outlook.com': 'Outlook',
    'google.com': 'Gmail',
    'protonmail.com': 'ProtonMail',
    'zoho.com': 'Zoho',
    'titan.email': 'Titan',
    'bluehost.com': 'BlueHost',
}

async def mail_config_handler(domain):
    try:
        if '://' in domain:
            parsed_url = urlparse(domain)
            domain = parsed_url.hostname or parsed_url.path
        
        # Get MX records
        try:
            mx_records = []
            mx_result = dns.resolver.resolve(domain, 'MX')
            for mx in mx_result:
                mx_records.append({
                    'exchange': str(mx.exchange),
                    'priority': mx.preference
                })
        except:
            mx_records = []
        
        # Get TXT records
        try:
            answer = dns.resolver.resolve(domain, 'TXT')
            txt_records = [r.to_text().strip('"') for r in answer]
            #print("TXT Records found:", txt_records)
        except:
            txt_records = []
        
        # Filter for only email related TXT records
        email_txt_records = []
        for record_string in txt_records:
            if (record_string.startswith('v=spf1') or
                record_string.startswith('v=DKIM1') or
                record_string.startswith('v=DMARC1') or
                record_string.startswith('MS=') or
                record_string.startswith('protonmail-verification=') or
                record_string.startswith('google-site-verification=') or
                record_string.startswith('zoho-verification=') or
                record_string.startswith('titan-verification=') or
                '-verification=' in record_string or
                'bluehost.com' in record_string):
                email_txt_records.append(record_string)
        
        # Identify specific mail services
        mail_services = []
        verification_records = []
        for record_string in email_txt_records:
            if record_string.startswith('protonmail-verification='):
                mail_services.append({'provider': 'ProtonMail', 'value': record_string.split('=')[1]})
            elif record_string.startswith('google-site-verification='):
                mail_services.append({'provider': 'Google Workspace', 'value': record_string.split('=')[1]})
            elif record_string.startswith('MS='):
                mail_services.append({'provider': 'Microsoft 365', 'value': record_string.split('=')[1]})
            elif record_string.startswith('zoho-verification='):
                mail_services.append({'provider': 'Zoho', 'value': record_string.split('=')[1]})
            elif record_string.startswith('titan-verification='):
                mail_services.append({'provider': 'Titan', 'value': record_string.split('=')[1]})
            elif 'bluehost.com' in record_string:
                mail_services.append({'provider': 'BlueHost', 'value': record_string})
            elif record_string.startswith('apple-domain-verification='):
                verification_records.append({'provider': 'Apple iCloud Mail', 'value': record_string.split('=')[1]})
            elif record_string.startswith('dropbox-domain-verification='):
                verification_records.append({'provider': 'Dropbox', 'value': record_string.split('=')[1]})
            elif record_string.startswith('openai-domain-verification='):
                verification_records.append({'provider': 'OpenAI', 'value': record_string.split('=')[1]})

        # Check known MX services
        for known_mx, provider_name in KNOWN_MX_RECORDS.items():
            known_mx_matches = [record for record in mx_records if known_mx in record['exchange']]
            if known_mx_matches:
                mail_services.append({'provider': provider_name, 'value': known_mx_matches[0]['exchange']})
        
        return {
            'mxRecords': mx_records,
            'txtRecords': email_txt_records,
            'mailServices': mail_services
        }
        
    except Exception as error:
        if hasattr(error, 'errno') and error.errno in [-2, -3]:
            return {'skipped': 'No mail server in use on this domain'}
        else:
            return {
                'statusCode': 500,
                'body': {'error': str(error)}
            }

handler = mail_config_handler
