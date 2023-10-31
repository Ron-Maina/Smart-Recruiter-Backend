from app.models import Interviewees, Assessments, IntervieweeAssessment
from faker import Faker
from app import app, db


fake = Faker()

with app.app_context():
    
    Interviewees.query.delete()
    Assessments.query.delete()
    IntervieweeAssessment.query.delete()

    interviewees_list = []
    for i in range(2):
        interviewee = Interviewees(
            username = fake.name(),
            phoneNumber = fake.phone_number(),
            email = fake.free_email(),
            _password_hash = '1234',
        )
        interviewees_list.append(interviewee)
    db.session.add_all(interviewees_list)
    db.session.commit()
    print('SEEDED INTERVIEWEES...')

    assessment_list = []
    for i in range(3):
        assessment = Assessments(
            when = fake.date(),
            duration = 120,
            link = 'https://1234.com',
            result = fake.phone_number(),
            pending = 'True', 
        )
        assessment_list.append(assessment)
    db.session.add_all(assessment_list)
    db.session.commit()
    print('SEEDED Assessment...')

    lists = []
    for interviewee in Interviewees.query.all():
        for i in range(1, 4):
            data = IntervieweeAssessment(
                interviewee_id = interviewee.id, 
                assessment_id = i
            )
            lists.append(data)
            # data = IntervieweeAssessment.insert().values(assessment_id = i, interviewee_id = interviewee.id)


            db.session.add_all(lists)
            db.session.commit()

    print("SEEDED JOIN TABLE....")

