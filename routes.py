from app import app
from flask import Flask
from flask import render_template, redirect, request, jsonify, session, flash, abort
from os import getenv
import security
import course

app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    result = security.login(username, password)
    if result == "Success":
        return redirect(request.referrer)
    else:
        flash("Invalid credentials. Try again.")
        return redirect(request.referrer)

@app.route("/logout")
def logout():
    del session["username"]
    del session["level"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        result = security.create_account(username, password)
        if not result:
            flash("Käyttäjänimi on jo käytössä. Yritä uudelleen.")
            return render_template("create_account.html")
        security.login(username, password)
        return redirect("/")
    else:
        return render_template("create_account.html")

@app.route("/courses")
def courses():
    user_id = 0
    if session.get("username") is not None:
        user_id = security.get_user_id(session["username"])
    courses = course.get_courses(user_id)
    return render_template("courses.html", courses=courses)

@app.route("/newcourse")
def new_course():
    return render_template("newcourse.html")

@app.route("/createcourse", methods=["POST"])
def create_course():
    csrf_token = request.form["csrf_token"]
    if security.check_pupil(csrf_token):
        abort(403)
    title = request.form["title"]
    content = request.form["content"]
    public = request.form["public"]
    course.create_course(title, content, session["username"], public)
    return redirect("/courses")

@app.route("/course/<int:id>")
def course_page(id):
    course_page = course.get_course(id)
    title = course_page[0][0]
    content = course_page[0][1]
    material = course.get_materials(id)
    owner = False
    if session.get("username") is not None:
        owner = security.check_owner(id, session["username"])
        if security.check_access(session.get("username"), id) == False:
            abort(403)
    else:
        if security.check_access("public", id) == False:
            abort(403)
    return render_template("course.html", 
        id=id, title=title, content=content, 
        materials = material, owner = owner)

@app.route("/course/<int:id>/createpage/", methods=["GET", "POST"])
def create_page(id):
    if request.method == "POST":
        csrf_token = request.form["csrf_token"]
        if security.check_pupil(csrf_token):
            abort(403)
        course_id = request.form["id"]
        title = request.form["title"]
        content = request.form.getlist("content")
        qtitle = request.form.getlist("qtitle")
        assignment = request.form.getlist("question")
        answer = request.form.getlist("answer")
        answeropt = request.form.getlist("answeropt")
        question = request.form.getlist("question")
        type = request.form.getlist("type")
        result = course.create_course_page(title, 
            content, course_id, qtitle, answer, 
            answeropt, question, type, assignment)
        return redirect("/course/"+str(id)+"/"+str(result))
    else:
       materials = course.get_materials(id)
       return render_template("newpage.html", id=id, materials=materials)

@app.route("/course/<int:id>/<int:mid>")
def course_material(id, mid):
    course_id = id
    page_id = mid
    material = course.get_material(page_id)
    pages = course.get_materials(course_id)
    assignments = course.get_assignments(page_id)
    answers = {}
    modify = False
    if session.get("username") is not None:
        answers = course.get_page_answers(
            security.get_user_id(session["username"]), page_id)
        if not security.check_access(session.get("username"), course_id):
            return abort(403)
        modify = security.get_modify_course(course_id)
    else:
        if not security.check_access("public", course_id):
            return abort(403)
    return render_template("material.html", 
        id=course_id, 
        content=material, 
        assignments=assignments, 
        answers=answers, 
        page_id=page_id,
        materials=pages,
        owner=modify)

@app.route("/check_answer")
def check_answer():
    question_id = request.args.get("question_id", type=int)
    answer = request.args.get("answer_val", type=int)
    correct_answer = course.get_answer(question_id)
    result = answer == correct_answer
    if session.get("username") is not None:
        user_id = security.get_user_id(session["username"])
        course.insert_answer(question_id, answer, user_id, result)
    if result:
        return jsonify(disable="true", val=question_id)
    else:
        return jsonify(disable="false", val=question_id)

@app.route("/modify/<int:course_id>/<int:page_id>", methods=["POST", "GET"])
def modify(course_id, page_id):
    if request.method == "POST":
        csrf_token = request.form["csrf_token"]
        if not security.post_modify_course(csrf_token, course_id):
            abort(403)
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
        result = course.modify_course_page(
            title, content, course_id, qtitle, 
            answer, answeropt, question, type, 
            assignment, page_id)
        return redirect("/course/"+str(course_id)+"/"+str(result))
    else:
        modify = security.get_modify_course(course_id)
        if not modify:
            abort(403)
        pages = course.get_materials(course_id)
        material = course.get_material(page_id)
        assignments = course.get_assignments_modify(page_id)
        return render_template("modify.html", 
            material=material, 
            assignments=assignments, 
            page_id=page_id, 
            course_id=course_id,
            materials=pages,
            owner=modify)

@app.route("/course/<int:course_id>/rights", methods=["POST", "GET"])
def course_rights(course_id):
    if request.method == "POST":
        csrf_token = request.form["csrf_token"]
        if not security.post_modify_course(csrf_token, course_id):
            abort(403)
        current_users = request.form.getlist("current")
        current_rights = request.form.getlist("select")
        new_users = request.form.getlist("newuser")
        new_rights = request.form.getlist("right")
        security.update_course_rights(current_users, current_rights)
        user_list = []
        right_list = []
        for i in range(len(new_users)):
            check = security.get_user_id(new_users[i])
            if check == None:
                flash("Käyttäjää " + new_users[i] + " ei löydy")
            else:
                user_list.append(check)
                right_list.append(new_rights[i])
        security.add_course_rights(user_list, right_list, course_id)
        return redirect("/course/" + str(course_id) + "/rights")
    else:
        if not security.get_modify_course(course_id):
            abort(403)
        material = course.get_materials(course_id)
        users = security.get_course_rights(course_id)
        return render_template("course_rights.html", users=users, id=course_id, materials=material)

@app.route("/adminpage", methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        if session.get("username") is not None:
            if security.get_security_level(session["username"]) != 3:
                abort(403)
        else:
            abort(403)
        users = request.form.getlist("users")
        rights = request.form.getlist("level")
        security.modify_users(users, rights)
        return redirect("/adminpage")
    else:
        if session.get("username") is not None:
            if security.get_security_level(session["username"]) != 3:
                abort(403)
        else:
            abort(403)
        users = security.get_users()
        return render_template("adminpage.html", users=users)

@app.route("/profile", methods=["POST", "GET"])
def profile():
    if request.method == "POST":
        if session.get("username") is None:
            abort(403)
        csrf_token = request.form["csrf_token"]
        old_password = request.form["oldPassword"]
        new_password = request.form["newPassword"]
        result = security.password_change(csrf_token, old_password, new_password)
        if result:
            flash("Salasana vaihdettu")
        else:
            flash("Salasanan vaihto epäonnistui. Yritä uudelleen")
        return render_template("profile.html")
    else:
        if session.get("username") is None:
            abort(403)
        return render_template("profile.html")


@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        if session.get("username") is None:
            abort(403)
        csrf_token = request.form["csrf_token"]
        password = request.form["password"]
        result = security.delete(csrf_token, password)
        if not result:
            flash("Tunnuksen poisto epäonnistui. Yritä uudelleen")
            return render_template("profile.html")
        logout()
        return redirect("/")
    else:
        if session.get("username") is None:
            abort(403)
        return render_template("delete.html")
