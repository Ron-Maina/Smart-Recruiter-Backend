from flask import make_response, jsonify, request, session, render_template
from sqlalchemy import desc
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
import subprocess

from datetime import datetime

from app import app, db, api, mail, serializer, SignatureExpired, BadTimeSignature, Message, url_for, request
from app.models import  Interviewees, Recruiters, Assessments, IntervieweeAssessment, Questions, Answers, WhiteboardSubmissions, IntervieweeRecruiter, InviteData

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

            existing_user = Recruiters.query.filter_by(email=data.get('email')).first()
            interviewee = Interviewees.query.filter_by(email = data.get('email')).first()
            print(interviewee)

            if existing_user or interviewee:
                return jsonify({'message': 'Email already exists'}, 403)
            
            new_recruiter = Recruiters(
                username = data.get('username'),
                email = data.get('email'),
                phoneNumber = data.get('number'),
                role = 'recruiter'
            )
            new_recruiter.password_hash = data.get('password')

            db.session.add(new_recruiter)
            db.session.commit()

            session['recruiter'] = new_recruiter.id

            recruiter_dict = {
                "id": new_recruiter.id,
                "username": new_recruiter.username,
                "email": new_recruiter.email,
                "role": new_recruiter.role
            }

            result = make_response(
                jsonify(recruiter_dict),
                200
            )
            return result
        except ValueError:
            raise BadRequest(["validation errors"])  
        
        
class RecruiterSession(Resource):
    def get(self):
        recruiter = Recruiters.query.filter(Recruiters.id == session.get('recruiter')).first()
        if recruiter:
            recruiter_dict = {
                "id": recruiter.id,
                "username": recruiter.username,
                "email": recruiter.email,
                "role": recruiter.role
            }
            return jsonify(recruiter_dict)
        else:
           return {}, 401 
        
class RecruiterLogout(Resource):
    def delete(self):
        print(session['recruiter'])
        session['recruiter'] = None
        print(session['recruiter'])

        return {}, 204


class IntervieweeSignUp(Resource):
    def post(self):
        try:
            data = request.get_json()

            existing_user = Interviewees.query.filter_by(username=data.get('username')).first()
            if existing_user:
                return jsonify({'message': 'Email already registered'})
            
            new_interviewee = Interviewees(
                username = data.get('username'),
                email = data.get('email'),
                phoneNumber = data.get('number'),
                role = 'interviewee'
            )
            new_interviewee.password_hash = data.get('password')

            db.session.add(new_interviewee)
            db.session.commit()

            session['interviewee'] = new_interviewee.id

            interviewee_dict = {
                "id": new_interviewee.id,
                "username": new_interviewee.username,
                "email": new_interviewee.email,
                "role": new_interviewee.role
            }

            result = make_response(
                jsonify(interviewee_dict),
                200
            )
            return result
        except ValueError:
            raise BadRequest(["validation errors"])   
        
class IntervieweeSession(Resource):
    def get(self):
        interviewee = Interviewees.query.filter(Interviewees.id == session.get('interviewee')).first()
        if interviewee:
            interviewee_dict = {
                "id": interviewee.id,
                "username": interviewee.username,
                "email": interviewee.email,
                "role": interviewee.role
            }
            return jsonify(interviewee_dict)
        else:
           return {}, 401 
        
class IntervieweeLogout(Resource):
    def delete(self):
        session['interviewee'] = None
        return {}, 204
    
    
class Login(Resource):
    def post(self):
        recruiter = Recruiters.query.filter(Recruiters.email == request.get_json()['email']).first()
        interviewee = Interviewees.query.filter(Interviewees.email == request.get_json()['email']).first()

        password = request.get_json()['password']
        if recruiter:
            if (recruiter) and (recruiter.authenticate(password) == True):
                session['recruiter'] = recruiter.id
                print(session['recruiter'])
                recruiter_dict = {
                    "id": recruiter.id,
                    "username": recruiter.username,
                    "email": recruiter.email,
                    "role": recruiter.role
                }


                response = make_response(
                    jsonify(recruiter_dict),
                    200
                )
                return response
            else:
                return {"message":"You do not have an account"}, 401
            
        elif interviewee:
            if (interviewee) and (interviewee.authenticate(password) == True):
                session['interviewee'] = interviewee.id
                print(session['interviewee'])
                interviewee_dict = {
                    "id": interviewee.id,
                    "username": interviewee.username,
                    "email": interviewee.email,
                    "role": interviewee.role
                }

                response = make_response(
                    jsonify(interviewee_dict),
                    200
                )
                return response
            else:
                return {"message":"You do not have an account"}, 401

# interviewee side 
# Assessment Not Done   
class IntervieweePendingAssessments(Resource):
    def get(self):
        pending_list = []
        interviewee = Interviewees.query.filter(Interviewees.id == session.get('interviewee')).first() 
        if interviewee:
            assessments_done_by_interviewee = db.session.query(Assessments).join(IntervieweeAssessment).filter(IntervieweeAssessment.interviewee_id == interviewee.id, 
                                                                                                               IntervieweeAssessment.interviewee_status == 'pending').order_by(desc(IntervieweeAssessment.id)).all()
            for assessment in assessments_done_by_interviewee:
                pending_dict = {
                    "id": assessment.id,
                    "title": assessment.title,
                    "link": assessment.link,
                    "time": assessment.time,
                    "duration": assessment.duration
                }
                pending_list.append(pending_dict)

            result = make_response(
                jsonify(pending_list),
                200
            )
            return result
        
# Assessment Done and Reviewed       
class DoneAndReviewedAssessments(Resource):
    def get(self):
        reviewed_list = []
        interviewee = Interviewees.query.filter(Interviewees.id == session.get('interviewee')).first() 
        if interviewee:
            assessments_done_by_interviewee = db.session.query(Assessments).join(IntervieweeAssessment).filter(IntervieweeAssessment.interviewee_id == session.get('interviewee'), IntervieweeAssessment.recruiter_status == 'reviewed',IntervieweeAssessment.interviewee_status == 'completed').all()
            for assessment in assessments_done_by_interviewee:
                reviewed_dict = {
                    "id": assessment.id,
                    "title": assessment.title,
                    "recruiter_status": 'reviewed'
                }
                reviewed_list.append(reviewed_dict)

            result = make_response(
                jsonify(reviewed_list),
                200
            )
            return result
        
# Assessment Done and Not Reviewed       
class DoneNotReviewedAssessments(Resource):
    def get(self):
        reviewed_list = []
        interviewee = Interviewees.query.filter(Interviewees.id == session.get('interviewee')).first() 
        if interviewee:
            assessments_done_by_interviewee = db.session.query(Assessments).join(IntervieweeAssessment).filter(IntervieweeAssessment.interviewee_id == session.get('interviewee'), IntervieweeAssessment.recruiter_status == 'pending',IntervieweeAssessment.interviewee_status == 'completed').all()
            for assessment in assessments_done_by_interviewee:
                reviewed_dict = {
                    "id": assessment.id,
                    "title": assessment.title,
                    "recruiter_status": 'pending'

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
            if question.question_type == 'mcq':
                mcq_dict = {
                    "id": question.id,
                    "question": question.question_text,
                    "choices": question.choices,
                    "solution": question.solution,
                    "type": question.question_type
                }
                question_list.append(mcq_dict)

            elif question.question_type == 'kata':
                kata_dict = {
                    "id": question.id,
                    "question": question.question_text,
                    "solution": question.solution,
                    "type": question.question_type
                }
                question_list.append(kata_dict)
            else:
                ft_dict = {
                    "id": question.id,
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
        assessment = Assessments.query.filter_by(id=id).first()
    
        if not assessment:
            return jsonify({"message": "Assessment not found"}), 404

        questions = Questions.query.filter_by(assessment_id=id).all()
        
        assessment_data = {
            "assessment_id": assessment.id,
            "assessment_name": assessment.title,
            "feedback": IntervieweeAssessment.query.filter_by(assessment_id=assessment.id, interviewee_id=session.get('interviewee')).first().feedback,
            "total_score": IntervieweeAssessment.query.filter_by(assessment_id=assessment.id, interviewee_id=session.get('interviewee')).first().score,
            "questions": []
        }

        for question in questions:
            question_data = {
                "question_id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "answers": [],
                "whiteboard_submissions": []
            }

            if question.question_type in ["mcq", "ft"]:
                answers = Answers.query.filter_by(question_id=question.id).all()
                for answer in answers:
                    question_data["answers"].append({
                        "answer_id": answer.id,
                        "answer_text": answer.answer_text,
                        "grade": answer.grade
                    })
            elif question.question_type == "kata":
                whiteboard_submissions = WhiteboardSubmissions.query.filter_by(question_id=question.id).all()
                for submission in whiteboard_submissions:
                    question_data["whiteboard_submissions"].append({
                        "submission_id": submission.id,
                        "pseudocode": submission.pseudocode,
                        "code": submission.code,
                    })

            assessment_data["questions"].append(question_data)

        return jsonify(assessment_data)
    
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
        assessments = Assessments.query.filter(Assessments.recruiter_id == session.get('recruiter')).order_by(desc(Assessments.id)).all()
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

# Recruiter side
# Interviewees with pending status for a particular assessment sorted by score    
class PendingIntervieweesByScore(Resource):
    def get(self, id):
        interviewee_score = []
        interviewees_with_scores = db.session.query(Interviewees, IntervieweeAssessment.score).\
        join(IntervieweeAssessment).\
        filter(IntervieweeAssessment.assessment_id == id, IntervieweeAssessment.recruiter_status == "pending", IntervieweeAssessment.interviewee_status == "completed").\
        order_by(desc(IntervieweeAssessment.score)).all()

        for interviewee, score in interviewees_with_scores:
            interviewee_dict = {
                "id": interviewee.id,
                "assessment_id": id,
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
# Interviewees with pending status for a particular assessment sorted by score    
class ReviewedIntervieweesByScore(Resource):
    def get(self, id):
        interviewee_score = []
        interviewees_with_scores = db.session.query(Interviewees, IntervieweeAssessment.score).\
        join(IntervieweeAssessment).\
        filter(IntervieweeAssessment.assessment_id == id, IntervieweeAssessment.recruiter_status == "reviewed").\
        order_by(desc(IntervieweeAssessment.score)).all()

        for interviewee, score in interviewees_with_scores:
            interviewee_dict = {
                "id": interviewee.id,
                "assessment_id": id,
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


    
# Displays the question and answers for each question 
# for a particular interviewee for a particular assessment    
class McqFreeTextAnswersByID(Resource):
    def get(self, assessment_id, interviewee_id):
        answer_list = []
        questions = Questions.query.filter(Questions.assessment_id == assessment_id, Questions.question_type != 'kata').all()

        for question in questions:
            print(question.question_type)
            for answer in (question.answers):
                if answer.interviewee_id == interviewee_id and question.id == answer.question_id:
                    response_dict = {
                        "question_id": question.id,
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
class KataAnswersByID(Resource):
    def get(self, assessment_id, interviewee_id):
        kata_answer_list = []
        kata = Questions.query.filter(Questions.assessment_id == assessment_id, Questions.question_type == 'kata').first()
        
        for answer in (kata.whiteboard):
            if answer.interviewee_id == interviewee_id:
                response_dict = {
                    "question": kata.question_text,
                    "pseudocode": answer.pseudocode,
                    "code": answer.code,
                    "grade": answer.grade
                }
                kata_answer_list.append(response_dict)

        result = make_response(
            jsonify(kata_answer_list),
            200
        )
        return result
    
class AddAnswers(Resource):
    def post(self):
        try:
            data = request.get_json()
            details = data['answers']

            for answer in details:
                interviewee_answers = Answers(
                    interviewee_id = data['intervieweeId'],
                    answer_text = answer['answer'],
                    grade = answer['grade'],
                    question_id = answer['questionId'],
                )

                db.session.add(interviewee_answers)
                db.session.commit()


            response_dict = {
                "id": interviewee_answers.id,
                "answer_text": interviewee_answers.answer_text,
                "grade": interviewee_answers.grade,
                "question_id": interviewee_answers.question_id,
            }

            result = make_response(
                jsonify(response_dict),
                200
            )
            return result
        
        except ValueError:
            raise BadRequest(["validation errors"])  
        
class AdddWhiteboard(Resource):
    def post(self):
        try:
            data = request.get_json()

            kata_answers = WhiteboardSubmissions(
                interviewee_id = data.get('interviewee_id'),
                pseudocode = data.get('pseudocode'),
                code = data.get('code'),
                grade = data.get('grade'),
                question_id = data.get('question_id'),
            )

            db.session.add(kata_answers)
            db.session.commit()


            response_dict = {
                "id": kata_answers.id,
                "code": kata_answers.code,
                "pseudocode": kata_answers.pseudocode,
                "grade": kata_answers.grade,
                "question_id": kata_answers.question_id,
            }

            result = make_response(
                jsonify(response_dict),
                200
            )
            return result
        
        except ValueError:
            raise BadRequest(["validation errors"])  
    
class CreateAssessment(Resource):
    def post(self):
        try:
            data = request.get_json()
            assessment = Assessments(
                title = data.get('title'),
                link = data.get('link'),
                duration = data.get('duration'),
                recruiter_id = data.get('recruiter_id'),
                time = datetime.strptime(data.get('time'), '%Y-%m-%dT%H:%M')
            )
            
            db.session.add(assessment)
            db.session.commit()

            session['newAssessment'] = assessment.id

            response_dict = {
                "id": assessment.id,
                "title": assessment.title,
                "link": assessment.link
            }
        
            result = make_response(
                jsonify(response_dict)
            )

            return result
        
        except Exception as e:
            db.session.rollback()  
            response = make_response(
                jsonify({"error": str(e)}),
                500
            )

# Adds set questions     
class QuestionsResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            print(data)
            
            # Check for empty fields
            required_fields = ['question_text', 'solution', 'question_type', 'assessment_id']
            for field in required_fields:
                if not data.get(field):
                    return make_response(jsonify({"error": f"{field} is required"}), 400)
            
            # Create the Questions instance
            question = Questions(
                question_text=data['question_text'],
                solution=data['solution'],
                question_type=data['question_type'],
                assessment_id=data['assessment_id']
            )
            
            # If the question type is "mcq," include the "choices" attribute
            if data['question_type'] == 'mcq':
                choices = data.get('choices')
                if choices:
                    question.choices = choices
            
            db.session.add(question)
            db.session.commit()
            
            response_dict = {
                "id": question.id,
                "question_text": question.question_text,
                "solution": question.solution,
                "assessment_id": question.assessment_id,
                "question_type": question.question_type,
            }
            
            # Include "choices" attribute in the response if the question type is "mcq"
            if data['question_type'] == 'mcq':
                response_dict['choices'] = question.choices
            
            return make_response(jsonify(response_dict), 201)
        
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)

        
class UpdateInterviewAssessment(Resource):
    def patch(self, assessmentId, intervieweeId):

        new_feedback = request.json.get('feedback')
        score = request.json.get('score')
        status = request.json.get('status')

        interviewee_assessment = IntervieweeAssessment.query.filter(IntervieweeAssessment.interviewee_id==intervieweeId, IntervieweeAssessment.assessment_id==assessmentId).first()

        if interviewee_assessment and new_feedback:
            interviewee_assessment.feedback = new_feedback
            interviewee_assessment.recruiter_status = "reviewed"
            interviewee_assessment.score = score

            db.session.commit()
            return jsonify({"message": "Feedback updated successfully"}, 200)

        elif interviewee_assessment and status:
            interviewee_assessment.interviewee_status = 'completed'
            db.session.commit()
            return jsonify({"message": "Score updated successfully"}, 200)

        else:
            return jsonify({"message": "No entry found"}, 404)

      

@app.route('/sendinvite', methods=['POST'])   
def sendinvite():
    data = request.json
    emails = data.get('recipient_emails')
    title = data.get('title')
    assessment_id = data.get('assessment_id')

    for email in emails:
        token = serializer.dumps(email, salt="email-confirm")

    
        invite_data = InviteData(email=email, title=title, assessment_id=assessment_id, recruiter_id=session.get('recruiter'))
        db.session.add(invite_data)
        db.session.commit()


        msg = Message('Accept Assessment', sender='noreply@app.com', recipients=[email])


        link = url_for('accept_invite', token=token, _external=True)


        msg.body = "Your link is {}. Please note the link expires after 24 hours". format(link)

        mail.send(msg)

    return jsonify({"Message": "Successful"})
    

@app.route('/accept_invite/<token>')
def accept_invite(token):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=86400)

        interviewee = Interviewees.query.filter(Interviewees.email == email).first()

        if not interviewee:
            return '<p>You do not have a Smart Recruiter account. <a href="http://localhost:3000/signup">Click here</a> to create an account and get access to the assessment</p>'
        
        invite_data = InviteData.query.filter(InviteData.email == interviewee.email).first()


        interviewee_assessment = IntervieweeAssessment(
            interviewee_id = interviewee.id,
            assessment_id = invite_data.assessment_id,
            recruiter_status = 'pending',
            interviewee_status = 'pending'
        )

        db.session.add(interviewee_assessment)
        db.session.commit()

        interviewee_recruiter = IntervieweeRecruiter(
            interviewee_id = interviewee.id,
            recruiter_id = invite_data.recruiter_id
        )

        db.session.add(interviewee_recruiter)
        db.session.commit()


    except SignatureExpired:
        return '<h1>Expired Invite</h1>'
    except BadTimeSignature:
        return '<h1>Please Enter Correct Invite Token</h1>'
        
    return '<p>You have accepted the assessment {}. Please view it in the App</p>'.format(invite_data.title)
    
@app.route('/runcode', methods=['POST'])
def run_tests():
    try:
        data = request.get_json()
        user_code = (data['userCode'])
        test_code = data['testCode']
       

        # Save user code and tests to separate files
        with open('user_code.py', 'w') as user_file:
            user_file.write(user_code)

        with open('test_code.py', 'w') as test_file:
            test_file.write(test_code)

        # Run pytest using subprocess
        result = subprocess.run(['pytest', 'test_code.py'], capture_output=True, text=True)

        # Parse pytest output to get number of passed and total tests
        passed_tests = result.stdout.count('passed')
        total_tests = result.stdout.count('collected')

        return jsonify({'passed': passed_tests, 'total': total_tests})

    except Exception as e:
        print('Error running tests:', str(e))
        return jsonify({'error': 'Error running tests'})
        

api.add_resource(Login, '/login')

api.add_resource(RecruiterSignUp, '/recruitersignup')
api.add_resource(RecruiterLogout, '/recruiterlogout')
api.add_resource(RecruiterSession, '/recruitersession')

api.add_resource(RecruiterAssessments, '/recruiterassessments')
api.add_resource(RecruiterInterviewees, '/recruiterinterviewees')

api.add_resource(IntervieweeSignUp, '/intervieweesignup')
api.add_resource(IntervieweeLogout, '/intervieweelogout')
api.add_resource(IntervieweeSession, '/intervieweesession')
api.add_resource(IntervieweeFeedback, '/intfeedback/<int:id>')

api.add_resource(IntervieweePendingAssessments, '/pendingassessments')
api.add_resource(DoneAndReviewedAssessments, '/reviewedassessments')
api.add_resource(DoneNotReviewedAssessments, '/notreviewedassessments')


api.add_resource(AssessmentQuestions, '/questions/<int:id>')
api.add_resource(KataFeedback, '/whiteboard/<int:id>')
api.add_resource(McqFreeTextAnswersByID, '/ftmcqanswers/<int:assessment_id>/<int:interviewee_id>')
api.add_resource(KataAnswersByID, '/katanswers/<int:assessment_id>/<int:interviewee_id>')
api.add_resource(AddAnswers, '/answers')
api.add_resource(AdddWhiteboard, '/whiteboard')




api.add_resource(PendingIntervieweesByScore, '/pendinginterviewees/<int:id>')
api.add_resource(ReviewedIntervieweesByScore, '/reviewedinterviewees/<int:id>')

api.add_resource(CreateAssessment, '/createassessment')
api.add_resource(QuestionsResource, '/createquestions')
api.add_resource(UpdateInterviewAssessment, '/update_interviewee_assessment/<int:assessmentId>/<int:intervieweeId>')












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