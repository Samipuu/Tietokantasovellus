from db import db
from security import *
from flask_sqlalchemy import SQLAlchemy

def get_courses(user_id):
    sql = "SELECT id, title, content " \
          "FROM courses " \
          "LEFT JOIN course_rights ON id=course_id " \
          "WHERE (user_id=0 AND can_read = TRUE) " \
          "OR (user_id=:user_id AND can_read = TRUE) " \
          "GROUP BY id"
    result = db.session.execute(sql, {"user_id":user_id})
    courses = result.fetchall()
    return courses

def create_course(title, content, username, public):
    user = get_user_id(username)
    sql = "INSERT INTO courses (title, content, created_at, owner) " \
          "VALUES (:title, :content, NOW(), :owner) " \
          "RETURNING id"
    result = db.session.execute(sql, {"title":title,
                                      "content":content, 
                                      "owner":user})
    course_id = result.fetchone()[0]
    sql = "INSERT INTO course_rights (course_id, user_id, can_read) " \
          "VALUES (:course_id, :user_id, :can_read)"
    result = db.session.execute(sql, {"course_id":course_id, 
                                      "user_id":"0", 
                                      "can_read":public})
    db.session.execute("INSERT INTO course_rights " \
                       "(course_id, user_id, can_read) " \
                       "VALUES (:course_id, :user_id, :can_read)", 
                       {"course_id":course_id, 
                        "user_id":user, 
                        "can_read":"true"})
    db.session.commit()
    return course_id

def create_course_page(title, content, course_id, qtitle, answer,
                       answeropt, question, type, assignment):
    sql = "INSERT INTO pages (title, course_id, modified) " \
          "VALUES (:title, :course_id, NOW()) " \
          "RETURNING ID"
    result = db.session.execute(sql, {"title":title, 
                                      "course_id":course_id})
    page_id = result.fetchone()[0]
    order_number = 1
    assignment_i = 0
    text_i = 0
    for block in type:
        if block == "assignment":
            sql = "INSERT INTO assignments " \
                  "(title, assignment, answer, " \
                  "course_id, page_id, order_number) " \
                  "VALUES (:title, :assignment, :answer, " \
                  ":course_id, :page_id, :order_number) " \
                  "RETURNING ID"
            question_id = db.session.execute(sql, 
                {"title":qtitle[assignment_i],
                "assignment":assignment[assignment_i], 
                "answer":answer[assignment_i], 
                "course_id":course_id, 
                "page_id":page_id, 
                "order_number":order_number})
            qid = question_id.fetchone()[0]
            assignment_i += 1
            order_number += 1
            opti = 1
            for y in range((assignment_i-1)*3, assignment_i*3):
                option = answeropt[y]
                sql = "INSERT INTO options " \
                      "(option, question_id, option_id) " \
                      "VALUES (:option, :question_id, :option_id)"
                db.session.execute(sql, 
                    {"option":option, 
                    "question_id":qid, 
                    "option_id":opti})
                opti += 1
                db.session.commit()
        elif block == "text":
            sql = "INSERT INTO content " \
                  "(content, course_id, page_id, order_number) " \
                  "VALUES (:content, :course_id, :page_id, :order_number)"
            db.session.execute(sql, 
                {"content":content[text_i], 
                "course_id":course_id, 
                "page_id":page_id, 
                "order_number":order_number})
            db.session.commit()
            order_number += 1
            text_i += 1
    return page_id

def modify_course_page(title, content, course_id, 
                       qtitle, answer, answeropt, 
                       question, type, assignment, page_id):
    sql = "DELETE FROM assignments WHERE page_id=:page_id"
    db.session.execute(sql, {"page_id":page_id})
    sql2 = "DELETE FROM content WHERE page_id=:page_id"
    db.session.execute(sql2, {"page_id":page_id})
    sqltitle = "UPDATE pages SET title=:title WHERE id=:page_id"
    db.session.execute(sqltitle, {"title":title, "page_id":page_id})
    order_number = 1
    assignment_i = 0
    text_i = 0
    for block in type:
        if block == "assignment":
            sql = "INSERT INTO assignments " \
                  "(title, assignment, answer, " \
                  "course_id, page_id, order_number) " \
                  "VALUES (:title, :assignment, :answer, " \
                  ":course_id, :page_id, :order_number) " \
                  "RETURNING ID"
            question_id = db.session.execute(sql, 
                {"title":qtitle[assignment_i], 
                "assignment":assignment[assignment_i], 
                "answer":answer[assignment_i], 
                "course_id":course_id, 
                "page_id":page_id, 
                "order_number":order_number})
            qid = question_id.fetchone()[0]
            assignment_i += 1
            order_number += 1
            opti = 1
            for y in range((assignment_i-1)*3, assignment_i*3):
                option = answeropt[y]
                sql = "INSERT INTO options " \
                      "(option, question_id, option_id) " \
                      "VALUES (:option, :question_id, :option_id)"
                db.session.execute(sql, 
                    {"option":option, 
                    "question_id":qid, 
                    "option_id":opti})
                opti += 1
        elif block == "text":
            sql = "INSERT INTO content " \
                  "(content, course_id, page_id, order_number) " \
                  "VALUES (:content, :course_id, :page_id, :order_number)"
            db.session.execute(sql, 
                {"content":content[text_i], 
                "course_id":course_id, 
                "page_id":page_id, 
                "order_number":order_number})
            order_number += 1
            text_i += 1
    db.session.commit()
    return page_id

def get_course(id):
    sql = "SELECT title, content FROM courses WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    list = result.fetchall()
    return list

def get_materials(id):
    sql = "SELECT title, id FROM pages WHERE course_id=:id"
    result = db.session.execute(sql, {"id":id})
    materials = result.fetchall()
    return materials

def get_material(page_id):
    sql = "SELECT title, c.content, order_number " \
          "FROM content C LEFT JOIN pages P " \
          "ON C.course_id=P.course_id AND C.page_id = P.id " \
          "WHERE page_id=:page_id"
    result = db.session.execute(sql, {"page_id":page_id})
    materials = result.fetchall()
    if len(materials) == 0:
        sql = "SELECT title FROM pages WHERE id=:page_id"
        result = db.session.execute(sql, {"page_id":page_id})
        materials = [[result.fetchone()[0]]]
    return materials

def get_assignments(page_id):
    sql = "SELECT assignments.id, title, assignment, " \
          "order_number, option, option_id " \
          "FROM assignments LEFT JOIN options " \
          "ON assignments.id=question_id " \
          "WHERE page_id=:page_id"
    result = db.session.execute(sql, {"page_id":page_id})
    assignments = result.fetchall()
    return assignments

def get_assignments_modify(page_id):
    sql = "SELECT assignments.id, title, assignment, " \
          "order_number, option, option_id, answer " \
          "FROM assignments LEFT JOIN options " \
          "ON assignments.id=question_id " \
          "WHERE page_id=:page_id"
    result = db.session.execute(sql, {"page_id":page_id})
    assignments = result.fetchall()
    return assignments

def get_answer(question_id):
    sql = "SELECT answer FROM assignments WHERE id=:question_id"
    result = db.session.execute(sql, {"question_id":question_id})
    answer = result.fetchone()[0]
    return answer

def insert_answer(question_id, answer, user_id, result):
    sql = "INSERT INTO progression " \
          "(assignment_id, user_id, answer_id, correct) " \
          "VALUES (:assignment_id, :user_id, :answer_id, :correct)"
    result = db.session.execute(sql, 
        {"assignment_id":question_id, 
        "user_id":user_id, 
        "answer_id":answer, 
        "correct":result})
    db.session.commit()
    return

def get_page_answers(username, page_id):
    sql = "SELECT id, correct, answer_id " \
          "FROM assignments " \
          "LEFT JOIN progression ON id = assignment_id " \
          "WHERE page_id=:page_id " \
          "AND (correct = true OR correct is NULL) " \
          "AND user_id=:user_id"
    result = db.session.execute(sql, {"user_id":username, "page_id":page_id})
    answers = result.fetchall()
    return answers
