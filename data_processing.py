import sqlite3
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

#tree = ET.parse('./askubuntu.com/Posts.xml')
#root = tree.getroot()

connection = sqlite3.connect('askubuntu_unixstack.db')
cur = connection.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS dataset(id TEXT PRIMARY KEY, question TEXT UNIQUE, answer TEXT, answer_score INT)")


def insert_question(row):
    pid=row.get('Id')
    body=row.get('Body')
    body = BeautifulSoup(body, "html.parser").get_text().replace("\n", " ").replace('"', "'")
    cur.execute('SELECT id FROM DATASET WHERE id ="{}"'.format(pid))
    q_exist=cur.fetchone()
    if(q_exist==None):
        try:
            cur.execute('INSERT INTO dataset(id, question, answer_score) VALUES ("{}","{}","{}");'.format(pid, body, -100))
        except:
            print("A duplicate question found, skipping it.")
    else:
        try:
            cur.execute('UPDATE dataset SET question = "{}" WHERE id = "{}";'.format(body, pid))
        except:
            cur.execute('UPDATE dataset SET question = "{}" WHERE id = "{}";'.format(" "+body, pid))

def update_answer(row):
    pid=row.get('ParentId')
    cur.execute('SELECT answer_score FROM DATASET WHERE id ="{}";'.format(pid))
    score = cur.fetchone()
    if(score == None):
        body=row.get('Body')
        body = BeautifulSoup(body, "html.parser").get_text().replace("\n", " ").replace('"', "'")
        cur.execute('INSERT INTO dataset(id, answer, answer_score) VALUES ("{}","{}","{}");'.format(pid, body, -100))
    else:
        score = score[0]
        if(score<int(row.get('Score'))):
            body=row.get('Body')
            body = BeautifulSoup(body, "html.parser").get_text().replace("\n", " ").replace('"', "'")
            score = int(row.get('Score'))
            cur.execute('UPDATE dataset SET answer = "{}", answer_score = "{}" WHERE id = "{}";'.format(body, score, pid))
    

######MAIN

for data_file in ['./askubuntu.com/Posts.xml', './unix.stackexchange.com/Posts.xml']:
    i=0
    fh = open(data_file, 'r', buffering=1000)
    for _ in range(2):
        next(fh)

    for line in fh:
        i+=1
        try:
            row=ET.fromstring(line)
        except:
            print("unable to parse a line, skipping it")
        if(row.get('PostTypeId')=='1' and row.get('AnswerCount')!='0'):
            insert_question(row)
        elif(row.get('PostTypeId')=='2'):
            update_answer(row)
        if(i%10000==0):
            connection.commit()
            print("went through {} entries".format(i))


cur.execute('SELECT COUNT(*) FROM dataset WHERE question IS NULL;') #THIS CAN BE DONE FOR EACH COLUMN AND THIS WAY IT WAS FOUND THAT QUESTION COLUMN HAD 111 NULL VALUES
print("There are",cur.fetchone()[0], "missing values.")

#DELETING ROWS WITH NULL VALUES IN QUESTION COLUMN:
cur.execute('DELETE FROM dataset WHERE question IS NULL;')
connection.commit()

connection.commit()
connection.close()
fh.close()
        
        
