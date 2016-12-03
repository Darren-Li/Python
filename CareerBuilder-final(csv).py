#!/usr/bin/python3
# coding: utf-8

from bs4 import BeautifulSoup
import requests
import time
import os

print('''
    ***********************************************************************
    Python practice 001 -- scrap data form http://www.careerbuilder.com/
        The 1st version - Wuqing Li, 2016/10/28
        The 2nd version - Wuqing Li, 2016/11/10
    ***********************************************************************
    '''
    )

# extract the link of 'view active jobs' and then enter the web and extract more detailed information,
# finally store data in csv file
def get_attractions(url, data=None):
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    links = soup.select('div[class="thirdBlock"] > a')

    print('Current time is: ', time.ctime())
    # print current page number
    for pg in soup.select('#SearchPagination > span[class="current"]'):
        current_pg = pg.get_text().strip()
        print('Current page number is: ', current_pg)
    # print total pages
    if int(current_pg) == 1:
        for pg in soup.select('#SearchPagination > a.lastpage'):
            total_pg = pg.get_text().strip()
            print('The number of total pages is: ', total_pg)
    else:
        pass

    active_jobs_links = list()
    for link in links:
        active_jobs_links.append(link.get('href'))
    
    for i in range(0, len(active_jobs_links)):
        get_details(active_jobs_links[i])
    # time.sleep(1)

# enter more detail web and get data, especially, active jobs
def get_details(url, data=None):
    wb_data=requests.get(url)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    # to fix the problem of '&nbsp'
    for t in soup.find_all(text=True):
        newtext = t.replace("\xa0", ' ')
        t.replace_with(newtext)

    # company name
    if soup.select('a[id="hrefcompanyname"]')==[]:
        compName = None
    else:
        for company in soup.select('a[id="hrefcompanyname"]'):
            compName = company.get_text().strip(' *\n')
    # print('company name: ', compName)

    # company type
    if soup.select('span[class="CompanyType"]')==[]:
        compType = None
    else:
        for string in soup.select('span[class="CompanyType"]'):
            if string.get_text() is None:
                compType = None
            elif string.get_text().strip() == '':
                compType = None
            else:
                compType = string.get_text().strip('() \n')
    # print('company type: ', compType)

    # company industry
    if soup.select('div[class="CompanyIndustry"]')==[]:
        compIndustry = None
    else:
        for string in soup.select('div[class="CompanyIndustry"]'):
            if string.strong.get_text() == '':
                compIndustry = None
            else:
                compIndustry = string.strong.get_text().strip(', \n')
    # print('company industry: ', compIndustry)

    # company active jobs
    if soup.select('span[id="spnActiveJobCount"]')==[]:
        compActiveJobs = None
    else:
        for count in soup.select('span[id="spnActiveJobCount"]'):
            if count.get_text() == '':
                compActiveJobs = None
            else:
                compActiveJobs = count.get_text().strip(' \n')
    # print('active jobs: ', compActiveJobs)

    # company href
    if soup.select('a[id="hlWebsite"]') ==[]:
        compHomePage = None
    else:
        for link in soup.select('a[id="hlWebsite"]'):
            compHomePage = link.get('href')
    # print('compHomePage link: ', compHomePage)

    # company address
    if len(soup.select('#headercontent > div > p > span[style="color:#c0c0c0"]')) == 3:
        for string in soup.select('#headercontent > div > p'):
            if string.find('span').previous_sibling is None:
                compAddress = None
            elif string.find('span').previous_sibling.strip() == '':
                compAddress = None
            else:
                compAddress = string.find('span').previous_sibling.strip(' \n')
    else:
        compAddress = None
    # print('address: ', compAddress)

    # company employees
    if soup.select('#headercontent > div > p')==[]:
        compEmployees = None
    for string in soup.select('#headercontent > div > p'):
        if string.find(text=' employees') is None:
            compEmployees = None
        elif string.find(text=' employees').previous_sibling.get_text() is None:
            compEmployees = None
        else:
            compEmployees = string.find(text=' employees').previous_sibling.get_text().strip(' \n')
    # print('employees: ', compEmployees)

    if compName is None or str(compActiveJobs) == '0':
        pass
    else:
        fo.write('"'+str(compName)+'","'+str(url)+'","'+str(compType)+'","'+str(compIndustry)+'","'+str(compAddress)+'","'+str(compEmployees)+'","'+str(compActiveJobs)+'","'+str(compHomePage)+'"'+'\n')


#############################################################################################################################################################
print('The program start running at: ', time.ctime())
t_begin = time.time()

print('There are 25 companies on each page except for the last one.', end='\n')
start_pg = int(input('Enter start page number[should be an integer (default value: 1)]: '))
end_pg   = int(input('Enter end page number[should be an integer (default value: 236)]: '))

# urls = ['http://www.careerbuilder.com/employerprofile/companysearch.aspx?pg={}'.format(str(i)) for i in range(start_pg, end_pg + 1)]
urls = ['http://www.careerbuilder.com/jobs/company/?jmn=1&pg={}&jmx=99999'.format(str(i)) for i in range(start_pg, end_pg +1)]

filename = 'C:\Darren\ziqing\Merkle\Python\Web Scraping with Python\CareerBuilder\CareerBuilder_AvtiveJobs.csv'
new = input('If {} exists, do you want to keep it or delete it [keep,delete]'.format(filename))

if os.path.exists(filename) and new == 'delete':
    os.remove(filename)
    print('file {} is deleted!'.format(filename))
else:
    pass

fo = open(filename, 'a', encoding='utf-8')

if new == 'keep':
    pass
else:
    fo.write('compName,activeJobsLink,compType,compIndustry,compAddress,compEmployees,compActiveJobs,compHomePage\n')

if (end_pg-start_pg+1) < 50:
    for single_url in urls[0: (end_pg-start_pg)+1]:
        get_attractions(single_url)
else:
    for i in range(0, (end_pg-start_pg+1)//50):
        for single_url in urls[50 * i: 50 * (i + 1)]:
            get_attractions(single_url)
        time.sleep(5)
        print("The {}-th 1,250 companies' data extraction is completed at:".format(i+1), time.ctime(), '\n')

    if ((end_pg-start_pg+1)) % 50 == 0:
        pass
    else:
        for single_url in urls[50 * ((end_pg-start_pg+1)//50): (end_pg-start_pg)+1]:
            get_attractions(single_url)

fo.close()

t_end = time.time()
print('The program finish executing at:', time.ctime())
print('This program totally used:', (t_end - t_begin)/60, 'Minutes')
