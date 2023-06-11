import re
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import flash
from flask_app.models import user

class Wallnote:
    def __init__(self, data):
        self.id = data['id']
        self.text = data['text']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.creator = None

    @staticmethod
    def validate_note(data):
        is_valid = True
        if  not (data.get('text')):
            flash('Please write something on the wall!', 'wall')
            is_valid = False
        if len(data['text']) > 25:
            flash('Maximum 25 words, sorry!', 'wall')
            is_valid = False
        return is_valid
    
    @classmethod
    def save_wall_note(cls, data):
        query = 'INSERT INTO wallnotes(text, created_at, updated_at, user_id) VALUES ( %(text)s, NOW(), NOW(), %(user_id)s );'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
    
    @classmethod
    def get_all_notes_with_users(cls):
        query = 'SELECT * FROM wallnotes JOIN users ON users.id = wallnotes.user_id;'
        results = connectToMySQL('lovebirds_schema').query_db(query)
        all_notes = []
        for row in results:
            one_note = cls(row)
            one_notes_creator_info = {
                'id': row['users.id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': None,
                'password': None,
                'created_at': None,
                'updated_at': None,
                'num_of_blocks': None,
                'new_message': None,
                'suspended': None
            }
            one_note.creator = user.User(one_notes_creator_info)
            all_notes.append(one_note)
        return all_notes

    @classmethod
    def delete_note(cls, data):
        query = 'DELETE FROM wallnotes WHERE id = %(id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)

