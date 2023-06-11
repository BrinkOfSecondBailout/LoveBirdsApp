import re
from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from flask_app import app
from flask import flash

class Message:
    def __init__(self, data):
        self.id = data['id']
        self.text = data['text']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.sender = None
        self.receiver = None

    @staticmethod
    def validate_message(data):
        is_valid = True
        if len(data['text']) < 10:
            flash('Please type a message, at least 10 characters to impress your match :)', 'message')
            is_valid = False
        return is_valid
    
    @classmethod
    def save_message(cls, data):
        query = 'INSERT INTO messages (text, created_at, updated_at, sender_id, receiver_id) VALUES ( %(text)s , NOW() , NOW() , %(sender_id)s , %(receiver_id)s );'
        connectToMySQL('lovebirds_schema').query_db(query, data)
        query = 'UPDATE users SET new_message = new_message + 1 WHERE id = %(receiver_id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
    
    @classmethod
    def delete_message(cls,data):
        query = 'DELETE FROM messages WHERE id = %(id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
