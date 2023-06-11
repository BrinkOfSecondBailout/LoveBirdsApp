import re
from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from flask_app import app
from flask import flash
from flask_app.models.message import Message
from flask_app.models.attribute import Attribute
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.num_of_blocks = data['num_of_blocks']
        self.new_message = data['new_message']
        self.suspended = data['suspended']
        self.hearts_sent = []
        self.hearts_received = []
        self.messages = []
        self.matches = []
        self.blocks = []
        


    @staticmethod
    def validate_registration(data):
        is_valid = True
        query = 'SELECT * FROM users WHERE email=%(email)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if len(results) > 0:
            flash('This email account already exists! Please log in.', 'registration')
            is_valid = False
        if len(data['first_name']) < 2:
            flash('First name must be at least 2 characters!', 'registration')
            is_valid = False
        if len(data['last_name']) < 2:
            flash('Last name must be at least 2 characters!', 'registration')
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash('Invalid email format', 'registration')
            is_valid = False
        if len(data['password']) < 5:
            flash('Password must be at least 5 characters', 'registration')
            is_valid = False
        if data['password'] != data['confirm_password']:
            flash('Password confirmation not matching! Try again.', 'registration')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_edit(data):
        is_valid = True
        query = 'SELECT * FROM users WHERE id=%(id)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if len(data['first_name']) < 2:
            flash('First name must be at least 2 characters!', 'edit')
            is_valid = False
        if len(data['last_name']) < 2:
            flash('Last name must be at least 2 characters!', 'edit')
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash('Invalid email format', 'edit')
            is_valid = False
        return is_valid

    @staticmethod
    def validate_login(data):
        is_valid = True
        query = 'SELECT * FROM users WHERE email=%(email)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if len(results) == 0:
            flash('That email is not found in the database! Try again.', 'login')
            is_valid = False
            return is_valid
        else:
            is_valid = True
            user_data = results[0]
            return user_data


    @classmethod
    def save_user(cls, data):
        query = 'INSERT INTO users(first_name, last_name, email, password, created_at, updated_at, num_of_blocks, new_message, suspended) VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s , NOW(), NOW(), 0, 0, "no" );'
        return connectToMySQL('lovebirds_schema').query_db(query, data)

    @classmethod
    def get_info_by_id(cls, data):
        query = 'SELECT * FROM users WHERE id=%(user_id)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        return cls(results[0])
    
    @classmethod
    def update_user(cls, data):
        query = 'UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s, email=%(email)s WHERE id = %(id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
    
    @classmethod
    def validate_password(cls, data):
        is_valid = True
        if len(data['password']) < 5:
            flash('Password must be at least 5 characters', 'update_pw')
            is_valid = False
        if data['password'] != data['confirm_password']:
            flash('Password confirmation not matching! Try again.', 'update_pw')
            is_valid = False
        return is_valid


    @classmethod
    def update_password(cls, data):
        query = 'UPDATE users SET password=%(password)s WHERE id = %(id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
    
    @classmethod
    def delete_user(cls, data):
        query = 'DELETE FROM users WHERE id=%(user_id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
    
    @classmethod
    def get_all_users(cls):
        query = 'SELECT * FROM users;'
        return connectToMySQL('lovebirds_schema').query_db(query)
    
    @classmethod
    def get_all_messages_for_me(cls, data):
        query = 'SELECT * FROM messages LEFT JOIN users ON messages.sender_id = users.id WHERE receiver_id = %(user_id)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        all_messages = []
        for row in results:
            one_message = Message(row)
            one_message_sender_info = {
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
            one_message.sender = cls(one_message_sender_info)
            all_messages.append(one_message)
        return all_messages
    
    @classmethod
    def reset_new_message_count(cls, data):
        query = 'UPDATE users SET new_message = 0 WHERE id = %(user_id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)

    @classmethod
    def block_user(cls, data):
        query = 'INSERT INTO blocks(reason, blocker_id, blocked_id) VALUES (%(reason)s, %(user_id)s, %(id)s );'
        connectToMySQL('lovebirds_schema').query_db(query, data)
        query = 'UPDATE users SET num_of_blocks = num_of_blocks + 1 WHERE id = %(id)s;'
        connectToMySQL('lovebirds_schema').query_db(query, data)
        query = 'SELECT num_of_blocks FROM users WHERE id = %(id)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        print(results[0]['num_of_blocks'])
        if (results[0]['num_of_blocks']) == 3:
            query = 'UPDATE users SET suspended = "yes" WHERE id = %(id)s;'
            return connectToMySQL('lovebirds_schema').query_db(query, data)
        return True
    
    @classmethod
    def check_if_im_blocked(cls, data):
        query = 'SELECT * FROM blocks WHERE blocker_id = %(blocker_id)s AND blocked_id = %(blocked_id)s ;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if results:
            return True
        query = 'SELECT * FROM blocks WHERE blocked_id = %(blocker_id)s AND blocker_id = %(blocked_id)s ;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if results:
            return True
        return False


    @classmethod
    def send_heart(cls, data):
        query = 'SELECT * FROM matches WHERE user_id = %(user_id)s AND match_id = %(match_id)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if results:
            flash('You already sent this user a heart, be patient! :)', 'heart')
            return False

        query = 'INSERT INTO matches(user_id, match_id) VALUES (%(user_id)s, %(match_id)s);'
        return connectToMySQL('lovebirds_schema').query_db(query, data)
    
    @classmethod
    def unsend_heart(cls, data):
        query = 'DELETE FROM matches WHERE user_id = %(user_id)s AND match_id = %(id)s;'
        return connectToMySQL('lovebirds_schema').query_db(query, data)

    @classmethod
    def get_me_with_all_my_hearts(cls, data):

        # this gets us all the users that we have sent hearts out to and add it to the hearts_sent array above
        query = 'SELECT u.*, m.* FROM users u LEFT JOIN matches ON matches.user_id = u.id LEFT JOIN users m ON matches.match_id = m.id WHERE u.id = %(id)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        user = cls(results[0])
        for row in results:
            user_data = {
                'id': row['m.id'],
                'first_name': row['m.first_name'],
                'last_name': row['m.last_name'],
                'email': row['m.email'],
                'password': row['m.password'],
                'created_at': row['m.created_at'],
                'updated_at': row['m.updated_at'], 
                'num_of_blocks': None,
                'new_message': None,
                'suspended': None
            }
            user.hearts_sent.append(cls(user_data))

        # this gets us all the users that have sent us hearts and add it to the hearts_received array above
        query = 'SELECT u.* , m.* FROM users u LEFT JOIN matches ON matches.match_id = u.id LEFT JOIN users m ON matches.user_id = m.id WHERE u.id = %(id)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        for row in results:
            user_data = {
                'id': row['m.id'],
                'first_name': row['m.first_name'],
                'last_name': row['m.last_name'],
                'email': row['m.email'],
                'password': row['m.password'],
                'created_at': row['m.created_at'],
                'updated_at': row['m.updated_at'],
                'num_of_blocks': None,
                'new_message': None,
                'suspended': None
            }
            user.hearts_received.append(cls(user_data))

        # this will check our hearts_sent and hearts_received and see which matches we actually have and add it to self.matches
        for recipient in user.hearts_sent:
            for sender in user.hearts_received:
                if recipient.id == sender.id:
                    user.matches.append(recipient)

        return user
    
    @classmethod
    def check_if_we_match(cls, data):
        user1 = cls.get_me_with_all_my_hearts(data)
        for sent in user1.hearts_sent:
            for received in user1.hearts_received:
                if sent.id == received.id:
                    print("Congrats! It's a match!")
                    return True
        return False
    
    @classmethod
    def get_users_by_age_higher_filter(cls, data):
        query = 'SELECT * FROM users JOIN attributes ON users.id = attributes.user_id WHERE age >= %(age)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False
        all_users = []
        for row in results:
            user_data = {
                'id': row['id'],
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
            one_user = cls(user_data)
            all_users.append(one_user)
        return all_users
    
    @classmethod
    def get_users_by_age_lower_filter(cls, data):
        query = 'SELECT * FROM users JOIN attributes ON users.id = attributes.user_id WHERE age <= %(age)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False
        all_users = []
        for row in results:
            user_data = {
                'id': row['id'],
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
            one_user = cls(user_data)
            all_users.append(one_user)
        return all_users

    @classmethod
    def get_users_by_gender_filter(cls, data):
        query = 'SELECT * FROM users JOIN attributes ON users.id = attributes.user_id WHERE gender = %(gender)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False
        all_users = []
        for row in results:
            user_data = {
                'id': row['id'],
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
            one_user = cls(user_data)
            all_users.append(one_user)
        return all_users
    
    @classmethod
    def get_users_by_smoker_filter(cls, data):
        query = 'SELECT * FROM users JOIN attributes ON users.id = attributes.user_id WHERE smoker = %(smoker)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False
        all_users = []
        for row in results:
            user_data = {
                'id': row['id'],
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
            one_user = cls(user_data)
            all_users.append(one_user)
        return all_users
    
    @classmethod
    def get_users_by_drinker_filter(cls, data):
        query = 'SELECT * FROM users JOIN attributes ON users.id = attributes.user_id WHERE drinker = %(drinker)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False
        all_users = []
        for row in results:
            user_data = {
                'id': row['id'],
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
            one_user = cls(user_data)
            all_users.append(one_user)
        return all_users
    
    @classmethod
    def get_users_by_goal_filter(cls, data):
        query = 'SELECT * FROM users JOIN attributes ON users.id = attributes.user_id WHERE dating_goal = %(dating_goal)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False
        all_users = []
        for row in results:
            user_data = {
                'id': row['id'],
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
            one_user = cls(user_data)
            all_users.append(one_user)
        return all_users
    
    @classmethod
    def get_users_by_hobbies_filter(cls, data):
        query = 'SELECT * FROM users JOIN attributes ON users.id = attributes.user_id WHERE hobbies = %(hobbies)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False
        all_users = []
        for row in results:
            user_data = {
                'id': row['id'],
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
            one_user = cls(user_data)
            all_users.append(one_user)
        return all_users

    @classmethod
    def get_users_by_body_filter(cls, data):
        query = 'SELECT * FROM users JOIN attributes ON users.id = attributes.user_id WHERE body_type = %(body_type)s;'
        results = connectToMySQL('lovebirds_schema').query_db(query, data)
        if not results:
            return False
        all_users = []
        for row in results:
            user_data = {
                'id': row['id'],
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
            one_user = cls(user_data)
            all_users.append(one_user)
        return all_users
    
