from datetime import datetime

from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect

from pybo import db
from pybo.forms import CommentForm
from pybo.models import Question, Answer, Comment
from pybo.views.auth_views import login_required
import random

bp = Blueprint('comment', __name__, url_prefix='/comment')

# 질문 댓글 기능
@bp.route('/create/question/<int:question_id>', methods=('POST','GET'))
# @login_required
def create_question(question_id):
    form = CommentForm()
    question = Question.query.get_or_404(question_id)
    get_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if request.method == 'POST' and form.validate_on_submit():
        if g.user:   
            comment = Comment(user=g.user, content=form.content.data, create_date=datetime.now(), question=question, ip=get_ip)
        elif not g.user:
            comment = Comment(ip=get_ip, content=form.content.data, create_date=datetime.now(), question=question)
        
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('question.detail', question_id=question_id))
    return render_template('comment/comment_form.html', form=form)

@bp.route('/modify/question/<int:comment_id>')
@login_required
def modify_question(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if g.user != comment.user:
        flash('수정권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=comment.question.id))
    if request.method == 'POST':
        form = CommentForm()
        if form.validate_on_submit():
            form.populate_obj(comment)
            comment.modify_date = datetime.now()
            db.session.commit()
            return redirect(url_for('question.detail', question_id=comment.question.id))
    else:
        form = CommentForm(obj=comment)
    return render_template('comment/comment_form.html', form=form)

@bp.route('/delete/question/<int:comment_id>')
@login_required
def delete_question(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    question = Question.query.get_or_404(comment.question.id)
    if g.user != comment.user and g.user != question.user: # 질문 작성자도 삭제 가능
        flash('삭제권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=comment.question.id))
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('question.detail', question_id=comment.question.id))

# 답변 댓글 기능
@bp.route('/create/answer/<int:answer_id>', methods=('POST','GET'))
# @login_required
def create_answer(answer_id):
    form = CommentForm()
    answer = Answer.query.get_or_404(answer_id)
    get_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if request.method == 'POST' and form.validate_on_submit():
        if g.user:   
            comment = Comment(user=g.user, content=form.content.data, create_date=datetime.now(), answer=answer, ip=get_ip)
        elif not g.user:
            comment = Comment(ip=get_ip, content=form.content.data, create_date=datetime.now(), answer=answer)
        
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('question.detail', question_id=answer.question.id))
    return render_template('comment/comment_form.html', form=form)

@bp.route('/modify/answer/<int:comment_id>')
@login_required
def modify_answer(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if g.user != comment.user:
        flash('수정권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=comment.question.id))
    if request.method == 'POST':
        form = CommentForm()
        if form.validate_on_submit():
            form.populate_obj(comment)
            comment.modify_date = datetime.now()
            db.session.commit()
            return redirect(url_for('question.detail', question_id=comment.question.id))
    else:
        form = CommentForm(obj=comment)
    return render_template('comment/comment_form.html', form=form)

@bp.route('/delete/answer/<int:comment_id>')
@login_required
def delete_answer(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    answer = Answer.query.get_or_404(comment.answer.id)
    question = Question.query.get_or_404(answer.question.id)
    if g.user != comment.user and g.user != answer.user and g.user != question.user:
        flash('삭제권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=comment.question.id))
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('question.detail', question_id=comment.question.id))
