from datetime import datetime
import ssl
import socket
from urllib.parse import urlparse

def check_expiry(parsed_cert):
    not_before = parsed_cert["notBefore"]  # e.g. 'Jan  1 00:00:00 2025 GMT'
    not_after  = parsed_cert["notAfter"]

    fmt = "%b %d %H:%M:%S %Y %Z"
    nb = datetime.strptime(not_before, fmt)
    na = datetime.strptime(not_after, fmt)
    now = datetime.utcnow()

    print(f"Valid from : {nb}")
    print(f"Valid until: {na}")
    print(f"Now (UTC)  : {now}")
    if now < nb:
        print("Status: NOT YET VALID")
    elif now > na:
        print("Status: EXPIRED")
    else:
        print("Status: VALID right now")

# def check_hostname(parsed_cert, hostname):
#     try:
#         ssl.match_hostname(parsed_cert, hostname)
#         print(f"Hostname OK: certificate matches {hostname}")
#     except ssl.CertificateError as e:
#         print(f"Hostname mismatch: {e}")

def ssl_handler(url_string):
    try:
        parsed_url = urlparse(url_string)
        hostname = parsed_url.hostname
        port = parsed_url.port or 443
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_OPTIONAL

        print(f"Connecting to {hostname}:{port} to retrieve SSL certificate...")
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get certificate in DER (binary) form
                #der_cert = ssock.getpeercert(binary_form=True)
                # Also get a parsed dict version
                #parsed_cert = ssock.getpeercert()
                parsed_cert = ssock.getpeercert(binary_form=False)

                if not parsed_cert:
                    raise Exception(f"""
                No certificate presented by the server.
                The server is possibly not using SNI (Server Name Indication) to identify itself, and you are connecting to a hostname-aliased IP address.
                Or it may be due to an invalid SSL certificate, or an incomplete SSL handshake at the time the cert is being read.""")

            # Convert DER to PEM (readable / storable)
            #pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
            #print("PEM Certificate:")
            #print(pem_cert)

            #print(parsed_cert)
            #check_expiry(parsed_cert)
            #check_hostname(parsed_cert, hostname)
            return parsed_cert

                
    except Exception as error:
        raise Exception(str(error))

handler = ssl_handler