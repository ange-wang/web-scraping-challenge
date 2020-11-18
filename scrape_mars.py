from splinter import Browser
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import time


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    # Visit NASA to get feature news
    nasa_url = "https://mars.nasa.gov/news/"
    browser.visit(nasa_url)

    news_html = browser.html
    soup = bs(news_html, "lxml")

    news = soup.find(class_="slide")

    news_title = news.find(class_="content_title").find('a').text
    news_p = news.find(class_="rollover_description_inner").text

    time.sleep(1)
    
    # Get URL of featured image
    feat_img_site = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(feat_img_site)

    feat_img_html = browser.html
    soup = bs(feat_img_html, 'lxml')

    feat_image = soup.find(class_='carousel_items').find('article')['style']
    link = re.search("'(.*)'", feat_image)
    feat_img_url = "https://jpl.nasa.gov" + link.group(1)

    # Mars facts table
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    df = tables[0]
    df = df.rename(columns={0:'Description', 1: 'Value'})

    html_table = df.to_html(index=False)

    # Hemisphere Images
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)
    html = browser.html
    soup = bs(html, 'html.parser')

    products = soup.find_all(class_='item')

    image_list = []
    large_image_list = []
    heading_list = []

    for product in products:
        image_link = product.find(class_='description').\
            find('a', class_='itemLink product-item')['href']
        heading = product.find(class_='description').find('h3').text
        image_list.append(image_link)
        heading_list.append(heading)
        
    image_url_list = ['https://astrogeology.usgs.gov/' + url for url in image_list]

    for image_url in image_url_list:
        try:
            browser.visit(image_url)
            html = browser.html
            soup = bs(html, 'html.parser')
            
            large_image = soup.find('img', class_='wide-image')['src']
            large_image_url = 'https://astrogeology.usgs.gov/' + large_image
            large_image_list.append(large_image_url)
        except:
            print('error')
    
    result_dict = [{'title': a,'img_url': b} for a, b in zip(heading_list,large_image_list)]
    
    mars_data = {
        'news_title': news_title,
        'news_p': news_p,
        'feat_img_url': feat_img_url,
        'html_table': html_table,
        'hemi_img': result_dict
    }

    browser.quit()

    # Return results
    return mars_data