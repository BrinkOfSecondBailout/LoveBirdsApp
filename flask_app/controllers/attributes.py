from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for, Response
from flask_app.models import user, attribute, image


@app.route('/attributes/new')
def new_attributes():
    data = {
        'user_id': session['user_id']
    }

    id = session['user_id']

    all_pics = image.Photo.query.filter_by(user=id).all()

    user1 = user.User.get_info_by_id(data)
    if user1.suspended == "yes":
        return redirect('/suspended')

    for pic in all_pics:
        if(pic.profile == "yes"):
            profile_pic = pic
            return render_template('new_attributes.html', profile=profile_pic, user=user1)

    return render_template('new_attributes.html', user=user1)

@app.route('/attributes/create', methods=['POST'])
def create_attributes():
    if not session:
        return redirect('/logout')
    if not attribute.Attribute.validate_attribute(request.form):
        return redirect('/attributes/new')
    data = {
        'description': request.form['description'],
        'age': request.form['age'],
        'gender': request.form['gender'],
        'smoker': request.form['smoker'],
        'drinker': request.form['drinker'],
        'dating_goal': request.form['dating_goal'],
        'hobbies': request.form['hobbies'],
        'body_type': request.form['body_type'],
        'user_id': session['user_id'],
        'instagram': request.form['instagram'],
        'facebook': request.form['facebook'],
        'twitter': request.form['twitter']
    }
    attribute.Attribute.save_attribute(data)
    return redirect('/users/edit')

@app.route('/attributes/edit')
def update_attributes():
    data = {
        'user_id': session['user_id']
    }
    
    id = session['user_id']
    all_pics = image.Photo.query.filter_by(user=id).all()
    user1 = user.User.get_info_by_id(data)
    if user1.suspended == "yes":
        return redirect('/suspended')
    
    for pic in all_pics:
        if(pic.profile == "yes"):
            profile_pic = pic
            return render_template('update_attributes.html', attribute=attribute.Attribute.get_attribute_by_user_id(data), profile=profile_pic, user=user1)
    return render_template('update_attributes.html', attribute=attribute.Attribute.get_attribute_by_user_id(data), user=user1)

@app.route('/attributes/update', methods=['POST'])
def process_update_attributes():
    if not session:
        return redirect('/logout')
    if not attribute.Attribute.validate_attribute(request.form):
        return redirect('/attributes/edit')
    data = {
        'description': request.form['description'],
        'age': request.form['age'],
        'gender': request.form['gender'],
        'smoker': request.form['smoker'],
        'drinker': request.form['drinker'],
        'dating_goal': request.form['dating_goal'],
        'hobbies': request.form['hobbies'],
        'body_type': request.form['body_type'],
        'user_id': session['user_id'],
        'instagram': request.form['instagram'],
        'facebook': request.form['facebook'],
        'twitter': request.form['twitter']
    }
    attribute.Attribute.update_attribute(data)
    return redirect('/users/edit')