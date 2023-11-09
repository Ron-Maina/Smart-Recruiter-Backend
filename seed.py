from app.models import Interviewees, Assessments, IntervieweeAssessment, Recruiters, Questions, Answers, WhiteboardSubmissions, IntervieweeRecruiter
from faker import Faker
from app import app, db
import random


fake = Faker()

with app.app_context():
    
    Interviewees.query.delete()
    # Recruiters.query.delete()
    Assessments.query.delete()
    Questions.query.delete()
    Answers.query.delete()
    IntervieweeAssessment.query.delete()
    WhiteboardSubmissions.query.delete()
    IntervieweeRecruiter.query.delete()

    # interviewees_list = []
    # for i in range(1):
    #     interviewee = Interviewees(
    #         username = fake.name(),
    #         phoneNumber = fake.phone_number(),
    #         email = 'hahem61090@glalen.com',
    #         _password_hash = '1234',
    #         # created_at = '2023-10-31 09:31:23'
    #     )
    #     interviewees_list.append(interviewee)
    # db.session.add_all(interviewees_list)
    # db.session.commit()
    # print('SEEDED INTERVIEWEES...')

    # recruiters_list = []
    # for i in range(3):
    #     recruiter = Recruiters(
    #         username = fake.name(),
    #         phoneNumber = fake.phone_number(),
    #         email = fake.free_email(),
    #         _password_hash = '12345',
    #         # created_at = '2023-10-31 09:31:23'
    #     )
    #     recruiters_list.append(recruiter)
    # db.session.add_all(recruiters_list)
    # db.session.commit()
    # print('SEEDED RECRUITERS...')

    assessment_list = []
    for i in range(10):
        assessment = Assessments(
            title = fake.sentence(nb_words=5),
            # when = fake.date(),
            duration = 120,
            link = 'https://1234.com',
            recruiter_id = random.randint(1,3)
        )
        assessment_list.append(assessment)
    db.session.add_all(assessment_list)
    db.session.commit()
    print('SEEDED ASSESSMENTS...')

    lists = []
    status = ['pending', 'reviewed']
    int_status = ['pending', 'completed']
    for j in range(1, 11):
        for i in range(1, 4):
            data = IntervieweeAssessment(
                interviewee_id = j, 
                assessment_id = i,
                recruiter_status = random.choice(status),
                interviewee_status = random.choice(int_status),
                feedback = fake.sentence(),
                score = random.randint(1, 10)
            )
            lists.append(data)


            db.session.add_all(lists)
            db.session.commit()

    print("SEEDED INTASS JOIN TABLE....")

    recint = []
    for interviewee in Interviewees.query.all():
        for i in range(1,random.randint(2,4)):
            data = IntervieweeRecruiter(
                interviewee_id = interviewee.id, 
                recruiter_id = i,
            )
            recint.append(data)


            db.session.add_all(recint)
            db.session.commit()

    print("SEEDED INTREC JOIN TABLE....")

    questions_list = []
    type = ['ft', 'kata']
    for i in range(6):
        question = Questions(
            question_text = fake.sentence(),
            solution = 'solution',
            question_type = random.choice(type),
            assessment_id = random.randint(1, 3)
        )
        questions_list.append(question)
    for i in range(6):
        kata = Questions(
            question_text = fake.sentence(),
            choices = 'solution,mine,yours,his',
            solution = 'solution',
            question_type = 'mcq',
            assessment_id = random.randint(1, 3)
        )
        questions_list.append(kata)
    db.session.add_all(questions_list)
    db.session.commit()
    print('SEEDED QUESTIONS...')

    answers_list = []
    for i in range(10):
        answer = Answers(
            question_id = random.randint(1,3),
            interviewee_id = random.randint(1,2),
            answer_text = fake.sentence(),
            grade = random.randint(1,10),
            
        )
        answers_list.append(answer)
    db.session.add_all(answers_list)
    db.session.commit()
    print('SEEDED ANSWERS...')


    whiteboard_list = []
    for i in range(5):
        submission = WhiteboardSubmissions(
            question_id = random.randint(1,3),
            interviewee_id = random.randint(1,2),
            pseudocode = fake.sentence(),
            grade = random.randint(1,10),
            code = fake.sentence(),
        )
        whiteboard_list.append(submission)
    db.session.add_all(whiteboard_list)
    db.session.commit()
    print('SEEDED SUBMISSIONS...')

