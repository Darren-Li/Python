import requests
import sqlite3
import time
from tqdm import tqdm


"""import list data to DB"""

# create DB and tables
db_filename = 'sqlite3_Kaggle.db'
db = sqlite3.connect(db_filename)
table = 'Kaggle_kernels3'

db.execute('DROP TABLE IF EXISTS {}'.format(table))
db.execute('''CREATE TABLE {} (title text, userName text, aceLanguageName text, languageName text, isNotebook text,
 isFork text, totalComments text, totalForks text, totalScripts text, totalViews text, totalVotes text,
 isRunning text, isDeleted text, scriptVersionDateCreated text, scriptUrl text)'''.format(table))


def get_post(url):
    i = 1
    while True:
        try:
            resp = requests.get(url, timeout=30)
            r_json = resp.json()
        except requests.exceptions.ConnectionError as e:
            print(e)
            time.sleep(5)
        except requests.exceptions.ReadTimeout as e:
            print(e)
            time.sleep(5)
        i += 1
        if i > 10:
            break

    data = []
    for post in r_json:
        title = post.get('title')
        userName = post.get('author').get('userName')
        aceLanguageName = post.get('aceLanguageName')
        languageName = post.get('languageName')
        isNotebook = post.get('isNotebook')
        isFork = post.get('isFork')
        totalComments = post.get('totalComments')
        totalForks = post.get('totalForks')
        totalScripts = post.get('totalScripts')
        totalViews = post.get('totalViews')
        totalVotes = post.get('totalVotes')
        isRunning = post.get('isRunning')
        isDeleted = post.get('isDeleted')
        scriptVersionDateCreated = post.get('scriptVersionDateCreated')
        scriptUrl = 'https://www.kaggle.com' + post.get('scriptUrl')
        after = post.get('id')

        data.append([title, userName, aceLanguageName, languageName, isNotebook, isFork,
                     totalComments, totalForks, totalScripts, totalViews, totalVotes,
                     isRunning, isDeleted, scriptVersionDateCreated, scriptUrl])

    db.executemany('''INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''.format(table), data)
    db.commit()

    return after


after_tmp = None
for page in tqdm(range(0, 1000)):
    if page == 0:
        url = 'https://www.kaggle.com/kernels.json?sortBy=dateCreated&group=everyone&pageSize=20'
        after = get_post(url)
    else:
        if after_tmp == after:
            print('No new data')
            break
        after_tmp = after

        url = 'https://www.kaggle.com/kernels.json?sortBy=dateCreated&group=everyone&pageSize=20&after={}'.format(after)
        after = get_post(url)
