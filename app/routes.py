from flask import make_response, jsonify, request, session, render_template
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import app, db, api
from app.models import  Interviewees, Recruiters, Assessments, IntervieweeAssessment, Questions, Answers, WhiteboardSubmissions

app.config['SESSION_TYPE'] = 'filesystem'

from dotenv import load_dotenv
load_dotenv()

@app.route('/')
@app.route('/<int:id>')
def index(id=0):
    return render_template("index.html")
   

class RecruiterSignUp(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_recruiter = Recruiters(
                username = data.get('username'),
                email = data.get('email'),
                phoneNumber = data.get('number'),
            )
            new_recruiter.password_hash = data.get('password')

            db.session.add(new_recruiter)
            db.session.commit()

            session['recruiter_id'] = new_recruiter.id

            recruiter_dict = {
                "id": new_recruiter.id,
                "username": new_recruiter.username,
                "email": new_recruiter.email,

            }

            result = make_response(
                jsonify(recruiter_dict),
                200
            )
            return result
        except ValueError:
            raise BadRequest(["validation errors"])  
        

class RecruiterLogin(Resource):
    def post(self):
        recruiter = Recruiters.query.filter(Recruiters.username == request.get_json()['username']).first()
        password = request.get_json()['password']

        if (recruiter) and (recruiter.authenticate(password) == True):
            session['recruiter'] = recruiter.id

            response = make_response(
                jsonify(recruiter.to_dict()),
                200
            )
            return response
        else:
            return {"message":"You do not have an account"}, 401
        
class RecruiterSession(Resource):
    def get(self):
        recruiter = Recruiters.query.filter(Recruiters.id == session.get('recruiter')).first()
        if recruiter:
            return jsonify(recruiter.to_dict())
        else:
           return {}, 401 
        
class RecruiterLogout(Resource):
    def delete(self):
        session['recruiter'] = None
        return {}, 204


class IntervieweeSignUp(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_interviewee = Interviewees(
                username = data.get('username'),
                email = data.get('email'),
                phoneNumber = data.get('number'),
            )
            new_interviewee.password_hash = data.get('password')

            db.session.add(new_interviewee)
            db.session.commit()

            session['interviewee_id'] = new_interviewee.id

            interviewee_dict = {
                "id": new_interviewee.id,
                "username": new_interviewee.username,
                "email": new_interviewee.email,
            }

            result = make_response(
                jsonify(interviewee_dict),
                200
            )
            return result
        except ValueError:
            raise BadRequest(["validation errors"])   
        
class IntervieweeLogin(Resource):
    def post(self):
        interviewee = Interviewees.query.filter(Interviewees.username == request.get_json()['username']).first()
        password = request.get_json()['password']

        if (interviewee) and (interviewee.authenticate(password) == True):
            session['interviewee'] = interviewee.id

            response = make_response(
                jsonify(interviewee.to_dict()),
                200
            )
            return response
        else:
            return {"message":"You do not have an account"}, 401
        
class IntervieweeSession(Resource):
    def get(self):
        interviewee = Interviewees.query.filter(Interviewees.id == session.get('interviewee')).first()
        if interviewee:
            return jsonify(interviewee.to_dict())
        else:
           return {}, 401 
        
class IntervieweeLogout(Resource):
    def delete(self):
        session['interviewee'] = None
        return {}, 204
    
class IntervieweePendingAssessments(Resource):
    def get(self):
        pending_list = []
        interviewee = Interviewees.query.filter(Interviewees.id == 1).first() 
        if interviewee:
            assessments_done_by_interviewee = db.session.query(Assessments).join(IntervieweeAssessment).filter(IntervieweeAssessment.interviewee_id == interviewee.id, IntervieweeAssessment.status == 'pending').all()
            for assessment in assessments_done_by_interviewee:
                pending_dict = {
                    "id": assessment.id,
                    "title": assessment.title,
                }
                pending_list.append(pending_dict)

            result = make_response(
                jsonify(pending_list),
                200
            )
            return result
        
class IntervieweeReviewedAssessments(Resource):
    def get(self):
        reviewed_list = []
        interviewee = Interviewees.query.filter(Interviewees.id == 1).first() 
        if interviewee:
            assessments_done_by_interviewee = db.session.query(Assessments).join(IntervieweeAssessment).filter(IntervieweeAssessment.interviewee_id == interviewee.id, IntervieweeAssessment.status == 'done').all()
            for assessment in assessments_done_by_interviewee:
                reviewed_dict = {
                    "id": assessment.id,
                    "title": assessment.title,
                }
                reviewed_list.append(reviewed_dict)

            result = make_response(
                jsonify(reviewed_list),
                200
            )
            return result

class AssessmentQuestions(Resource):
    def get(self, id):
        question_list = []
        questions = Questions.query.filter(Questions.assessment_id == id).all()
        for question in questions:
            if question.question_type == 'mcq' or question.question_type == 'kata':
                question_dict = {
                    "question": question.question_text,
                    "choices": question.solution,
                    "type": question.question_type
                }
                question_list.append(question_dict)
            else:
                ft_dict = {
                    "question": question.question_text,
                    "type": question.question_type
                }
                question_list.append(ft_dict)

        result = make_response (
            jsonify(question_list),
            200
        )
        return result  

class IntervieweeFeedback(Resource):
    def get(self, id):
        answer_list = []
        answers = db.session.query(Answers).join(Questions).filter(Questions.assessment_id == id, Answers.interviewee_id == session.get('interviewee')).all()
        for answer in answers:
            answer_dict = {
                "answer_text": answer.answer_text,
                "grade": answer.grade,
                "feedback": answer.feedback
            }
            answer_list.append(answer_dict)

        result = make_response (
            jsonify(answer_list),
            200
        )
        return result
    
class KataFeedback(Resource):
    def get(self, id):
        kata_list = []
        katas = db.session.query(WhiteboardSubmissions).join(Questions).filter(Questions.assessment_id == id, Questions.question_type == 'kata', WhiteboardSubmissions.interviewee_id == session.get('interviewee')).all()
        for kata in katas:
            answer_dict = {
                "pseudocode": kata.pseudocode,
                "code": kata.code,
                "grade": kata.grade,
                "feedback": kata.feedback
            }
            kata_list.append(answer_dict)

        result = make_response (
            jsonify(kata_list),
            200
        )
        return result        

api.add_resource(RecruiterSignUp, '/recruitersignup')
api.add_resource(RecruiterLogin, '/recruiterlogin')
api.add_resource(RecruiterLogout, '/recruiterlogout')
api.add_resource(RecruiterSession, '/recruitersession')

api.add_resource(IntervieweeSignUp, '/intervieweesignup')
api.add_resource(IntervieweeLogin, '/intervieweelogin')
api.add_resource(IntervieweeLogout, '/intervieweelogout')
api.add_resource(IntervieweeSession, '/intervieweesession')

api.add_resource(IntervieweePendingAssessments, '/pendingassessments')
api.add_resource(IntervieweeReviewedAssessments, '/reviewedassessments')
api.add_resource(IntervieweeFeedback, '/intfeedback/<int:id>')
api.add_resource(AssessmentQuestions, '/questions/<int:id>')
api.add_resource(KataFeedback, '/whiteboard/<int:id>')









@app.route('/loginpage')
@app.route('/contactspage')
@app.route('/chatpage')
@app.route('/new-contactpage')
@app.route('/update-profilepage')
@app.route('/settingspage')
@app.route('/homepage')
def catch_all():
    return render_template("index.html")


if __name__ == '__main__':
    db.session.create_all()
    app.run(debug = True)