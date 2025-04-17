import awsgi
from flask import Flask,render_template,redirect,request,session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mongo_client = MongoClient("mongodb+srv://skrajiuddin18:Raj24032003@cluster0.i1pmhyj.mongodb.net/")
db = mongo_client["admin_"]
collection = db["admin_"]
image_collection = db["images"]


@app.route("/")
def home():
    datas=image_collection.find()
    return render_template("index.html",images=datas)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout",methods=["POST"])
def logout():
    if request.method == "POST":
        session.pop("username", None)
        return redirect("/login")

@app.route("/submit",methods=["POST","GET"])
def submit():
    if request.method == "POST":
        session['username'] = request.form['username']
        username = request.form["username"]
        password = request.form["password"]

        data=collection.find_one({"username": username})
        if data:
            if check_password_hash(data["password"], password):
                return redirect("/admin")
            else:
                return redirect("/login")
        else:
            return redirect("/login")

@app.route("/admin")
def admin_page():
    datas=image_collection.find()
    if collection.find_one({"username": session.get("username")}):
        if session.get("username"):
            return render_template("admin.html",images=datas)
        else:
            return redirect("/login")
    else:
        return redirect("/login")

@app.route("/upload",methods=["POST"])
def upload():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        image = request.files["image"]
        image.save(f"static/images/{image.filename}")
        image_data = {
            "title": title,
            "description": description,
            "image_path": f"static/images/{image.filename}"
        }
        image_collection.insert_one(image_data)
        return redirect("/admin")
    return redirect("/admin")
        
@app.route("/delete/<image_id>",methods=["POST"])
def delete(image_id):
    if request.method == "POST":
        image = image_collection.find_one({"_id": ObjectId(image_id)})
        if image:
            os.remove(image["image_path"])
            image_collection.delete_one({"_id": ObjectId(image_id)})
            return redirect("/admin")
        return redirect("/admin")

def lambda_handler(event, context):
    return awsgi.response(app, event, context,base64_content_types={"image/jpeg", "image/png", "image/gif"})

if __name__ == "__main__":
    app.run(debug=True)