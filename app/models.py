from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from app import db, bcrypt

class IntervieweeAssessment(db.Model):
    __tablename__ = 'interviewee_assessment'

    interviewee_id = db.Column(db.Integer, db.ForeignKey('interviewees.id'), primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), primary_key = True)
    status = db.Column(db.String, nullable=False) 

class IntervieweeRecruiter(db.Model):
    __tablename__ = 'interviewee_recruiter'

    interviewee_id = db.Column(db.Integer, db.ForeignKey('interviewees.id'), primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters.id'), primary_key = True)


class Recruiters(db.Model, SerializerMixin):
    __tablename__ = 'recruiters'

    serialize_rules = ('-_password_hash', '-created_at',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    phoneNumber = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
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
    when = db.Column(db.DateTime)
    duration = db.Column(db.Integer, nullable=True) 
    link = db.Column(db.String)

    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters.id'), nullable=False)

    questions = db.relationship('Questions', backref='assessment')
    whiteboard = db.relationship('WhiteboardSubmissions', backref='assessment')
    interviewees = db.relationship('Interviewees', secondary='interviewee_assessment', back_populates='assessments')

class Questions(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String, nullable=False)
    solution = db.Column(db.String, nullable=False)
    question_type = db.Column(db.String, nullable=False) 
    answer_text = db.Column(db.String, nullable=False)
    grade = db.Column(db.Integer)
    feedback_text = db.Column(db.String(500), nullable=False)

    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)

class WhiteboardSubmissions(db.Model):
    __tablename__ = "whiteboard"

    id = db.Column(db.Integer, primary_key=True)
    bdd_text = db.Column(db.String(500), nullable=False)
    pseudocode_text = db.Column(db.String(500), nullable=False)
    code_text = db.Column(db.String(500), nullable=False)

    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'))
    interviewee_id = db.Column(db.Integer, db.ForeignKey('interviewees.id'))
