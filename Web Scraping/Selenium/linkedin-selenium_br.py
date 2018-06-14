from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
import time
import sqlite3

__author__ = 'Wuqing Li'
__date__ = '2017-04-19'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# create DB
db = sqlite3.connect('sqlite3_wuli_linkedin.db')
db.execute('drop table if exists linkedin_br')
db.execute('create table linkedin_br '
           '(JobTitle text, CompName text, Location text, Desc text, postedTime text, ctime text)')


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load chrome.exe
chrome = webdriver.Chrome(r'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\chromedriver.exe')
chrome.set_window_size(1024, 768)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# login
chrome.get('https://www.linkedin.com/')
time.sleep(5)

username = chrome.find_element_by_css_selector("input[id='login-email']")
username.clear()
# input your LinkedIn account name[email_address]
username.send_keys('lwq07010328@163.com')
time.sleep(2)

password = chrome.find_element_by_css_selector("input[id='login-password']")
password.clear()
# your account password
password.send_keys('xxx')
time.sleep(2)

chrome.find_element_by_css_selector('input[id="login-submit"]').click()
time.sleep(3)

# go to job search tab
# chrome.find_element_by_css_selector('span[id="jobs-tab-icon"]').click()
# time.sleep(5)

chrome.get('https://www.linkedin.com/jobs/')
time.sleep(5)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
city_state = ['São Paulo Area, Brazil', 'São Paulo, São Paulo, Brazil', 'Guarulhos, São Paulo, Brazil',
              'Barueri, São Paulo, Brazil', 'Valinhos, São Paulo, Brazil', 'Indaiatuba, São Paulo, Brazil',
              'Rio de Janeiro, Rio de Janeiro, Brazil','Belo Horizonte, Minas Gerais, Brazil', 'Goiânia, Goiás, Brazil',
              'Campinas, São Paulo, Brazil',
              ]

for city in city_state:
    citySearch = chrome.find_element_by_css_selector('input[placeholder="City, state, postal code or country"]')
    citySearch.clear()
    citySearch.send_keys(city)
    time.sleep(2)

    citySearch.send_keys(Keys.ENTER)
    # chrome.find_element_by_css_selector('button[class="submit-button button-secondary-large"]').click()

    chrome.execute_script("window.scrollTo(0, 1000);")
    time.sleep(5)

    # past month
    # date_posted = chrome.find_element_by_css_selector('button["aria-controls="date-posted-facet-values"]')
    # An invalid or illegal selector was specified
    # date_posted.find_element_by_css_selector('h3').click()
    for h3 in chrome.find_elements_by_css_selector('h3[class="search-s-facet__name Sans-15px-black-85%-semibold"]'):
        if h3.text == 'Date Posted':
            h3.click()
    time.sleep(2)

    for li in chrome.find_elements_by_css_selector('span[class="search-s-facet-value__name Sans-15px-black-70%"]'):
        if li.text == 'Past Month':
            li.click()
    time.sleep(10)

    print('Searching city: {}   '.format(city),
          time.ctime(),
          chrome.find_element_by_css_selector('div[class="jobs-search-results__count-string results-count-string'
                                              ' Sans-15px-black-55% pb0 ph4"]').text,
          end='\n')

    # scraping each page
    while True:
        for i in range(1000, 5000, 1000):
            chrome.execute_script("window.scrollTo(0, {});".format(i))
            time.sleep(1)
        chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)

        divs = chrome.find_elements_by_css_selector('div[class="occludable-update card-list__item job-card'
                                                    ' job-card--column ember-view"]')

        for div in divs:
            title = div.find_element_by_css_selector('h3[class="job-card__title ember-view"]').text
            company = div.find_element_by_css_selector('h4[class="job-card__company-name"]').text
            location = div.find_element_by_css_selector('h5[class="job-card__location"]').text[13:]

            '''
            l_s = location.split(', ')
            if len(l_s) == 3:
                city, state, country = l_s
            elif len(l_s) == 2:
                city, state = l_s
            else:
                city = l_s
                state = None
            '''

            description = div.find_element_by_css_selector('p[class="job-card__description-snippet"]').text
            postedTime = div.find_element_by_css_selector('p[class="job-card__listed-status"]').text

            # print(title, company, location, description, postedTime, sep=' | ', end='\n')

            db.execute('insert into linkedin_br (JobTitle, CompName, Location, Desc, postedTime, ctime) '
                       'values (?, ?, ?, ?, ?, ?)',
                       (title, company, location, description, postedTime, time.strftime("%Y-%m-%d")))
            db.commit()

        # break out when all pages are scraped.
        try:
            Next = chrome.find_element_by_css_selector('button[class="next"]')
            Next.click()
        # less than 1000 jos postings
        except exceptions.NoSuchElementException as e:
            # print('Go to next city!', e)
            break
        # can't show 1000+ jobs postings

        time.sleep(5)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
chrome.quit()   # close browser and chromedriver.exe
chrome.close()  # only close browser
