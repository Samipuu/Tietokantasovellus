from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from flask import session
import os

def create_account(username, password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username, password) " \
              "VALUES (:username, :password)"
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
    except:
        return False
    return True

def login(username, password):
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        return "Unknown user"
    else:
        hash_value = user[0]
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["level"] = get_security_level(username)
            session["csrf_token"] = os.urandom(16).hex()
            return "Success"
        else:
            return "Incorrect password"

def get_security_level(username):
    sql = "SELECT security_level FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    answer = result.fetchone()[0]
    return answer

def check_owner(course, username):
    sql = "SELECT users.username " \
          "FROM courses " \
          "LEFT JOIN users ON courses.owner = users.id " \
          "WHERE courses.id=:course"
    result = db.session.execute(sql, {"course":course})
    answer = result.fetchone()[0]
    return answer == username

def check_pupil(csrf_token):
    if session.get("username") is not None:
        if session["csrf_token"] != csrf_token:
            return True
        user = session["username"]
        level = get_security_level(user)
        return level == 1
    return True

def get_user_id(username):
    try:
        sql = "SELECT id FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        id = result.fetchone()[0]
    except:
        return None
    return id

def get_course_rights(course_id):
    sql = "SELECT username, can_read, user_id " \
          "FROM course_rights " \
          "LEFT JOIN users ON user_id = id " \
          "WHERE course_id=:course_id " \
          "AND (can_read = true or user_id = 0)"
    result = db.session.execute(sql, {"course_id":course_id})
    users = result.fetchall()
    return users

def update_course_rights(users, rights):
    for i in range(len(users)):
        if rights[i] == "read":
            can_read = "true"
        elif rights[i] == "blocked":
            can_read = "false"
        else:
            continue
        sql = "UPDATE course_rights " \
              "SET can_read = :right " \
              "WHERE user_id =:user"
        db.session.execute(sql, {"right":can_read, "user":users[i]})
    db.session.commit()

def add_course_rights(users, rights, course_id):
    for i in range(len(users)):
        if rights[i] == "Luku":
            can_read = "true"
        elif rights[i] == "Estetty":
            continue
        else:
            continue
        sql = "INSERT INTO course_rights (course_id, user_id, can_read) " \
              "VALUES (:course_id, :user_id, :can_read)"
        result = db.session.execute(sql, {"course_id":course_id, "user_id":users[i], "can_read":can_read})
    db.session.commit()

def modify_users(users, rights):
    for i in range(len(users)):
        sql = "UPDATE users SET security_level=:level WHERE username =:user"
        db.session.execute(sql, {"level":rights[i], "user":users[i]})
    db.session.commit()

def get_users():
    users = db.session.execute("SELECT username, security_level FROM users")
    return users

def check_access(username, id):
    if not username == "public":
        user_id = get_user_id(username)
    else:
        user_id = 0
    sql = "SELECT can_read " \
          "FROM course_rights " \
          "WHERE course_id=:id " \
          "AND (user_id=:user OR user_id = 0) " \
          "ORDER BY can_read DESC"
    result = db.session.execute(sql, {"id":id, "user":user_id})
    access = result.fetchone()[0]
    if access == True:
        return True
    return False

def post_modify_course(csrf_token, course_id):
    if session.get("username") is not None:
        if session["csrf_token"] != csrf_token:
            return False
        if check_owner(course_id, session["username"]):
            return True
        if get_security_level(session["username"]) == 3:
            return True
    return False

def get_modify_course(course_id):
    if session.get("username") is not None:
        if check_owner(course_id, session["username"]):
            return True
        if get_security_level(session["username"]) == 3:
            return True
    return False

def password_change(csrf_token, old_password, new_password):
    if csrf_token != session["csrf_token"]:
        abort(403)
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":session["username"]})
    user = result.fetchone()
    hash_value = user[0]
    new_hash = generate_password_hash(new_password)
    if check_password_hash(hash_value, old_password):
        sql = "UPDATE users " \
              "SET password=:new_hash " \
              "WHERE username=:username"
        result = db.session.execute(sql, {"new_hash":new_hash, 
                                          "username":session["username"]})
        db.session.commit()
        return True
    else:
        return False

def delete(csrf_token, password):
    if csrf_token != session["csrf_token"]:
        abort(403)
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":session["username"]})
    user = result.fetchone()
    hash_value = user[0]
    if check_password_hash(hash_value, password):
        sql = "DELETE FROM users WHERE username=:username RETURNING id"
        result = db.session.execute(sql, {"username":session["username"]})
        user_id = result.fetchone()[0]
        sql_course = "DELETE FROM course_rights WHERE user_id=:user_id"
        db.session.execute(sql_course, {"user_id":user_id})
        db.session.commit()
        return True
    else:
        return False

