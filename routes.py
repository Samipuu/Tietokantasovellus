from app import app
from flask import Flask
from flask import render_template, redirect, request, jsonify, session, flash
from os import getenv
import db

app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    result = db.login(username, password)
    if result == "Success":
        session["username"] = username
        session["level"] = db.get_security_level(username)
        return redirect("/")
    else:
        flash("Invalid credentials. Try again.")
        return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    del session["level"]
    return redirect("/")

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        result = db.create_account(username, password)
        session["username"] = result
        session["level"] = 1
        return redirect("/")
    else:
        return render_template("create_account.html")

@app.route("/courses")
def courses():
    user_id = 0
    if session.get("username") is not None:
        user_id = db.get_user_id(session["username"])
    courses = db.get_courses(user_id)
    return render_template("courses.html", courses=courses)

@app.route("/newcourse")
def new_course():
    return render_template("newcourse.html")

@app.route("/createcourse", methods=["POST"])
def create_course():
    if db.check_pupil(session):
        return redirect("/courses")
    title = request.form["title"]
    content = request.form["content"]
    public = request.form["public"]
    db.create_course(title, content, session["username"], public)
    return redirect("/courses")

@app.route("/course/<int:id>")
def course(id):
   course = db.get_course(id)
   title = course[0][0]
   content = course[0][1]
   material = db.get_materials(id)
   owner = False
   if session.get("username") is not None:
       owner = db.check_owner(id, session["username"])
   return render_template("course.html", id=id, title=title, content=content, materials = material, owner = owner)

@app.route("/course/<int:id>/createpage/", methods=["GET", "POST"])
def create_page(id):
    if request.method == "POST":
        if db.check_pupil(session):
            return redirect("/courses")
        course_id = request.form["id"]
        title = request.form["title"]
        content = request.form.getlist("content")
        qtitle = request.form.getlist("qtitle")
        assignment = request.form.getlist("question")
        answer = request.form.getlist("answer")
        answeropt = request.form.getlist("answeropt")
        question = request.form.getlist("question")
        type = request.form.getlist("type")
        result = db.create_course_page(title, content, course_id, qtitle, answer, answeropt, question, type, assignment)
        return redirect("/course/"+str(id)+"/"+str(result))
    else:
       return render_template("newpage.html", id=id)

@app.route("/course/<int:id>/<int:mid>")
def course_material(id, mid):
    course_id = id
    page_id = mid
    material = db.get_material(page_id)
    assignments = db.get_assignments(page_id)
    answers = {}
    if session.get("username") is not None:
        answers = db.get_page_answers(db.get_user_id(session["username"]), page_id)
    return render_template("material.html", id=course_id, content=material, assignments=assignments, answers=answers, page_id=page_id)

@app.route("/check_answer")
def check_answer():
    question_id = request.args.get("question_id", type=int)
    answer = request.args.get("answer_val", type=int)
    correct_answer = db.get_answer(question_id)
    result = answer == correct_answer
    if session.get("username") is not None:
        user_id = db.get_user_id(session["username"])
        db.insert_answer(question_id, answer, user_id, result)
    if result:
        return jsonify(disable="true", val=question_id)
    else:
        return jsonify(disable="false", val=question_id)

@app.route("/modify/<int:course_id>/<int:page_id>", methods=["POST", "GET"])
def modify(course_id, page_id):
    if request.method == "POST":
        if session.get("username") is not None:
            if db.check_owner(course_id, session["username"]):
                rights = True
            elif db.get_security_level(session["username"]) == 3:
                rights = True
            else:
                return redirect("/")
        else:
            return redirect ("/")
        course_id = request.form["id"]
        page_id = request.form["page_id"]
        title = request.form["title"]
        content = request.form.getlist("content")
        qtitle = request.form.getlist("qtitle")
        assignment = request.form.getlist("question")
        answer = request.form.getlist("answer")
        answeropt = request.form.getlist("answeropt")
        question = request.form.getlist("question")
        type = request.form.getlist("type")
        result = db.modify_course_page(title, content, course_id, qtitle, answer, answeropt, question, type, assignment, page_id)
        return redirect("/course/"+str(course_id)+"/"+str(result))
    else:
        material = db.get_material(page_id)
        assignments = db.get_assignments_modify(page_id)
        return render_template("modify.html", material=material, assignments=assignments, page_id=page_id, course_id=course_id)

@app.route("/course/<int:course_id>/rights", methods=["POST", "GET"])
def course_rights(course_id):
    if request.method == "POST":
        if session.get("username") is not None:
            if db.check_owner(course_id, session["username"]):
                rights = True
            elif db.get_security_level(session["username"]) == 3:
                rights = True
            else:
                return redirect("/")
        else:
            return redirect ("/")
        current_users = request.form.getlist("current")
        current_rights = request.form.getlist("select")
        new_users = request.form.getlist("newuser")
        new_rights = request.form.getlist("right")
        db.update_course_rights(current_users, current_rights)
        user_list = []
        right_list = []
        for i in range(len(new_users)):
            check = db.get_user_id(new_users[i])
            if check == None:
                flash("Käyttäjää " + new_users[i] + " ei löydy")
            else:
                user_list.append(check)
                right_list.append(new_rights[i])
        db.add_course_rights(user_list, right_list, course_id)
        return redirect("/course/" + str(course_id) + "/rights")
    else:
        users = db.get_course_rights(course_id)
        return render_template("course_rights.html", users=users, id=course_id)

@app.route("/adminpage", methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        if session.get("username") is not None:
            if db.get_security_level(session["username"]) != 3:
                return redirect("/")
        else:
            return redirect("/")
        users = request.form.getlist("users")
        rights = request.form.getlist("level")
        db.modify_users(users, rights)
        return redirect("/adminpage")
    else:
        if session.get("username") is not None:
            if db.get_security_level(session["username"]) != 3:
                return redirect("/")
        else:
            return redirect("/")
        users = db.get_users()
        return render_template("adminpage.html", users=users)

