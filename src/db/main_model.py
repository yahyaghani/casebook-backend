from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    return migrate

def setup_database(app):
    with app.app_context():
        db.create_all()

# all the models
class UserModel(db.Model):
    __tablename__ = 'user_model'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    fname = db.Column(db.String(80))
    lname = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    city = db.Column(db.String(80))
    country = db.Column(db.String(80))
    organisation = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(500))
    admin = db.Column(db.Boolean)
    file_posts = db.relationship('FilePost', backref='user_model', lazy='select')
    ratings = db.relationship('Rating', backref='user_model', lazy='select')

    def __repr__(self):
        return f'{self.public_id}'

caselog_files = db.Table('caselog_files',
    db.Column('caselog_id', db.Integer, db.ForeignKey('caselog.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('file_post.id'), primary_key=True)
)

class FilePost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    caselogs = db.relationship('Caselog', secondary=caselog_files, back_populates='files')
    total_rating = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.id}'

    def serialize(self):
        post = {c: getattr(self, c) for c in inspect(self).attrs.keys()}
        if 'user_model' in post and getattr(self, 'user_model'):
            del post['user_model']
            post['user_info'] = {}
            for c in inspect(self.user_model).attrs.keys():
                post['user_info'][c] = getattr(self.user_model, c)
            del post['user_info']['file_posts']
            del post['user_info']['ratings']
            del post['user_info']['password']

        if 'caselogs' in post:
            post['all_caselogs'] = [caselog.id for caselog in self.caselogs]
            del post['caselogs']

        if 'ratings' in post:
            post['all_ratings'] = []
            for rating in post['ratings']:
                newRating = {}
                newRating['rating'] = getattr(rating, 'rating')
                newRating['review'] = getattr(rating, 'review')
                newRating['id'] = getattr(rating, 'id')
                newRating['user_id'] = getattr(rating, 'user_id')
                post['all_ratings'].append(newRating)
            del post['ratings']
        return post

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    review = db.Column(db.String(80))
    post_id = db.Column(db.Integer, db.ForeignKey('file_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)

    def __repr__(self):
        return f'{self.id}'

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

class Caselog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_description = db.Column(db.String(255))  # Case description or title
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))  # Link to the user
    files = db.relationship('FilePost', secondary='caselog_files', back_populates="caselogs")  # Relationship to files

    def __repr__(self):
        return f'<Caselog {self.id} {self.case_description}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'case_description': self.case_description,
            'user_id': self.user_id,
            'files': [file.serialize() for file in self.files]
        }


# custom decorators

# db.create_all()

