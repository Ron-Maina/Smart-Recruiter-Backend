from flask import make_response, jsonify, request, session, render_template
from sqlalchemy import desc
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

# interviewee side    
class IntervieweePendingAssessments(Resource):
    def get(self):
        pending_list = []
        interviewee = Interviewees.query.filter(Interviewees.id == session.get('interviewee')).first() 
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
        interviewee = Interviewees.query.filter(Interviewees.id == session.get('interviewee')).first() 
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

class RecruiterAssessments(Resource):
    def get(self):
        assessments_list = []
        assessments = Assessments.query.filter(Assessments.recruiter_id == session.get('recruiter')).all()
        for assessment in assessments:
            assessment_dict = {
                "id": assessment.id,
                "title": assessment.title,
                "link": assessment.link
            }
            assessments_list.append(assessment_dict)

        result = make_response(
            jsonify(assessments_list),
            200
        )
        return result
    
class RecruiterInterviewees(Resource):
    def get(self):
        interviewees_list = []
        recruiter = Recruiters.query.filter(Recruiters.id == session.get('recruiter')).first()
        int_recruiter = recruiter.interviewees
        for interviewee in int_recruiter:
            interviewee_dict = {
                "username": interviewee.username,
                "email": interviewee.email,
                "id": interviewee.id
            }
            interviewees_list.append(interviewee_dict)

        result = make_response(
            jsonify(interviewees_list),
            200
        )
        return result
    
class SortIntervieweesByScore(Resource):
    def get(self, id):
        interviewee_score = []
        interviewees_with_scores = db.session.query(Interviewees, IntervieweeAssessment.score).\
        join(IntervieweeAssessment).\
        filter(IntervieweeAssessment.assessment_id == session.get('recruiter')).\
        order_by(desc(IntervieweeAssessment.score)).all()

        for interviewee, score in interviewees_with_scores:
            interviewee_dict = {
                "id": interviewee.id,
                "username": interviewee.username,
                "email": interviewee.email,
                "score": score
            }
            interviewee_score.append(interviewee_dict)

        result = make_response(
        jsonify(interviewee_score),
        200
        )
        return result

# Recruiter side
# Interviewees with pending status for a particular assessment   
class PendingReviews(Resource):
    def get(self, id):
        interviewees_with_pending_list = []
        interviewees_with_pending_status = db.session.query(Interviewees).\
        join(IntervieweeAssessment, Interviewees.id == IntervieweeAssessment.interviewee_id).\
        filter(IntervieweeAssessment.assessment_id == id, IntervieweeAssessment.status == "pending").\
        all()

        for interviewee in interviewees_with_pending_status:
            interviewee_dict = {
                "interviewee_id": interviewee.id,
                "assessment_id": id,
                "username": interviewee.username,
                "email": interviewee.email
            }
            
            interviewees_with_pending_list.append(interviewee_dict)

        result = make_response(
            jsonify(interviewees_with_pending_list),
            200
        )
        return result

# Displays the question and answers for each question 
# for a particular interviewee for a particular assessment    
class McqFreeTextAnswers(Resource):
    def get(self, assessment_id, interviewee_id):
        answer_list = []
        questions = Questions.query.filter(Questions.assessment_id == assessment_id, Questions.question_type != 'kata').all()

        for question in questions:
            print(question.question_type)
            for answer in (question.answers):
                if answer.interviewee_id == interviewee_id and question.id == answer.question_id:
                    response_dict = {
                        "question": question.question_text,
                        "answer": answer.answer_text,
                        "grade": answer.grade
                    }
                    answer_list.append(response_dict)

        result = make_response(
            jsonify(answer_list),
            200
        )
        return result

# Displays the kata question and solution for a particular interviewee
# for a particular assessment
class KataAnswers(Resource):
    def get(self, assessment_id, interviewee_id):
        kata_answer_list = []
        kata = Questions.query.filter(Questions.assessment_id == assessment_id, Questions.question_type == 'kata').first()
        
        for answer in (kata.whiteboard):
            if answer.interviewee_id == interviewee_id:
                response_dict = {
                    "question": kata.question_text,
                    "pseudocode": answer.pseudocode,
                    "bdd": answer.bdd,
                    "code": answer.code,
                    "grade": answer.grade
                }
                kata_answer_list.append(response_dict)

        result = make_response(
            jsonify(kata_answer_list),
            200
        )
        return result


api.add_resource(RecruiterSignUp, '/recruitersignup')
api.add_resource(RecruiterLogin, '/recruiterlogin')
api.add_resource(RecruiterLogout, '/recruiterlogout')
api.add_resource(RecruiterSession, '/recruitersession')

api.add_resource(RecruiterAssessments, '/recruiterassessments')
api.add_resource(RecruiterInterviewees, '/recruiterinterviewees')
api.add_resource(PendingReviews, '/pendingreview/<int:id>')

api.add_resource(IntervieweeSignUp, '/intervieweesignup')
api.add_resource(IntervieweeLogin, '/intervieweelogin')
api.add_resource(IntervieweeLogout, '/intervieweelogout')
api.add_resource(IntervieweeSession, '/intervieweesession')

api.add_resource(IntervieweePendingAssessments, '/pendingassessments')
api.add_resource(IntervieweeReviewedAssessments, '/reviewedassessments')
api.add_resource(IntervieweeFeedback, '/intfeedback/<int:id>')
api.add_resource(AssessmentQuestions, '/questions/<int:id>')
api.add_resource(KataFeedback, '/whiteboard/<int:id>')
api.add_resource(McqFreeTextAnswers, '/ftmcqanswers/<int:assessment_id>/<int:interviewee_id>')
api.add_resource(KataAnswers, '/katanswers/<int:assessment_id>/<int:interviewee_id>')



api.add_resource(SortIntervieweesByScore, '/assessment/<int:id>')











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