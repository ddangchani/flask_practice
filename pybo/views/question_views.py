from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash, jsonify
from werkzeug.utils import redirect

from .. import db
from pybo.models import Question, Answer, User, answer_voter, question_voter
from pybo.forms import QuestionForm, AnswerForm, CommentForm
from pybo.views.auth_views import login_required
from sqlalchemy import func

bp = Blueprint('question', __name__, url_prefix='/question')

@bp.route('/list/')
def _list(): # list는 파이썬 내장 함수이므로 함수명을 _list로 정의
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    question_list = Question.query.order_by(Question.create_date.desc())
    # 검색 기능
    if kw:
        search = '%%{}%%'.format(kw) # %%는 %를 문자 자체로 인식하게 함
        # Subquery
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery() # 서브쿼리를 사용하여 답변 테이블과 사용자 테이블을 조인
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |
                    Question.content.ilike(search) | 
                    User.username.ilike(search) | 
                    sub_query.c.content.ilike(search) | 
                    sub_query.c.username.ilike(search) 
                    ) \
            .distinct() # 중복 제거

    question_list = question_list.paginate(page=page, per_page=10) # 10개씩 보여주기

    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw)

@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    # paginate answer
    question = Question.query.get_or_404(question_id)
    page = request.args.get('page', type=int, default=1)
    sort = request.args.get('sort', type=str, default='recent')
    # 정렬 기능
    if sort == 'popular' and question.answer_set :
        answer_list =  Answer.query.filter(Answer.question_id == question_id).\
                  outerjoin(answer_voter).\
                  group_by(Answer).\
                  order_by(func.count(answer_voter.c.user_id).desc()) # func.count()는 SQL의 count() 함수를 의미, outerjoin으로 추천수가 없는 답변도 포함
    else:
        answer_list = Answer.query.filter(Answer.question_id == question_id).order_by(Answer.create_date.desc())
    answer_list = answer_list.paginate(page=page, per_page=5)
    form = AnswerForm()

    return render_template('question/question_detail.html', question=question, form=form, answer_list=answer_list, sort=sort)                                                                               

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
