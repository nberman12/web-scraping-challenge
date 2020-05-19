#import dependencies
from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import requests
import time
import re


def scrape():
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    
    mars_data={}

    #Nasa Mars Site
    nasa_url='https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(nasa_url)
    nasa_html=browser.html
    nasa_soup=BeautifulSoup(nasa_html,'html.parser')

    #Find latest article w. Title and paragraph
    slide=nasa_soup.find('li',class_='slide')
    result=slide.find_all('div', class_="content_title")

    news_title=result[0].get_text()

    news_p=nasa_soup.find('div',class_='article_teaser_body').text


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
    
    browser.visit(mars_hemisphere_url)
    hemi_soup=BeautifulSoup(browser.html,"html.parser")

    links=hemi_soup.find_all('h3')

    hemisphere_img_urls=[]

    for i in range(len(links)):
        hemi_dict ={}
        browser.find_by_tag('h3')[i].click()
        time.sleep(1)
        soup = BeautifulSoup(browser.html, 'html.parser')
        initial =soup.find('h2', class_='title')
        title = initial.text
        hemi_dict['title'] = title
        img_url = soup.select_one('img.wide-image').get('src')
        hemi_dict['img_url'] = img_url
        browser.back()
        time.sleep(1)
        hemisphere_img_urls.append(hemi_dict)

    mars_data['hemisphere_imgs']=hemisphere_img_urls


    browser.quit()

    return mars_data

if __name__ == "__main__":
    print(scrape())
