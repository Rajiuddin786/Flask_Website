from flask import Flask,render_template,redirect,request,session,send_file
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from io import BytesIO
import gridfs


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mongo_client = MongoClient("mongodb+srv://skrajiuddin18:Raj24032003@cluster0.i1pmhyj.mongodb.net/")
db1 = mongo_client["admin_"]
collection = db1["admin_"]
fs1=gridfs.GridFS(db1)
db2= mongo_client["local_"]
fs2=gridfs.GridFS(db2)


@app.route("/")
def home():
    image_files1 = [
        {"_id": str(image._id), "filename": image.filename}
        for image in fs1.find()
    ]
    image_files2 = [
        {"_id": str(image._id), "filename": image.filename,"title": image.title, "description": image.description}
        for image in fs2.find()
    ]
    images = {"image_files1": image_files1,
             "image_files2": image_files2}
    return render_template("index.html",images=images)

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
    if collection.find_one({"username": session.get("username")}):
        if session.get("username"):
            image_files = [
        {"_id": str(image._id), "filename": image.filename,"title": image.title, "description": image.description}
        for image in fs2.find()
    ]
            return render_template("admin.html",images=image_files)
        else:
            return redirect("/login")
    else:
        return redirect("/login")

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No file part"
    image = request.files['image']
    title = request.form['title']
    description = request.form['description']
    if image.filename == '':
        return "No selected file"

    file_id = fs2.put(image, filename=image.filename,title=title, description=description)
    return redirect("/admin")

        
@app.route("/delete/<image_id>",methods=["POST"])
def delete(image_id):
    if request.method == "POST":
        image = fs2.get(ObjectId(image_id))
        fs2.delete(image._id)
        return redirect("/admin")
    
@app.route('/image/<filename>')
def index_image(filename):
    image = fs1.find_one({'filename': filename})
    if image:
        return send_file(BytesIO(image.read()), mimetype='image/jpeg')
    else:
        return "Image not found", 404

@app.route('/gallery/<image_id>')
def image(image_id):
    image = fs2.get(ObjectId(image_id))
    if image:
        return send_file(BytesIO(image.read()), mimetype='image/jpeg')
    else:
        return "Image not found", 404


if __name__ == "__main__":
    app.run()