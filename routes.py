from app import app
from flask import Flask
from flask import render_template, redirect, request
import db

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/courses")
def courses():
	courses = db.get_courses()
	return render_template("courses.html", courses=courses)

@app.route("/newcourse")
def new_course():
	return render_template("newcourse.html")

@app.route("/createcourse", methods=["POST"])
def create_course():
	title = request.form["title"]
	content = request.form["content"]
	db.create_course(title, content)
	return redirect("/courses")

@app.route("/course/<int:id>")
def course(id):
	course = db.get_course(id)
	title = course[0][0]
	content = course[0][1]
	material = db.get_materials(id)
	return render_template("course.html", id=id, title=title, content=content, materials = material)

@app.route("/course/<int:id>/createpage/", methods=["GET", "POST"])
def create_page(id):
	if request.method == "POST":
		course_id = request.form["id"]
		title = request.form["title"]
		content = request.form.getlist("content")
		qtitle = request.form.getlist("qtitle")
		answer = request.form.getlist("answer")
		answeropt = request.form.getlist("answeropt")
		question = request.form.getlist("question")
		result = db.create_course_page(title, content, course_id, qtitle, answer, answeropt, question)
		return redirect("/course/"+str(id)+"/"+str(result))
	else:
		return render_template("newpage.html", id=id)

@app.route("/course/<int:id>/<int:mid>")
def course_material(id, mid):
	course_id = id
	page_id = mid
	material = db.get_material(course_id, page_id)
	#assignments = db.get_assignments(course_id, page_id)
	return render_template("material.html", id=course_id, content=material)
