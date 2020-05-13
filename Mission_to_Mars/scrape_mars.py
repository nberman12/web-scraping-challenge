#import dependencies
from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import requests
import time
import re

def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser=init_browser()
    mars_data={}

    #Nasa Mars Site
    nasa_url='https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(nasa_url)
    nasa_html=browser.html
    nasa_soup=BeautifulSoup(nasa_html,'html.parser')

    news_list = nasa_soup.find('ul', class_='item_list')
    first_item = news_list.find('li', class_='slide')
    news_title = first_item.find('div', class_='content_title').text
    news_p = first_item.find('div', class_='article_teaser_body').text

    mars_data['nasa_headline']=news_title
    mars_data['nasa_teaser']=news_p

    
    #visit JPL and scrape featured image
    jpl_url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)
    time.sleep(1)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(1)
    expand=browser.find_by_css('a.fancybox-expand')
    expand.click()
    time.sleep(1)

    jpl_html=browser.html
    jpl_soup=BeautifulSoup(jpl_html,'html.parser')

    img_relative=jpl_soup.find('img',class_='fancybox-image')['src']
    image_path=f"https://www.jpl.nasa.gov{img_relative}"
    
    mars_data['feature_image_src']=image_path

    #Mars Weather via Twitter
    mars_weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(mars_weather_url)
    time.sleep(1)

    soup=BeautifulSoup(browser.html,'html.parser')

    mars_weather=soup.find_all(text=re.compile('InSight'))[0]
    mars_data['weather_summary']=mars_weather

    #Get Mars FActs
    tables=pd.read_html('https://space-facts.com/mars/')

    df= tables[0]
    df=df.rename(columns={0:'Describe',1:'Value'})

    mars_facts_html=[df.to_html(classes='data table table-borderless', index=False, header=False, border=0)]

    mars_data['fact_table']=mars_facts_html

    #Mars Hemispheres
    mars_hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hemi_dicts = []

    for i in range(1,9,2):
        hemi_dict = {}
        
        browser.visit(mars_hemisphere_url)
        time.sleep(1)
        hemispheres_html = browser.html
        hemispheres_soup = BeautifulSoup(hemispheres_html, 'html.parser')
        hemi_name_links = hemispheres_soup.find_all('a', class_='product-item')
        hemi_name = hemi_name_links[i].text.strip('Enhanced')
        
        detail_links = browser.find_by_css('a.product-item')
        detail_links[i].click()
        time.sleep(1)
        browser.find_link_by_text('Sample').first.click()
        time.sleep(1)
        browser.windows.current = browser.windows[-1]
        hemi_img_html = browser.html
        browser.windows.current = browser.windows[0]
        browser.windows[-1].close()
        
        hemi_img_soup = BeautifulSoup(hemi_img_html, 'html.parser')
        hemi_img_path = hemi_img_soup.find('img')['src']

        hemi_dict['title']=hemi_name.strip()
        hemi_dict['img_url']=hemi_img_path

        hemi_dicts.append(hemi_dict)
    
    mars_data['hemisphere_imgs']=hemi_dicts

    browser.quit()

    return mars_data
