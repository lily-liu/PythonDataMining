from sqlalchemy.dialects.oracle import CLOB

from testing_1 import db

db.reflect()

class Mailbox(db.Model):
    __bind_key__ = 'mailconfig'
    __tablename__ = 'MAILBOX'
    uuid = db.Column(db.VARCHAR, primary_key=True)
    name = db.Column(db.VARCHAR)

class ChannEmail(db.Model):
    __bind_key__ = 'main'
    __tablename__ = 'CHANN_EMAIL'
    id = db.Column(db.INTEGER, primary_key=True)
    gateway_id = db.Column(db.VARCHAR)
    sent_date = db.Column(db.TIMESTAMP)
    subject = db.Column(db.VARCHAR)
    body = db.Column(CLOB)
    is_inbound = db.Column(db.CHAR)

class ChannEmailAddress(db.Model):
    __bind_key__ = 'main'
    __tablename__ = 'CHANN_EMAIL_ADDRESS'
    id = db.Column(db.INTEGER, primary_key=True)
    email_address = db.Column(db.VARCHAR)
    type = db.Column(db.VARCHAR)

class ChannCategory(db.Model):
    __bind_key__ = 'main'
    __tablename__ = 'CHANN_CATEGORY'
    id = db.Column(db.INTEGER, primary_key=True)
    env_id = db.Column(db.INTEGER)
    release_id = db.Column(db.INTEGER)
    name = db.Column(db.VARCHAR)
    is_active = db.Column(db.CHAR)
    tenant_id = db.Column(db.VARCHAR)

class ChannEmailCategory(db.Model):
    __bind_key__ = 'main'
    __tablename__ = 'CHANN_EMAIL__CATEGORY'
    email_id = db.Column(db.INTEGER, primary_key=True)
    category_env_id = db.Column(db.INTEGER)
    category_id = db.Column(db.INTEGER)
    tenant_id = db.Column(db.VARCHAR)

    def __init__(self, email_id, category_env_id, category_id, tenant_id):
        self.email_id = email_id
        self.category_env_id = category_env_id
        self.category_id = category_id
        self.tenant_id = tenant_id
