# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt



def scrape_all():

    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_p = mars_news(browser)

    


    data = {'news_title': news_title,
            'news_p':news_p,
            'featured_image':featured_image(browser),
            'facts':mars_facts(),
            'last_modified':dt.datetime.now(),
            'hemispheres':hemispheres(browser)
            }



    browser.quit()
    return data



def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')

        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        news_p = slide_elem.find('div',class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None,None        

    return news_title, news_p

### Featured Images

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:

        # Find relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    
    df.columns = ['description','Mars','Earth']
    df.set_index('description',inplace=True)


    return df.to_html(classes="table table-striped")

def hemispheres(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    html = browser.html
    home_soup = soup(html, 'html.parser')

    hemisphere_image_urls = []
    results = home_soup.find_all('div',class_='description')

    for result in results:

        img_url = result.find('a',class_='itemLink product-item').get('href')

        full_image_url = f'{url}{img_url}'
            
        browser.visit(full_image_url)

        html = browser.html
        full_image_soup = soup(html, 'html.parser')

        url_piece_div = full_image_soup.find('div',class_='downloads')
        url_piece = url_piece_div.find('a').get('href')

        full_jpeg_url = f'{url}{url_piece}'

        title = full_image_soup.find('h2',class_='title').text

        image_dict = {'img_url':full_jpeg_url,'title':title}

        hemisphere_image_urls.append(image_dict)

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())