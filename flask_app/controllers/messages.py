from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for, Response
from flask_app.models import user, message, image

@app.route('/messages/new/<int:id>')
def new_message(id):
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
    receiver = user.User.get_info_by_id(data)
    data3 = {
        'user_id': session['user_id']
    }
    myId = session['user_id']

    all_pics = image.Photo.query.filter_by(user=myId).all()
    user1 = user.User.get_info_by_id(data3)
    if user1.suspended == "yes":
        return redirect('/suspended')
    for pic in all_pics:
        if(pic.profile == "yes"):
            profile_pic = pic
            return render_template('new_message.html', profile=profile_pic, receiver=receiver, user=user1)
    return render_template('new_message.html', receiver=receiver, user=user1)

@app.route('/messages/process/<int:id>', methods=['POST'])
def process_message(id):
    if not session:
        return redirect('/logout')
    if not message.Message.validate_message(request.form):
        return redirect('/messages/new/' + str(id))
    message.Message.save_message(request.form)
    myId = session['user_id']
    return redirect('/users/' + str(myId))


@app.route('/messages/threads/process/<int:id>', methods=['POST'])
def process_message_from_inbox(id):
    if not session:
        return redirect('/logout')
    if not message.Message.validate_message(request.form):
        return redirect('/users/inbox/' + str(id))
    message.Message.save_message(request.form)
    return redirect('/users/inbox/' + str(id))

@app.route('/messages/delete/<int:id>')
def delete_message(id):
    if not session:
        return redirect('/logout')
    data = {
        'id': id
    }
    message.Message.delete_message(data)
    return redirect('/users/messages')


@app.route('/users/messages')
def show_message_threads():
    if not session:
        return redirect('/logout')
    data = {
        'user_id': session['user_id']
    }
    id = session['user_id']
    messages = user.User.get_all_messages_by_threads(data)
    user.User.reset_new_message_count(data)


    all_pics = image.Photo.query.filter_by(user=id).all()

    user1 = user.User.get_info_by_id(data)
    if user1.suspended == "yes":
        return redirect('/suspended')
    
    for pic in all_pics:
        if(pic.profile == "yes"):
            profile_pic = pic
            return render_template('message_threads.html', messages=messages, profile=profile_pic, user=user1)

    return render_template('message_threads.html', messages=messages, user=user1)

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
