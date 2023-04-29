from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from .. import db
from pybo.models import Question
from pybo.forms import QuestionForm, AnswerForm
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')

@bp.route('/list/')
def _list(): # list는 파이썬 내장 함수이므로 함수명을 _list로 정의
    page = request.args.get('page', type=int, default=1)
    question_list = Question.query.order_by(Question.create_date.desc())
    question_list = question_list.paginate(page=page, per_page=10) # 10개씩 보여주기

    return render_template('question/question_list.html', question_list=question_list)

@bp.route('/detail/<int:question_id>/') # Url mapping rule
def detail(question_id):
    question = Question.query.get_or_404(question_id)
    form = AnswerForm()
    return render_template('question/question_detail.html', question=question, form=form)                                                                                  

@bp.route('/create/', methods = ('GET','POST'))
@login_required
def create():
    form = QuestionForm()

    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index')) # POST(질문 등록) 방식에는 데이터베이스 처리
    
    return render_template('question/question_form.html', form=form)

@bp.route('/modify/<int:question_id>', methods=('GET','POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)

    if g.user != question.user:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=question_id))
    
    if request.method == 'POST':
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question) # form에서 받은 데이터를 question 객체에 적용
            question.modify_date = datetime.now() # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
        
    else: # GET 방식일 때
        form = QuestionForm(obj=question)

    return render_template('question/question_form.html', form=form) # GET 방식일 때는 question 객체를 form에 적용하여 전달

@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))

# 질문 추천 라우팅 함수
@bp.route('/like/<int:question_id>/')
@login_required
def like(question_id):
    _question = Question.query.get_or_404(question_id)
    # 본인 글 추천 불가
    if g.user == _question.user:
        flash('본인 글은 추천할 수 없습니다.')
    # 추천한 적이 있으면 추천 취소
    elif g.user in _question.voter:
        _question.voter.remove(g.user)
        db.session.commit()
    else:
        _question.voter.append(g.user)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))
