from flask_app.models.db import db_init, db
from werkzeug.utils import secure_filename
from flask_app.models import user, image
from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for, Response


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Photo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload/<int:id>', methods=['POST'])
def upload_pic(id):
    pic = request.files['pic']
    if not pic:
        flash('No image has been selected!', 'upload')
        return redirect('/users/edit')
    if not allowed_file(pic.filename):
        flash('Allowed image types are - png, jpg, jpeg, gif', 'upload')
        return redirect('/users/edit')
    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    userid = int(id)
    img = image.Photo(img=pic.read(), name=filename, mimetype=mimetype, user=userid, profile="no")
    db.session.add(img)
    db.session.commit()
    flash('Upload successful!', 'upload')
    return redirect('/users/edit')


@app.route('/pics/<int:id>')
def get_img(id):
    img = image.Photo.query.filter_by(id=id).first()
    if not img:
        return "No image with that id", 404
    return Response(img.img, mimetype=img.mimetype)


@app.route('/pics/delete/<int:id>')
def delete_img(id):
    img = image.Photo.query.filter_by(id=id).first()
    if not img:
        return "No image with that id", 404
    db.session.delete(img)
    db.session.commit()
    return redirect('/users/edit')


@app.route('/makeprofile/<int:id>')
def make_profile_pic(id):
    user_id = session['user_id']
    all_pics = image.Photo.query.filter_by(user=user_id).all()
    for pic in all_pics:
        if(pic.profile == "yes"):
            pic.profile = "no"
            db.session.commit()
        if(pic.id == id):
            pic.profile = "yes"
            db.session.commit()
    return redirect('/users/edit')
