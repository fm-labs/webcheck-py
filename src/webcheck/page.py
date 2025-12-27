import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from webcheck.conf import WEBCHECK_USER_AGENT
from .adblock import adblock_rules, privacy_rules, cookiemonster_rules

async def page_handler(url: str):
    """
    Load the page using a headless browser and capture resource loading details.

    :param url:
    :return:
    """
    resources = list()
    requests = list()

    time_start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # log all resource requests
        browser_context = await browser.new_context(user_agent=WEBCHECK_USER_AGENT)

        def log_request(request):
            print(f"[REQUEST] {request.method} {request.url} {request.resource_type}")
            requests.append({
                "url": request.url,
                "method": request.method,
                "resourceType": request.resource_type,
                "headers": request.headers
            })

        page = await browser_context.new_page()
        page.on("request", log_request)

        # create a router that intercepts requests, checks them against adblock rules, and blocks them if needed
        async def route_intercept(route, request):
            if cookiemonster_rules.should_block(request.url):
                print(f"[BLOCKED] {request.url}")
                await route.abort()
            else:
                await route.continue_()
        await page.route("**/*", route_intercept)

        response = None
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"[ERROR] {e}. Fallback to domcontentloaded.")
            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e2:
                print(f"[ERROR] {e2}. Giving up on loading the page.")
                await browser.close()
                raise Exception(f"Failed to load the page: {str(e2)}")

        if response is None:
            await browser.close()
            raise Exception("No response received when loading the page.")

        # Grab the http response headers
        headers = response.headers
        print("Response Headers:")
        for k, v in headers.items():
            print(f"  {k}: {v}")

        # Grab the full page content
        try:
            content = await page.content()
            print(f"Page content length: {len(content)} characters")
        except Exception as e:
            content = ""
            print(f"Error getting page content: {str(e)}")

        # Grab resource timing entries from the browser
        resources = await page.evaluate(
            """() => performance.getEntriesByType('resource').map(e => ({
                name: e.name,
                initiatorType: e.initiatorType,
                startTime: e.startTime,       // ms from navigation start
                duration: e.duration,         // ms
                transferSize: e.transferSize, // bytes on the wire
                encodedBodySize: e.encodedBodySize,
                decodedBodySize: e.decodedBodySize
            }))"""
        )

        for r in resources:
            print(
                f"{r['initiatorType']:10} | "
                f"{r['duration']:8.2f} ms | "
                f"{r['transferSize']:8} B | "
                f"{r['name']}"
            )
        await browser.close()

    time_end = time.time()
    diff_ms = (time_end - time_start) * 1000
    print(f"Page load time: {diff_ms:.2f} ms")

    total_bytes = sum(r.get("transferSize", 0) for r in resources)
    print(f"Total resources: {len(resources)}, Total bytes transferred: {total_bytes} B")

    result = {
        "status": "success",
        "url": url,
        "headers": headers,
        "requests": requests,
        "resources": resources,
        "pageLoadTimeMs": diff_ms,
        "totalBytesTransferred": total_bytes
    }

    # Parse the HTML content for basic info
    parser = QuickHtmlParser(content, base_url=url)
    parsed_data = parser.parse()
    result["parsed"] = parsed_data

    # Adblock url detection
    adblock_detections = []
    privacy_detections = []
    cookiemonster_detections = []
    for req in requests:
        if adblock_rules.should_block(req["url"]):
            print(f"[*] Adblock list hit: {req['url']}")
            adblock_detections.append(req["url"])
        if privacy_rules.should_block(req["url"]):
            print(f"[*] Privacy list hist: {req['url']}")
            privacy_detections.append(req["url"])
        if cookiemonster_rules.should_block(req["url"]):
            print(f"[*] Cookiemonster list hit: {req['url']}")
            cookiemonster_detections.append(req["url"])
    result["adblockDetections"] = adblock_detections
    result["trackerDetections"] = privacy_detections
    result["cookiebannerDetections"] = cookiemonster_detections

    return result


class QuickHtmlParser:
    """
    A quick and dirty HTML parser to extract basic information using beautifulsoup
    This parser extracts the title, meta tags, headings, links, stylesheets, scripts, and images.
    """

    def __init__(self, html: str, base_url: str = ""):
        self.html = html.lower()
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.base_url = base_url

    def title(self) -> str:
        title_tag = self.soup.find("title")
        return title_tag.get_text().strip() if title_tag else None

    def meta_tags(self) -> dict:
        meta_data = {}
        for meta in self.soup.find_all("meta"):
            if 'name' in meta.attrs and 'content' in meta.attrs:
                meta_data[meta['name'].strip().lower()] = meta['content'].strip()
            elif 'property' in meta.attrs and 'content' in meta.attrs:
                meta_data[meta['property'].strip().lower()] = meta['content'].strip()
        return meta_data

    def headings(self) -> dict[str, list[str]]:
        headings = {}
        for level in range(1, 7):
            tag = f"h{level}"
            headings[tag] = [h.get_text().strip() for h in self.soup.find_all(tag)]
        return headings

    def links(self) -> list[tuple[str, str]]:
        links = []
        for a in self.soup.find_all('a', href=True):
            url = a['href'].strip()
            title = a.get_text().strip()
            if title is None or title == "":
                title = a['title'].strip() if a.has_attr('title') else title

            if url and title:
                links.append((url, title))
        return links


    def stylesheets(self) -> list[tuple[str, str]]:
        return [(link['href'], "") for link in self.soup.find_all('link', rel='stylesheet', href=True)]

    #def fonts(self):
    #    return [link['href'] for link in self.soup.find_all('link', href=True) if 'font' in link['href'].lower()]

    def scripts(self) -> list[tuple[str, str]]:
        return [(script['src'], "") for script in self.soup.find_all('script', src=True)]

    def images(self) -> list[tuple[str, str]]:
        return [(img['src'], img['alt'] if img.has_attr('alt') else "") for img in self.soup.find_all('img', src=True)]

    def audios(self) -> list[tuple[str, str]]:
        return [(audio['src'], audio['title'] if audio.has_attr('title') else "") for audio in self.soup.find_all('audio', src=True)]

    def videos(self) -> list[tuple[str, str]]:
        return [(video['src'], video['title'] if video.has_attr('title') else "") for video in self.soup.find_all('video', src=True)]

    def phones(self) -> list[tuple[str, str]]:
        return [(a['href'], a.get_text().strip()) for a in self.soup.find_all('a', href=True) if a['href'].startswith('tel:')]

    def emails(self) -> list[tuple[str, str]]:
        return [(a['href'], a.get_text().strip()) for a in self.soup.find_all('a', href=True) if a['href'].startswith('mailto:')]

    def normalize_url(self, url: str):
        base_url = self.base_url
        return urljoin(base_url, url)

    def normalize_urls(self, urls: list[tuple[str, str]]) -> list[tuple[str, str]]:
        normalized = [(self.normalize_url(url[0]), url[1]) for url in urls]
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in normalized:
            if url[0] not in seen:
                seen.add(url[0])
                unique_urls.append(url)
        return sorted(unique_urls)

    def extract_domains_from_urls(self, urls: list):
        from urllib.parse import urlparse
        domains = set()
        for url in urls:
            parsed_url = urlparse(url[0])
            domain = parsed_url.netloc
            if domain:
                domains.add(domain)
        # sort domains alphabetically
        return sorted(list(domains))

    def parse(self):
        return {
            "title": self.title(),
            "meta": self.meta_tags(),
            "headings": self.headings(),
            "links": self.normalize_urls(self.links()),
            "stylesheets": self.normalize_urls(self.stylesheets()),
            "scripts": self.normalize_urls(self.scripts()),
            "images": self.normalize_urls(self.images()),
            "audios": self.normalize_urls(self.audios()),
            "videos": self.normalize_urls(self.videos()),
            "phones": self.phones(),
            "emails": self.emails(),
            "linkDomains": self.extract_domains_from_urls(self.normalize_urls(self.links())),
            "resourceDomains": self.extract_domains_from_urls(
                self.normalize_urls(
                    self.stylesheets() +
                    self.scripts() +
                    self.images() +
                    self.audios() +
                    self.videos()
                )
            ),
        }