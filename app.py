import sys
from time import strptime
from datetime import datetime
from flask import (
    Flask,
    request,
    abort,
    flash,
    jsonify
)
from flask_cors import CORS
from sqlalchemy import exc
from database.models import *
from auth.auth import AuthError, requires_auth
from config import *
from enums import *


def create_app(test_config=None):
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object('config')
    app.secret_key = 'super secret key'

    with app.app_context():
        db.init_app(app)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        response.headers.add("Access-Control-Allow-Credentials", "*")

        return response

    @app.route('/')
    def health_check():
        return jsonify({
            'health': 'Running fine'
            }), 200

    # def format_datetime(value, format='medium'):
    #     date = -1
    #     if isinstance(value, str):
    #         date = dateutil.parser.parse(value)
    #     else:
    #         date = value
    #     if format == 'full':
    #         format = "EEEE MMMM, d, y 'at' h:mma"
    #     elif format == 'medium':
    #         format = "EE MM, dd, y h:mma"
    #     return babel.dates.format_datetime(date, format, locale='en')

    # app.jinja_env.filters['datetime'] = format_datetime

    def get_actor_names():
        app.app_context.push()
        return [name[0] for name in
                Actor.query.with_entities(Actor.name).all()]

    @app.route('/movies')
    @requires_auth('get:movies')
    def movies():
        all_movies = Movie.query.all()

        if len(all_movies) == 0:
            abort(404)

        movies = [movie.short() for movie in all_movies]

        return jsonify({
            'success': True,
            'movies': movies
        })

    @app.route('/actors')
    @requires_auth('get:actors')
    def actors():
        all_actors = Actor.query.all()

        if len(all_actors) == 0:
            abort(404)

        actors = [actor.short() for actor in all_actors]

        return jsonify({
            'success': True,
            'actors': actors
        })

    @app.route('/movies/<int:movie_id>')
    @requires_auth('get:movie')
    def get_movie_by_id(movie_id):
        movie = Movie.query.filter(
            Movie.id == movie_id).one_or_none()

        if movie is None:
            abort(404)

        return jsonify({
            'success': True,
            'movie': movie.full()
        })

    @app.route('/actors/<int:actor_id>')
    @requires_auth('get:actor')
    def get_actor_by_id(actor_id):
        actor = Actor.query.filter(
            Actor.id == actor_id).one_or_none()

        if actor is None:
            abort(404)

        return jsonify({
            'success': True,
            'actor': actor.full()
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie():
        try:
            body = request.get_json()
            error_text = f'Error occured: Movie could not be listed.'
            movie_keys = ['title', 'release_date', 'actors']
            if not all(key in body for key in movie_keys):
                raise KeyError

            movie_title = body.get('title')
            release_date = body.get('release_date')
            if len(movie_title) == 0 \
                    or len(release_date) == 0:
                raise ValueError

            error_text = (f'Error occured: Movie \'{movie_title}\'',
                          ' could not be listed.')

            movie = Movie()

            if len(movie_title) == 0:
                raise ValueError
            movie.title = movie_title

            if len(release_date) == 0:
                raise ValueError
            movie.release_date = datetime.strptime(release_date,
                                                   '%d-%m-%Y')

            cast = Actor.query.filter(
                Actor.name.in_(body.get('actors'))).all()

            if len(body.get('actors')) == len(cast):
                movie.actors = cast
                movie.insert()
                flash((f'Movie \'{movie_title}\'',
                       ' was successfully created!'))

                return jsonify({
                    'success': True,
                    'movie_id': movie.id
                }), 201
            else:
                raise ValueError
        except (ValueError, exc.SQLAlchemyError, KeyError) as e:
            print(sys.exc_info())
            print(str(e))
            flash(error_text)
            abort(422)

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_actor():
        try:
            body = request.get_json()
            error_text = (f'Error occured: Actor could not be edited.')
            actor_keys = ['name', 'dob', 'gender']
            if not all(key in body for key in actor_keys):
                raise KeyError

            actor_name = body.get('name')
            dob = body.get('dob')
            gender = body.get('gender')
            if len(actor_name) == 0 \
                    or len(dob) == 0 \
                    or len(gender) == 0:
                raise ValueError

            error_text = (f'Error occured: Actor \'{actor_name}\'',
                          ' could not be listed.')

            actor = Actor()

            if len(actor_name) == 0:
                raise ValueError
            actor.name = actor_name

            if len(dob) == 0:
                raise ValueError
            actor.dob = datetime.strptime(dob, '%d-%m-%Y')

            if len(gender) != 1:
                raise ValueError
            if gender not in Gender.choices():
                raise ValueError
            actor.gender = gender

            actor.insert()
            flash(f'Actor \'{actor_name}\' was successfully created!')

            return jsonify({
                'success': True,
                'actor_id': actor.id
            }), 201
        except (exc.SQLAlchemyError, ValueError, KeyError) as e:
            print(sys.exc_info())
            print(str(e))
            flash(error_text)
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def edit_movie(movie_id):
        try:
            body = request.get_json()
            error_text = f'Error occured: Movie could not be edited.'
            movie_keys = ['title', 'release_date', 'actors']
            if not any(key in body for key in movie_keys):
                raise KeyError

            movie = Movie.query.filter(
                Movie.id == movie_id).one_or_none()

            if movie is None:
                abort(404)

            movie_title = movie.title
            error_text = (f'Error occured: Movie \'{movie_title}\'',
                          ' could not be edited.')

            if 'title' in body:
                movie_title = body.get('title')
                if len(movie_title) == 0:
                    raise ValueError
                error_text = (f'Error occured: Movie \'{movie_title}\'',
                              ' could not be edited.')

                movie.title = movie_title

            if 'release_date' in body:
                release_date = body.get('release_date')
                if len(release_date) == 0:
                    raise ValueError

                movie.release_date = datetime.strptime(release_date,
                                                       '%d-%m-%Y')

            if 'actors' in body:
                cast = Actor.query.filter(
                    Actor.name.in_(body.get('actors'))).all()

                if len(body.get('actors')) == len(cast):
                    movie.actors = cast
                else:
                    raise ValueError

            movie.update()
            flash(f'Movie \'{movie_title}\' was successfully edited!')

            return jsonify({
                'success': True,
                'movie': movie.long()
            }), 202
        except (ValueError, exc.SQLAlchemyError, KeyError) as e:
            print(sys.exc_info())
            print(str(e))
            flash(error_text)
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def edit_actor(actor_id):
        try:
            body = request.get_json()
            error_text = f'Error occured: Actor could not be edited.'

            actor_keys = ['name', 'dob', 'gender']
            if not any(key in body for key in actor_keys):
                raise KeyError

            actor = Actor.query.filter(
                Actor.id == actor_id).one_or_none()

            if actor is None:
                abort(404)

            actor_name = actor.name
            error_text = (f'Error occured: Actor \'{actor_name}\'',
                          ' could not be edited.')

            if 'name' in body:
                actor_name = body.get('name')
                if len(actor_name) == 0:
                    raise ValueError

                error_text = (f'Error occured: Actor \'{actor_name}\'',
                              ' could not be edited.')
                actor.name = actor_name

            if 'dob' in body:
                dob = body.get('dob')
                if len(dob) == 0:
                    raise ValueError

                actor.dob = datetime.strptime(dob, '%d-%m-%Y')

            if 'gender' in body:
                gender = body.get('gender')
                if len(gender) != 1:
                    raise ValueError
                if gender not in Gender.choices():
                    raise ValueError

                actor.gender = gender

            actor.update()
            flash(f'Actor \'{actor_name}\' was successfully edited!')

            return jsonify({
                'success': True,
                'actor': actor.long()
            }), 202
        except (exc.SQLAlchemyError, KeyError, ValueError) as e:
            print(sys.exc_info())
            print(str(e))
            flash(error_text)
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(movie_id):
        movie = Movie.query.filter(
            Movie.id == movie_id).one_or_none()

        if movie is None:
            abort(404)

        movie_title = request.form.get('title')
        error_text = (f'Error occured: Movie \'{movie_title}\'',
                      ' could not be deleted.')

        try:
            movie.delete()
            flash(f'Movie \'{movie_title}\' was successfully deleted!')

            return jsonify({
                'success': True,
                'movie_id': movie.id
            })
        except exc.SQLAlchemyError as e:
            print(sys.exc_info())
            print(str(e.orig))
            flash(error_text)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(actor_id):
        actor = Actor.query.filter(
            Actor.id == actor_id).one_or_none()

        if actor is None:
            abort(404)

        actor_name = request.form.get('name')
        error_text = (f'Error occured: Actor \'{actor_name}\'',
                      ' could not be deleted.')

        try:
            actor.delete()
            flash(f'Actor \'{actor_name}\' was successfully deleted!')

            return jsonify({
                'success': True,
                'actor_id': actor.id
            })
        except exc.SQLAlchemyError as e:
            print(sys.exc_info())
            print(str(e.orig))
            flash(error_text)

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(422)
    @app.errorhandler(500)
    def error_handler(error):
        return jsonify({
            'success': False,
            'error': error.code,
            'message': error.description
        }), error.code

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            'success': False,
            'error': error.error['code'],
            'message': error.error['description']
        }), error.status_code

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
