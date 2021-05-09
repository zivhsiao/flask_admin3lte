# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User, Question, QuestionType

from app.base.util import verify_pass

import json

@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'accounts/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Email already registered', 
                                    success=False,
                                    form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template( 'accounts/register.html', 
                                msg='User created please <a href="/login">login</a>', 
                                success=True,
                                form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

## question type
@blueprint.route('/question-type-edit')
def question_type_edit():
    if not current_user.is_authenticated:
        return redirect('/login')
    question_types = QuestionType.query.all()
    return render_template('question/question-type-edit.html', question_types=question_types, segment='question-type-edit')

@blueprint.route('/delete-type',  methods=["POST", "GET"])
def delete_type():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    question_id = request.form.get('id')
    query = QuestionType.query.filter_by(id = question_id).first()
    db.session.delete(query)
    db.session.commit()
    return '', 200  

@blueprint.route('/update-type',  methods=["POST", "GET"])
def update_type():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    question_id = request.form.get('id')
    query = QuestionType.query.filter_by(id = question_id).first()
   
    return jsonify({"id": f"{query.id}", 
                    "type_name":f"{query.type_name}"
                    })

@blueprint.route('/update-type-action',  methods=["POST", "GET"])
def update_type_action():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    question_id = request.form.get('id')
    type_name = request.form.get('type_name')
    if question_id == '':
        # 新增資料
        q = QuestionType(type_name = type_name)
        db.session.add(q)             
        db.session.commit()
        
    else:
        # 更新資料    
        q = QuestionType.query.filter_by(id = question_id).first()
        q.type_name = type_name
        db.session.commit()
    
    return redirect('/question-type-edit')

# question
@blueprint.route('/delete-question',  methods=["POST", "GET"])
def delete_question():
    if not current_user.is_authenticated:
        return 'Forbidden', 403    
    question_id = request.form.get('id')
    query = Question.query.filter_by(id = question_id).first()
    db.session.delete(query)
    db.session.commit()
    return '', 200  

@blueprint.route('/update-question',  methods=["POST", "GET"])
def update_question():
    if not current_user.is_authenticated:
        return 'Forbidden', 403    
    question_id = request.form.get('id')
    query = Question.query.filter_by(id = question_id).first()
   
    return jsonify({"id": f"{query.id}", 
                    "question_type":f"{query.question_type}", 
                    "question": f"{query.question}",
                    "answer": f"{query.answer}",
                    "keyword": f"{query.keyword}"
                    })

@blueprint.route('/update-question-action',  methods=["POST", "GET"])
def update_question_action():
    if not current_user.is_authenticated:
        return 'Forbidden', 403    
    question_id = request.form.get('id')
    question_type = request.form.get('question_type')
    question = request.form.get('question')
    answer = request.form.get('answer')
    keyword = request.form.get('keyword')
    if question_id == '':
        # 新增資料
        q = Question(question_type = question_type,
                     question = question,
                     answer = answer,
                     keyword = keyword
                    )
        db.session.add(q)             
        db.session.commit()
        
    else:
        # 更新資料    
        q = Question.query.filter_by(id = question_id).first()
        q.question_type = question_type
        q.question = question
        q.answer = answer
        q.keyword = keyword
        db.session.commit()
    
    return redirect('/qna-edit')

# question
@blueprint.route('/qna-edit')
def question_edit():
    if not current_user.is_authenticated:
        return redirect('/login')
    questions = db.session.query(Question, QuestionType).filter(Question.question_type == QuestionType.id).order_by(Question.id.desc()).all()
    question_type = QuestionType.query.all()    
    return render_template('question/qna-edit.html', 
        questions = questions,
        question_type = question_type,  
        segment='qna-edit'
    )


## Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
