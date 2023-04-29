from datetime import datetime

from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect

from pybo import db
from ..forms import AnswerForm
from pybo.models import Question, Answer
from pybo.views.auth_views import login_required

bp = Blueprint('answer', __name__, url_prefix='/answer')


@bp.route('/create/<int:question_id>', methods=('POST',))
@login_required
def create(question_id): # answer.create
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    if form.validate_on_submit():
        content = request.form['content']
        answer = Answer(content=content, create_date=datetime.now(), user=g.user)
        question.answer_set.append(answer)
        db.session.commit()
        return redirect('{}#answer_{}'.format(url_for('question.detail', question_id=question_id), answer.id))
    return render_template('question/question_detail.html', question=question, form=form)

@bp.route('/modify/<int:answer_id>', methods=('GET','POST'))
@login_required
def modify(answer_id):
    answer = Answer.query.get_or_404(answer_id)

    if g.user != answer.user:
        flash('수정 권한이 없습니다.')
        return redirect('{}#answer_{}'.format(url_for('question.detail', question_id=answer.question.id), answer.id))
    
    if request.method == 'POST':
        form = AnswerForm()
        if form.validate_on_submit():
            form.populate_obj(answer)
            answer.modify_date = datetime.now()
            db.session.commit()
            return redirect('{}#answer_{}'.format(url_for('question.detail', question_id=answer.question.id), answer.id))

    else:
        form = AnswerForm(obj=answer)
    
    return render_template('answer/answer_form.html', answer=answer, form=form)

@bp.route('/delete/<int:answer_id>')
@login_required
def delete(answer_id):
    answer = Answer.query.get_or_404(answer_id)

    if g.user != answer.user:
        flash('삭제 권한이 없습니다.')
        return redirect('{}#answer_{}'.format(url_for('question.detail', question_id=answer.question.id), answer.id))
    
    question_id = answer.question.id # 먼저 question_id를 얻어놓고 삭제해야 한다.
    db.session.delete(answer)
    db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))

# 답변 추천 기능
@bp.route('/like/<int:answer_id>')
@login_required
def like(answer_id):
    _answer = Answer.query.get_or_404(answer_id)
    if g.user == _answer.user:
        flash('본인이 작성한 답변은 추천할 수 없습니다.')
    elif g.user in _answer.voter:
        _answer.voter.remove(g.user)
        db.session.commit()
    else:
        _answer.voter.append(g.user)
        db.session.commit()
    return redirect('{}#answer_{}'.format(url_for('question.detail', question_id=_answer.question.id), _answer.id))