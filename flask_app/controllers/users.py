from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models import user, image, attribute, wallnote
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/process/registration', methods=['POST'])
def process_registration():
    if not user.User.validate_registration(request.form):
        return redirect('/')
    else:
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password'])
        }
        user.User.save_user(data)
        return redirect('/')


@app.route('/process/login', methods=['POST'])
def process_login():
    user1 = user.User.validate_login(request.form)
    if not user1:
        return redirect('/')
    if not bcrypt.check_password_hash(user1['password'], request.form['password']):
        flash('Incorrect password! Try again.', 'login')
        return redirect('/')
    else:
        session['user_id'] = user1['id']
        data = {
            'user_id': session['user_id']
        }
        return redirect('/dashboard')
    
@app.route('/dashboard')
def dashboard():
    if not session:
        return redirect('/logout')
    data = {
        'user_id': session['user_id']
    }
    id = session['user_id']

    all_pics = image.Photo.query.filter_by(user=id).all()
    
    all_users = user.User.get_all_users()
    
    data2 = {
        'id': session['user_id']
    }
    user_with_matches = user.User.get_me_with_all_my_hearts(data2)

    wall_notes = wallnote.Wallnote.get_all_notes_with_users()

    user1 = user.User.get_info_by_id(data)
    if user1.suspended == "yes":
        return redirect('/suspended')

    for pic in all_pics:
        if(pic.profile == "yes"):
            profile_pic = pic
            return render_template('dashboard.html', all_users=all_users, profile=profile_pic, user=user1, user_with_matches=user_with_matches, wall_notes = wall_notes)

    return render_template('dashboard.html', all_users=all_users, user=user1, user_with_matches=user_with_matches, wall_notes=wall_notes)



@app.route('/users/edit')
def edit_profile():
    if not session:
        return redirect('/logout')
    data = {
        'user_id': session['user_id']
    }
    id = session["user_id"]
    all_pics = image.Photo.query.filter_by(user=id).all()
    if not all_pics:
        return render_template('edit_profile.html', user=user.User.get_info_by_id(data), attributes=attribute.Attribute.get_attribute_by_user_id(data))
    
    for pic in all_pics:
        if(pic.profile == "yes"):
            profile_pic = pic
            return render_template('edit_profile.html', user=user.User.get_info_by_id(data), pics=all_pics, profile=profile_pic, attributes=attribute.Attribute.get_attribute_by_user_id(data))

    return render_template('edit_profile.html', user=user.User.get_info_by_id(data), pics=all_pics, attributes=attribute.Attribute.get_attribute_by_user_id(data))

@app.route('/users/update', methods=['POST'])
def update_profile():
    if not session:
        return redirect('/logout')
    if not user.User.validate_edit(request.form):
        return redirect('/users/edit')
    data = {
        'id': session['user_id'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email']
    }
    user.User.update_user(data)
    return redirect('/dashboard')

@app.route('/changepw')
def change_pw():
    if not session:
        return redirect('/logout')
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
            return render_template('change_pw.html', profile=profile_pic, user=user1)

    return render_template('change_pw.html', profile=profile_pic, user=user1)

@app.route('/updatepw', methods=['POST'])
def update_pw():
    if not session:
        return redirect('/logout')
    if not user.User.validate_password(request.form):
        return redirect('/changepw')
    data = {
        'password': bcrypt.generate_password_hash(request.form['password']),
        'id': session['user_id']
    }
    user.User.update_password(data)
    return redirect('/users/edit')


@app.route('/users/<int:id>')
def show_profile(id):
    if not session:
        return redirect('/logout')

    data1 = {
        'blocker_id': session['user_id'],
        'blocked_id': id
    }
    if user.User.check_if_im_blocked(data1):
        return redirect('/dashboard')

    data = {
        'user_id': id
    }

    data2 = {
        'user_id': session['user_id']
    }
    
    attributes = attribute.Attribute.get_attribute_by_user_id(data)
    all_pics = image.Photo.query.filter_by(user=id).all()

    me=user.User.get_info_by_id(data2)

    if not all_pics:
        flash('This user has not uploaded any pics yet!', 'upload')
        return render_template('display_profile.html', me=me, user=user.User.get_info_by_id(data), attributes=attributes)
    
    for pic in all_pics:
        if(pic.profile == "yes"):
            profile_pic = pic
            return render_template('display_profile.html', me=me, user=user.User.get_info_by_id(data), pics=all_pics, profile=profile_pic, attributes=attributes)
        
    return render_template('display_profile.html', me=me, user=user.User.get_info_by_id(data), pics=all_pics, attributes=attributes)


@app.route('/sendheart/<int:id>')
def send_a_heart(id):
    if not session:
        return redirect('/logout')
    data = {
        'user_id': session['user_id'],
        'match_id': id
    }
    data1 = {
        'id': session['user_id']
    }
    if not user.User.send_heart(data):
        return redirect('/users/' + str(id))

    if user.User.check_if_we_match(data1):
        data2 = {
            'user_id': id
        }
        id = session['user_id']


        all_pics = image.Photo.query.filter_by(user=id).all()

        user1 = user.User.get_info_by_id(data)

        match = user.User.get_info_by_id(data2)
        for pic in all_pics:
            if(pic.profile == "yes"):
                profile_pic = pic
                return render_template('matched_up.html', profile=profile_pic, match=match, user=user1)
        return render_template('matched_up.html', match=match, user=user1)

    # return redirect('/users/' + str(id))
    return redirect('/dashboard')


@app.route('/unsend/<int:id>')
def unsend_a_heart(id):
    if not session:
        return redirect('/logout')
    data = {
        'user_id': session['user_id'],
        'id': id
    }
    user.User.unsend_heart(data)

    return redirect('/dashboard')



@app.route('/block/<int:id>')
def block_user(id):
    if not session:
        return redirect('/logout')
    data = {
        'user_id': id
    }
    user1 = user.User.get_info_by_id(data)
    return render_template('block_user.html', user=user1)

@app.route('/block/confirmed/<int:id>', methods=['POST'])
def confirmed_block(id):
    if not session:
        return redirect('/logout')
    if not (request.form.get('reason')):
        flash('Please provide a reason, minimum 10 characters please...', 'block')
        return redirect('/block/' + str(id))
    if len(request.form.get('reason')) < 10:
        flash('Please provide a reason, minimum 10 characters please...', 'block')
        return redirect('/block/' + str(id))
    data = {
        'reason': request.form['reason'],
        'user_id': session['user_id'],
        'id': request.form['id']
    }
    user.User.block_user(data)
    return redirect('/dashboard')


@app.route('/filter')
def filter_out():
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
            return render_template('filter.html', profile=profile_pic, user=user1)
    return render_template('filter.html', profile=profile_pic, user=user1)


@app.route('/users/messages')
def show_message_threads():
    try:
        if not session:
            return redirect('/logout')
        data = {
            'user_id': session['user_id']
        }
        id = session['user_id']
        user.User.reset_new_message_count(data)


        all_pics = image.Photo.query.filter_by(user=id).all()

        user1 = user.User.get_info_by_id(data)
        if user1.suspended == "yes":
            return redirect('/suspended')

        for pic in all_pics:
            if(pic.profile == "yes"):
                profile_pic = pic
                return render_template('message_threads.html', messages=user.User.get_all_messages_by_threads(data), profile=profile_pic, user=user1)

        return render_template('message_threads.html', messages=user.User.get_all_messages_by_threads(data), user=user1)
    except Exception as e:
        return f"An error occured: {str(e)}"


@app.route('/users/inbox/<int:id>')
def inbox_folder(id):
    if not session:
        return redirect('/logout')
    data = {
        'user_id': session['user_id'],
        'other_id': id
    }
    data2 = {
        'user_id': id
    }

    user_id = session['user_id']

    user2 = user.User.get_info_by_id(data2)

    messages = user.User.get_all_messages_for_me_by_one_user(data)

    all_pics = image.Photo.query.filter_by(user=user_id).all()
    all_others_pics = image.Photo.query.filter_by(user=id).all()

    user1 = user.User.get_info_by_id(data)

    if user1.suspended == "yes":
        return redirect('/suspended')

    for pic in all_pics:
        if(pic.profile == "yes"):
            profile_pic = pic
            for pic2 in all_others_pics:
                if(pic2.profile == "yes"):
                    profile_pic2 = pic2
                    return render_template('inbox.html', messages=messages, profile=profile_pic, profile2=profile_pic2, user=user1, user2=user2)
            return render_template('inbox.html', messages=messages, profile=profile_pic, user=user1, user2=user2)

    for pic2 in all_others_pics:
        if(pic2.profile == "yes"):
            profile_pic2 = pic2
            return render_template('inbox.html', profile2=profile_pic2, messages=messages, user=user1, user2=user2)

    return render_template('inbox.html', messages=messages, user=user1, user2=user2)




@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/filter/age', methods=['POST'])
def filter_by_age():
    if not session:
        return redirect('/logout')
    if request.form.get('param') == None or request.form['age'] == None:
        flash("Please check a box and pick an age")
        return redirect('/filter')
    if request.form['param'] == 'above':
        data = {
            'age': int(request.form['age'])
        }
        users = user.User.get_users_by_age_higher_filter(data)
        return render_template('filter_results.html', users=users)
    if request.form['param'] == 'below':
        data = {
            'age': int(request.form['age'])
        }
        users = user.User.get_users_by_age_lower_filter(data)
        return render_template('filter_results.html', users=users)
    return redirect('/filter')


@app.route('/filter/gender', methods=['POST'])
def filter_by_gender():
    if not session:
        return redirect('/logout')
    data = {
        'gender': request.form['gender']
    }
    users = user.User.get_users_by_gender_filter(data)
    return render_template('filter_results.html', users=users)


@app.route('/filter/smoker', methods=['POST'])
def filter_by_smoker():
    if not session:
        return redirect('/logout')
    data = {
        'smoker': request.form['smoker']
    }
    users = user.User.get_users_by_smoker_filter(data)
    return render_template('filter_results.html', users=users)


@app.route('/filter/drinker', methods=['POST'])
def filter_by_drinker():
    if not session:
        return redirect('/logout')
    data = {
        'drinker': request.form['drinker']
    }
    users = user.User.get_users_by_drinker_filter(data)
    return render_template('filter_results.html', users=users)


@app.route('/filter/goal', methods=['POST'])
def filter_by_goal():
    if not session:
        return redirect('/logout')
    data = {
        'dating_goal': request.form['dating_goal']
    }
    users = user.User.get_users_by_goal_filter(data)
    return render_template('filter_results.html', users=users)


@app.route('/filter/hobbies', methods=['POST'])
def filter_by_hobbies():
    if not session:
        return redirect('/logout')
    data = {
        'hobbies': request.form['hobbies']
    }
    users = user.User.get_users_by_hobbies_filter(data)
    return render_template('filter_results.html', users=users)


@app.route('/filter/body', methods=['POST'])
def filter_by_body():
    if not session:
        return redirect('/logout')
    data = {
        'body_type': request.form['body_type']
    }
    users = user.User.get_users_by_body_filter(data)
    return render_template('filter_results.html', users=users)

@app.route('/suspended')
def suspended_user():
    data = {
        'user_id': session['user_id']
    }
    user.User.delete_user(data)
    return render_template('suspended.html')