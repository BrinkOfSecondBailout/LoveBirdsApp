from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models import wallnote


@app.route('/wall/create', methods=['POST'])
def process_wall_note():
    if not session:
        return redirect('/logout')
    if not wallnote.Wallnote.validate_note(request.form):
        return redirect('/dashboard')
    data = {
        'text': request.form['text'],
        'user_id': session['user_id']
    }
    wallnote.Wallnote.save_wall_note(data)
    return redirect('/dashboard')

@app.route('/wall/delete/<int:id>')
def delete_wall_note(id):
    if not session:
        return redirect('/logout')
    data = {
        'id': id
    }
    wallnote.Wallnote.delete_note(data)
    return redirect('/dashboard')