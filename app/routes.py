from flask import make_response, jsonify, request, session, render_template
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import app, db, api
from app.models import Interviewees, Recruiters

app.config['SESSION_TYPE'] = 'filesystem'

from dotenv import load_dotenv
load_dotenv()

@app.route('/signup')
@app.route('/signup/<int:id>')
def index(id=0):
    return render_template('index.html')


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

api.add_resource(RecruiterSignUp, '/recruiter-signup')
api.add_resource(RecruiterLogin, '/recruiter-login')
api.add_resource(RecruiterLogout, '/recruiter-logout')
api.add_resource(RecruiterSession, '/recruiter-session')

api.add_resource(IntervieweeSignUp, '/interviewee-signup')
api.add_resource(IntervieweeLogin, '/interviewee-login')
api.add_resource(IntervieweeLogout, '/interviewee-logout')
api.add_resource(IntervieweeSession, '/interviewee-session')
