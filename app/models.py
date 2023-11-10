from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from app import db, bcrypt

class InviteData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    assessment_id = db.Column(db.Integer, nullable=False)
    recruiter_id = db.Column(db.Integer, nullable=False)


class IntervieweeAssessment(db.Model):
    __tablename__ = 'interviewee_assessment'

    id = db.Column(db.Integer, primary_key=True)
    interviewee_id = db.Column(db.Integer, db.ForeignKey('interviewees.id'))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'))
    recruiter_status = db.Column(db.String) 
    interviewee_status = db.Column(db.String)
    feedback = db.Column(db.String)
    score = db.Column(db.String) 

class IntervieweeRecruiter(db.Model):
    __tablename__ = 'interviewee_recruiter'

    id = db.Column(db.Integer, primary_key=True)
    interviewee_id = db.Column(db.Integer, db.ForeignKey('interviewees.id'))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters.id'))


class Recruiters(db.Model, SerializerMixin):
    __tablename__ = 'recruiters'

    serialize_rules = ('-_password_hash', '-created_at',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    phoneNumber = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    role = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    _password_hash = db.Column(db.String, nullable = False)



    # many to many relationship
    interviewees = db.relationship('Interviewees', secondary='interviewee_recruiter', back_populates='recruiters')

    # one to many relationship
    assessments = db.relationship('Assessments', backref='recruiter')

    @hybrid_property
    def password_hash(self):
        return 'Unauthorized'
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError('Invalid Email')
        return email

class Interviewees(db.Model, SerializerMixin):
    __tablename__ = 'interviewees'

    serialize_rules = ('-_password_hash', '-created_at',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    phoneNumber = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    _password_hash = db.Column(db.String, nullable = False)
    role = db.Column(db.String)

   

    # # one to many
    whiteboard = db.relationship('WhiteboardSubmissions', backref='interviewee')

    # # many to many relationship
    recruiters = db.relationship('Recruiters', secondary='interviewee_recruiter', back_populates='interviewees')
    
    # # many to many relationship
    assessments = db.relationship('Assessments', secondary='interviewee_assessment', back_populates='interviewees')

    @hybrid_property
    def password_hash(self):
        return 'Unauthorized'
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError('Invalid Email')
        return email
    

class Assessments(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime)
    duration = db.Column(db.Integer, nullable=True) 
    link = db.Column(db.String)

    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters.id'), nullable=False)

    questions = db.relationship('Questions', backref='assessment')
    interviewees = db.relationship('Interviewees', secondary='interviewee_assessment', back_populates='assessments')

class Questions(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String, nullable=False)
    choices = db.Column(db.String)
    solution = db.Column(db.String, nullable=False)
    question_type = db.Column(db.String, nullable=False) 

    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)

    answers = db.relationship('Answers', backref='question')
    whiteboard = db.relationship('WhiteboardSubmissions', backref='question')


class Answers(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    answer_text = db.Column(db.String)
    grade = db.Column(db.Integer)

    interviewee_id = db.Column(db.Integer, db.ForeignKey('interviewees.id'), nullable = False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable = False)


class WhiteboardSubmissions(db.Model):
    __tablename__ = "whiteboard"

    id = db.Column(db.Integer, primary_key=True)
    pseudocode = db.Column(db.String(500))
    code = db.Column(db.String(500))
    grade = db.Column(db.Integer)

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    interviewee_id = db.Column(db.Integer, db.ForeignKey('interviewees.id'))

