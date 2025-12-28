# webcheck-py

The Webcheck tool performs various checks on internet domains and hosts.

There are 3 different types of checks available:

- **Domain checks**: Perform checks related to domain configuration, such as DNS records, SSL certificates, and domain reputation.
- **Host checks**: Perform checks on specific hosts or IP addresses, including open ports, services, and vulnerabilities.
- **Web checks**: Perform checks on web applications, including security headers and content analysis.

## Checks

The following checks are available in Webcheck:


- **Hosts**:
  - [x] Ping
  - [x] Open Ports
  - [ ] Reverse DNS
  - [ ] Geolocation
  - [ ] Service Detection (e.g., HTTP, FTP)
  - [ ] Vulnerability Scan
  - [ ] ~~Traceroute~~


- **Domains**:
  - [x] IP Address
    - [x] IPv4 Address
    - [x] IPv6 Address
  - [x] DNS Records
    - [x] A Records
    - [x] AAAA Records
    - [x] CNAME Records
    - [x] MX Records
    - [x] NS Records
    - [x] SOA Records
    - [x] TXT Records
  - [x] INTERNIC Information
  - [ ] WHOIS Information
  - [ ] DNSSEC
  - [ ] Subdomains
  - [ ] Domain Reputation
  - [ ] Domain Blocklist
  - [x] Qualys SSL Check (https://www.ssllabs.com/ssltest/)


- **Web**:
  - [ ] HTTP Headers
    - [x] Security Headers
      - [x] Content Security Policy (CSP)
      - [x] X-Content-Type-Options
      - [x] X-Frame-Options
      - [ ] Referrer-Policy
      - [ ] Permissions-Policy
    - [x] Strict-Transport-Security (HSTS)
    - [ ] Cookie Headers
    - [x] WAF Detection
  - [x] SSL Certificate
  - [ ] Google Website Speed Test (API Key required) (https://www.googleapis.com/pagespeedonline)
  - [ ] Website Ranking
    - [ ] Tranco Website Ranking API (API Key required) (https://tranco-list.eu/)
    - [x] Tranco Website Ranking List match (https://tranco-list.eu/)
    - [x] Umbrella Website Ranking List match (https://tranco-list.eu/)
    - [ ] Majestic Million (https://majestic.com/reports/majestic-million)
  - [x] Screenshot (requires Chromium/Playwright)
  - [ ] Threats Intelligence
    - [ ] Google Safe Browsing (API Key required) (https://safebrowsing.google.com/)
    - [ ] VirusTotal (API Key required) (https://www.virustotal.com/)
    - [ ] PhishTank (API Key required) (https://www.phishtank.com/)
    - [ ] URLhaus (https://urlhaus.abuse.ch/)
    - [ ] Spamhaus (https://www.spamhaus.org/)
  - [x] Website Carbon Emissions Estimation (https://www.websitecarbon.com/)

- **Content Analysis**:
  - [x] Redirects
  - [x] Resource Requests
  - [x] Response Times
  - [x] HTML Meta Tags
    - [x] Social Media Meta Tags
      - [x] Open Graph
      - [x] Twitter Cards
  - [x] HTML Content Analysis
    - [x] Techstack
      - [x] Wappalyzer Integration (projectdiscovery/wappalyzergo)
      - [ ] Custom Wappalyzer Rules
    - [x] Privacy Analysis
      - [x] Advertisements (EasyList)
      - [x] Tracking Scripts (EasyPrivacy List)
      - [x] Cookie Banners (EasyList Cookie List/Fanboy's Cookiemonster List)
    - [x] Headings
    - [x] Document Meta Tags
    - [x] Links (Internal/External)
    - [x] Audio Resources
    - [x] Video Resources
    - [x] Images
    - [x] Phone Numbers
    - [x] Email Addresses
    - [ ] Vcards
    - [ ] Forms
    - [ ] Documents/PDFs/XLSX/DOCX
    - [ ] Social Media Links
    - [ ] Iframes
    - [ ] Addresses / Locations / Maps
  - [x] Linked Domains
    - [x] Linked content domains
    - [x] Linked resource domains
  - [x] Robots.txt
  - [x] Security.txt
  - [x] Sitemaps


## Local Development

### Run checks via CLI

```bash
uv run src/webcheckcli.py www.google.com
```


### Run server in development mode

```bash
uv run uvicorn --app-dir . --port 8000 webchecksrv:app --reload
```


## Docker

### Build Docker Image

```bash
docker build -t webcheck-py .
```

### Run scan via Docker

```bash
docker run -it --rm -v $PWD/data:/app/data --name webcheck webcheck-py webcheckcli --help
```

```bash
docker run -it --rm -v $PWD/data:/app/data --name webcheck webcheck-py webcheckcli @/app/data/domains.txt
```

### Run server via Docker

```bash
docker run -d -p 8000:8000 -v $PWD/data:/app/data --name webcheck-web webcheck-py webchecksrv
```


## Docker compose

A `compose.yml` file is provided for easier setup of the web server.

### Run server via Docker Compose

```bash
docker compose up -d
```

A web server will be available at `http://localhost:18000`.

A MongoDB instance will be available at `mongodb://localhost:18017`.