import requests
from lxml import html
from bs4 import BeautifulSoup
import getpass


USERNAME = 'lwq07010328@163.com'
# USERNAME = input("Please input your E-mail address: ")
PASSWORD = getpass.getpass("Please input the password: ")

LOGIN_URL = "https://bitbucket.org/account/signin/?next=/"
URL = "https://bitbucket.org/dashboard/repositories"


def main():
    # create session
    session_requests = requests.session()

    # Get login csrf token
    result = session_requests.get(LOGIN_URL)

    # lxml.html, xpath
    # tree = html.fromstring(result.text)
    # authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

    # BeautifulSoup, css selector
    soup = BeautifulSoup(result.text, 'lxml')
    authenticity_token = soup.select('input[name="csrfmiddlewaretoken"]')[0].get('value')

    # Create payload
    payload = {"username": USERNAME,
               "password": PASSWORD,
               "csrfmiddlewaretoken": authenticity_token
    }

    # Perform login
    session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))

    # Scrape url
    result = session_requests.get(URL, headers=dict(referer=URL))
    tree = html.fromstring(result.content)
    repositories = tree.xpath("//div[@class='repo-list--repo']/a/text()")
    projects = tree.xpath("//div[@class='repo-list--project']/a/text()")
    owners = tree.xpath("//div[@class='repo-list--owner']/a/text()")
    last_updated = tree.xpath("//td[@class='repo-list--updated-column']/time/text()")
    # print(repositories, projects, owners, last_updated)

    for repository, project, owner, last_updated in zip(repositories, projects, owners, last_updated):
        data = {
            'repository': repository,
            'project': project,
            'owner': owner,
            'last_updated': last_updated.strip(' \n')
        }
        print(data)

if __name__ == '__main__':
    main()
