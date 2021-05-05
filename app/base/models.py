# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String

from datetime import datetime, date, timedelta, timezone

from app import db, login_manager

from app.base.util import hash_pass

class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

class QuestionType(db.Model):
    __tablename__ = 'question_type'

    id = Column(Integer, primary_key=True)
    type_name = Column(String, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  

    def __init__(self, type_name):
        self.type_name = type_name

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.String(255)) 
    question = db.Column(db.String(255))
    answer = db.Column(db.Text(65536))
    keyword = db.Column(db.Text(65536))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)    

    def __init__(self, question_type, question, answer, keyword):
        self.question_type = question_type
        self.question = question
        self.answer = answer    
        self.keyword = keyword


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None
