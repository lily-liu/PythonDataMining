from __future__ import print_function, division

import json
import os
import threading

import maya
import requests
from flask import Flask, jsonify
from flask_apscheduler import APScheduler
from flask_json import FlaskJSON
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from nltk import WordNetLemmatizer, word_tokenize, Counter
from nltk.corpus import stopwords
from sqlalchemy.orm import scoped_session, sessionmaker
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import models

stoplist = stopwords.words('english')

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
DBSession = scoped_session(sessionmaker())
mongo = PyMongo(app)
flask_json = FlaskJSON(app)
scheduler = APScheduler()
scheduler.init_app(app)


@app.route('/')
def init_db():
    datas = process_data(get_mail_db())
    insert_to_sql(datas)
    mongo_ids = dump_to_mongo(datas)
    print(str(maya.now().datetime(to_timezone='Asia/Jakarta')) + ' - ' + str(mongo_ids))
    return str(mongo_ids)


def get_mail_db():
    table_1_data = models.Mailbox.query.all()
    mailbox_data = {datas.uuid: datas.name for datas in table_1_data}

    mail_data = models.ChannEmail.query.filter_by(is_inbound='Y').filter(
        models.ChannEmail.sent_date >= maya.when('2 minutes ago').datetime(to_timezone='Asia/Jakarta')).all()
    mail_ids = [mail.id for mail in mail_data]
    mail_contents = []
    for mail in mail_data:
        mail_contents.append({'id': mail.id, 'content': mail.body})

    mail_address_data = models.ChannEmailAddress.query.filter(models.ChannEmailAddress.id.in_(mail_ids)).filter_by(
        type='from').all()
    mail_address = {address.id: address.email_address for address in mail_address_data}

    mail_db_category = models.ChannCategory.query.filter_by(is_active='Y').filter().all()
    mail_db_category_ref = {category.name: {'CATEGORY_ID': category.id, 'CATEGORY_ENV_ID': category.env_id,
                                            'CATEGORY_TENANT_ID': category.tenant_id} for category in mail_db_category}

    mails_array = {'mailbox_data': mailbox_data, 'mail_data': mail_data, 'mail_address': mail_address,
                   'mail_category_ref': mail_db_category_ref}
    return mails_array


def process_data(mail_data):
    inserts = []
    for mail in mail_data['mail_data']:

        sentiment_values = analyze_sentiment(mail.body)
        category = parse_json_res(send_request({'id': int(mail.id), 'content': mail.body}))
        del category['id']
        if sentiment_values['compound'] >= 0.5:
            sentiment = 'positive'
        elif sentiment_values['compound'] < -0.5:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        dict = {'id': mail.id, 'date': mail.sent_date, 'subject': mail.subject, 'content': mail.body,
                'sender_email': mail_data['mail_address'][mail.id],
                'mailbox_target': mail_data['mailbox_data'][mail.gateway_id], 'sentiments_values': sentiment_values,
                'sentiment': sentiment, 'category': category,
                'ref_id': mail_data['mail_category_ref'][category['category']]}
        inserts.append(dict)

    return inserts


def dump_to_mongo(inserts_list):
    if not inserts_list:
        obj_id = None
    else:
        obj_id = mongo.db.mail_dumps.insert(inserts_list)
    return str(obj_id)


def insert_to_sql(inserts_dict):
    for inserts in inserts_dict:
        data = models.ChannEmailCategory(
            int(inserts['id']),
            int(inserts['ref_id']['CATEGORY_ENV_ID']),
            int(inserts['ref_id']['CATEGORY_ID']),
            inserts['ref_id']['CATEGORY_TENANT_ID'])
        db.session.add(data)
        db.session.flush()
    db.session.commit()
    return 'done'


def analyze_sentiment(sentence):
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(sentence)


def init_lists(folder):
    a_list = []
    file_list = os.listdir(folder)
    for a_file in file_list:
        f = open(folder + a_file, 'r')
        a_list.append(f.read())
    f.close()
    return a_list


def preprocess(sentence):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(unicode(sentence, errors='ignore'))]


def get_features(text, setting):
    if setting == 'bow':
        return {word: count for word, count in Counter(preprocess(text)).items() if not word in stoplist}
    else:
        return {word: True for word in preprocess(text) if not word in stoplist}


def send_request(content):
    content_data = json.dumps(content)
    url = 'http://10.80.32.98:8080/classifies'
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=content_data, headers=headers)
    return r


def parse_json_res(rez):
    data = rez.json()
    return data


@app.route('/run_post')
def run_json_test():
    return jsonify(maya.when('2 minutes ago',timezone='Asia/Jakarta').timezone())
    # return parse_json_res(send_request())

def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                r = requests.get('http://127.0.0.1:5000/')
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            maya.time.sleep(2)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


if __name__ == '__main__':
    scheduler.start()
    start_runner()
    app.run()
