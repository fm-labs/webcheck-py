from bs4 import BeautifulSoup
import json

from webcheck.util.content_helper import get_url_content


def social_tags_handler(url):
    # Check if url includes protocol
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    
    try:
        #response = requests.get(url)
        #html = response.text
        status_code, headers, content = get_url_content(url)
        html = content
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {}
        
        # Basic meta tags
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text()
        
        description_tag = soup.find('meta', attrs={'name': 'description'})
        if description_tag:
            metadata['description'] = description_tag.get('content')
        
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            metadata['keywords'] = keywords_tag.get('content')
        
        canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
        if canonical_tag:
            metadata['canonicalUrl'] = canonical_tag.get('href')

        # OpenGraph Protocol
        og_title_tag = soup.find('meta', attrs={'property': 'og:title'})
        if og_title_tag:
            metadata['ogTitle'] = og_title_tag.get('content')
        
        og_type_tag = soup.find('meta', attrs={'property': 'og:type'})
        if og_type_tag:
            metadata['ogType'] = og_type_tag.get('content')
        
        og_image_tag = soup.find('meta', attrs={'property': 'og:image'})
        if og_image_tag:
            metadata['ogImage'] = og_image_tag.get('content')
        
        og_url_tag = soup.find('meta', attrs={'property': 'og:url'})
        if og_url_tag:
            metadata['ogUrl'] = og_url_tag.get('content')
        
        og_description_tag = soup.find('meta', attrs={'property': 'og:description'})
        if og_description_tag:
            metadata['ogDescription'] = og_description_tag.get('content')
        
        og_site_name_tag = soup.find('meta', attrs={'property': 'og:site_name'})
        if og_site_name_tag:
            metadata['ogSiteName'] = og_site_name_tag.get('content')
        
        # Twitter Cards
        twitter_card_tag = soup.find('meta', attrs={'name': 'twitter:card'})
        if twitter_card_tag:
            metadata['twitterCard'] = twitter_card_tag.get('content')
        
        twitter_site_tag = soup.find('meta', attrs={'name': 'twitter:site'})
        if twitter_site_tag:
            metadata['twitterSite'] = twitter_site_tag.get('content')
        
        twitter_creator_tag = soup.find('meta', attrs={'name': 'twitter:creator'})
        if twitter_creator_tag:
            metadata['twitterCreator'] = twitter_creator_tag.get('content')
        
        twitter_title_tag = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title_tag:
            metadata['twitterTitle'] = twitter_title_tag.get('content')
        
        twitter_description_tag = soup.find('meta', attrs={'name': 'twitter:description'})
        if twitter_description_tag:
            metadata['twitterDescription'] = twitter_description_tag.get('content')
        
        twitter_image_tag = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image_tag:
            metadata['twitterImage'] = twitter_image_tag.get('content')

        # Misc
        theme_color_tag = soup.find('meta', attrs={'name': 'theme-color'})
        if theme_color_tag:
            metadata['themeColor'] = theme_color_tag.get('content')
        
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        if robots_tag:
            metadata['robots'] = robots_tag.get('content')
        
        googlebot_tag = soup.find('meta', attrs={'name': 'googlebot'})
        if googlebot_tag:
            metadata['googlebot'] = googlebot_tag.get('content')
        
        generator_tag = soup.find('meta', attrs={'name': 'generator'})
        if generator_tag:
            metadata['generator'] = generator_tag.get('content')
        
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_tag:
            metadata['viewport'] = viewport_tag.get('content')
        
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag:
            metadata['author'] = author_tag.get('content')
        
        publisher_tag = soup.find('link', attrs={'rel': 'publisher'})
        if publisher_tag:
            metadata['publisher'] = publisher_tag.get('href')
        
        favicon_tag = soup.find('link', attrs={'rel': 'icon'})
        if favicon_tag:
            metadata['favicon'] = favicon_tag.get('href')

        if len(metadata) == 0:
            return {'skipped': 'No metadata found'}
        
        return metadata
    
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed fetching data'})
        }

handler = social_tags_handler