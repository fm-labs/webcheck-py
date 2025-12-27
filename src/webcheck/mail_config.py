from urllib.parse import urlparse
import dns.resolver

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
            txt_records = []
            txt_result = dns.resolver.resolve(domain, 'TXT')
            for txt in txt_result:
                print("TXT Record:", txt)
                txt_records.append([str(txt)])
        except:
            txt_records = []
        
        # Filter for only email related TXT records
        email_txt_records = []
        for record in txt_records:
            record_string = ''.join(record)
            if (record_string.startswith('v=spf1') or
                record_string.startswith('v=DKIM1') or
                record_string.startswith('v=DMARC1') or
                record_string.startswith('protonmail-verification=') or
                record_string.startswith('google-site-verification=') or
                record_string.startswith('MS=') or
                record_string.startswith('zoho-verification=') or
                record_string.startswith('titan-verification=') or
                'bluehost.com' in record_string):
                email_txt_records.append(record)
        
        # Identify specific mail services
        mail_services = []
        for record in email_txt_records:
            record_string = ''.join(record)
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
        
        # Check MX records for Yahoo
        yahoo_mx = [record for record in mx_records if 'yahoodns.net' in record['exchange']]
        if yahoo_mx:
            mail_services.append({'provider': 'Yahoo', 'value': yahoo_mx[0]['exchange']})
        
        # Check MX records for Mimecast
        mimecast_mx = [record for record in mx_records if 'mimecast.com' in record['exchange']]
        if mimecast_mx:
            mail_services.append({'provider': 'Mimecast', 'value': mimecast_mx[0]['exchange']})
        
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
