import re
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import flash


class Attribute:
    def __init__(self, data):
        self.id = data['id']
        self.description = data['description']
        self.age = data['age']
        self.gender = data['gender']
        self.smoker = data['smoker']
        self.drinker = data['drinker']
        self.dating_goal = data['dating_goal']
        self.hobbies = data['hobbies']
        self.body_type = data['body_type']
        self.user_id = data['user_id']
        self.instagram = data['instagram']
        self.facebook = data['facebook']
        self.twitter = data['twitter']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']



    @staticmethod
    def validate_attribute(data):
        is_valid = True
        if len(data['description']) < 10:
            flash('Please type a description, must be at least 10 characters!', 'attribute')
            is_valid = False
        if not (data['age']):
            flash('Please specify your age!', 'attribute')
            is_valid = False
        return is_valid


    @classmethod
    def save_attribute(cls, data):
        query = 'INSERT INTO attributes(description, age, gender, smoker, drinker, dating_goal, hobbies, body_type, user_id, created_at, updated_at, instagram, facebook, twitter) VALUES ( %(description)s, %(age)s, %(gender)s, %(smoker)s, %(drinker)s, %(dating_goal)s, %(hobbies)s, %(body_type)s, %(user_id)s, NOW(), NOW(), %(instagram)s, %(facebook)s, %(twitter)s );'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
    
    @classmethod
    def get_attribute_by_user_id(cls, data):
        query = 'SELECT * FROM attributes WHERE user_id=%(user_id)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False;
        return cls(results[0])
    
    @classmethod
    def update_attribute(cls, data):
        query = 'UPDATE attributes SET description=%(description)s, age=%(age)s, gender=%(gender)s,  smoker=%(smoker)s, drinker=%(drinker)s, dating_goal=%(dating_goal)s, hobbies=%(hobbies)s, body_type=%(body_type)s, instagram=%(instagram)s, facebook=%(facebook)s, twitter=%(twitter)s WHERE user_id = %(user_id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
