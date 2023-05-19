from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


cast = db.Table('cast',
                db.Column('actor_id',
                          db.Integer, db.ForeignKey('actors.id'),
                          primary_key=True),
                db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'),
                          primary_key=True)
                )


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.Date, nullable=False)

    actors = db.relationship('Actor', secondary=cast,
                             backref=db.backref('movies', lazy=True))

    def short(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_year': self.release_date.strftime("%Y")
        }

    def long(self):
        return {
            'title': self.title,
            'release_date': self.release_date.strftime("%B %d, %Y")
        }

    def full(self):
        return {
            'title': self.title,
            'release_date': self.release_date.strftime("%B %d, %Y"),
            'actors': [actor.name for actor in self.actors]
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.full())


class Actor(db.Model):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(1), nullable=False)

    def short(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def long(self):
        return {
            'name': self.name,
            'dob': self.dob.strftime("%B %d, %Y"),
            'gender': self.gender
        }

    def full(self):
        return {
            'name': self.name,
            'dob': self.dob.strftime("%B %d, %Y"),
            'gender': self.gender,
            'movies': [movie.title for movie in self.movies]
        }
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.full())
