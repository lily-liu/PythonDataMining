import testing_1

SQLALCHEMY_DATABASE_URI = 'oracle://linkwoodorcl:linkwoodorcl@mwn-jkt.kana.com:1521/XE'
SQLALCHEMY_BINDS = {
    'main':'oracle://linkwoodorcl:linkwoodorcl@mwn-jkt.kana.com:1521/XE',
    'mailconfig':'oracle://linkwoodorcl_mailconfig:linkwoodorcl_mailconfig@mwn-jkt.kana.com:1521/XE'
}
MONGO_DBNAME = 'emails'
JOBS = [
    {
        'id': 'job1',
        'func': 'config:db_jobs',
        'trigger': 'interval',
        'minutes': 2
    }
]
SCHEDULER_API_ENABLED = True

def db_jobs():
    with testing_1.app.app_context():
        try:
            testing_1.init_db()
        except Exception:
            pass