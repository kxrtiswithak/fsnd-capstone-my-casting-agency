# FSND Capstone - Casting Agency

## Links

- Render Link: `<insert link here>`
- Runs locally on: [`http://127.0.0.1:5000/`](http://127.0.0.1:5000/)

## Getting started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python).

#### Virtual environment

Recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

## Running the server

Before running the application locally, run the [`app_setup.sh`](app_setup.sh) script in the root directory to set up the database and export database url as environment variable (feel free to change database url accordingly for you system):

```bash
. ./app_setup.sh
```

To run the server execute:

```bash
flask run --reload
```

the [`.flaskenv`](.flaskenv) contains app name and some other run configurations that flask will use, saving you the hassle of setting this up yourself. This file can be modified at your own discretion, [check this out](https://prettyprinted.com/tutorials/automatically_load_environment_variables_in_flask/) if you're curious how.

You can hit the endpoints using the [postman collection provided](udacity-fsnd-casting-agency.postman_collection.json) or using something like curl in the command line.

## API Reference

### Authentication

You can find the links for the app at the [beginning of the readme](#links).

In order to successfully hit the endpoints below and thus operate the API, authentication is required via JWTs passed in the header of requests. Within said JWTs there will need to be appropriate permissions for the endpoint one may wish to hit, passed via the `Bearer` token.

There are 3 different roles this application can be operated with:

- Casting Assistant:
    - Can view all the actors and their respective dates of birth and gender
    - Can view all the movies and their release dates
    - Can view individual actors and movies with the same information as above
    - Has the following permissions:
        - `get:actors`
        - `get:movies`
        - `get:actor`
        - `get:movie`
- Casting Director
    - Has all the access and permissions that `Casting Assistant` has
    - Can add new actors and edit existing actor and movie details
    - Can delete actors
    - Has the following additional permissions:
        - `post:actors`
        - `patch:actors`
        - `patch:movies`
        - `delete:actors`
- Executive Producer
    - Has all the access and permissions that `Casting Director` has
    - Can add and delete movies
    - Has the following additional permissions:
        - `post:movies`
        - `delete:movies`

### Error Handling

Errors are returned as JSON with their title and message in the body like so, along with http status code in the header, this example having `401 UNAUTHORIZED`:

```json
{
    "error": "permission_not_found",
    "message": "post:actors must be in permissions object",
    "success": false
}
```

The following errors will be returned in said format dependent on the nature of the failure of the request:
 - `400: Bad Request`
 - `401: Unauthorized`
 - `403: Forbidden`
 - `404: Not Found`
 - `405: Method Not Allowed`
 - `422: Unprocessable Entity`
 - `500: Internal Server Error`

### Endpoints

In order to successfully run the sample requests using the environment variables, run the script in the [testing section below](#testing).

#### `GET /`

- root endpoint that can be hit without any authorization
- can be used to check application is running fine

##### Sample Request

```bash
curl 'http://localhost:5000'
```

##### Sample Response

- `health` - should say 'Running fine' _(string)_

```json
{
    "health": "Running fine"
}
```

#### `GET /actors`

- retrieves the list of all the actors:
- `get:actors` permission needed in JWT

##### Sample Request

- headers:
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_

```bash
curl --location 'http://localhost:5000/actors' \
--header 'Authorization: Bearer '$CASTING_ASSISTANT_TOKEN''
```

##### Sample Response

- `actors` - list of actors _(list)_
    - `id `- id of actor in database _(integer)_
    - `name` - full name of actor _(string)_
- `success` - denotes whether an error has occured _(boolean)_


```json
{
  "actors": [
    {
      "id": 1,
      "name": "Anne Hathaway"
    },
    {
      "id": 2,
      "name": "Ansel Egort"
    },
    {
      "id": 3,
      "name": "Shailene Woodley"
    },
    {
      "id": 4,
      "name": "Daniel Radcliffe"
    }
  ],
  "success": true
}
```

#### `GET /actors/{{actor_id}}`

- retrieves all details for actor based on their id
- `get:actor` permission needed in JWT

##### Sample Request

- headers:
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_

```bash
curl --location 'http://localhost:5000/actors/1' \
--header 'Authorization: Bearer '$CASTING_ASSISTANT_TOKEN''
```

##### Sample Response

- `actor` - contains all details for requested actor _(object)_
    - `dob` - date of birth of actor _(string)_
    - `gender` - gender of actor, denoted by one letter being either `M`, `F` or `?` _(string)_
    - `movies` - any movies on the database the actor has been in _(list)_
    - `name` - full name of actor _(string)_
- `success` - denotes whether an error has occured _(boolean)_


```json
{
  "actor": {
    "dob": "November 12, 1982",
    "gender": "F",
    "movies": [
      "The Princess Diaries"
    ],
    "name": "Anne Hathaway"
  },
  "success": true
}
```

#### `POST /actors`

- adds a new actor to the database
- `post:actors` permission needed in JWT

##### Sample Request

- headers:
    - `Content-Type` - specifying the request body format, which is json _(string: required)_
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_
- body:
    - `name` - full name of actor _(string:required)_
    - `dob` - date of birth of actor, provided in format `dd-mm-yyyy` _(string:required)_
    - `gender` - gender of actor, denoted by one letter being either `M`, `F` or `?` _(string:required)_

```bash
curl --location --request POST 'http://localhost:5000/actors' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer '$CASTING_DIRECTOR_TOKEN'' \
--data '{
    "name": "Shailene Woodley",
    "dob": "15-11-1991",
    "gender": "F"
}'
```

##### Sample Response

- `actor_id `- id of newly created actor in database _(integer)_
- `success` - denotes whether an error has occured _(boolean)_

```json
{
  "actor_id": 6,
  "success": true
}
```

#### `PATCH /actors/{{actor_id}}`

- edits an existing actor based on their id
- only changes details for values existent in the body, but at least one value must be provided
- `patch:actors` permission needed in JWT

##### Sample Request

- headers:
    - `Content-Type` - specifying the request body format, which is json _(string: required)_
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_
- body:
    - `name` - full name of actor _(string:optional)_
    - `dob` - date of birth of actor, provided in format `dd-mm-yyyy` _(string:optional)_
    - `gender` - gender of actor, denoted by one letter being either `M`, `F` or `?` _(string:optional)_


```bash
curl --location --request PATCH 'http://localhost:5000/actors/1' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer '$CASTING_DIRECTOR_TOKEN'' \
--data '{
    "name": "Charlinha Brickley"
}'
```

##### Sample Response

- `actor` - contains all details for requested actor _(object)_
    - `dob` - date of birth of actor _(string)_
    - `gender` - gender of actor, denoted by one letter being either `M`, `F` or `?` _(string)_
    - `name` - full name of actor _(string)_
- `success` - denotes whether an error has occured _(boolean)_

```json
{
  "actor": {
    "dob": "November 12, 1982",
    "gender": "F",
    "name": "Charlinha Brickley"
  },
  "success": true
}
```

#### `DELETE /actors/{{actor_id}}`

- removes an actor from the database based on their id
- `delete:actors` permission needed in JWT

##### Sample Request

- headers:
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_

```bash
curl --location --request DELETE 'http://localhost:5000/actors/1' \
--header 'Authorization: Bearer '$CASTING_DIRECTOR_TOKEN''
```

##### Sample Response

- `actor_id `- id of actor that has been removed from the database _(integer)_
- `success` - denotes whether an error has occured _(boolean)_

```json
{
  "actor_id": 1,
  "success": true
}
```

#### `GET /movies`

- retrieves all movies in database
- `get:movies` permission needed in JWT

##### Sample Request

- headers:
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_

```bash
curl --location 'http://localhost:5000/movies' \
--header 'Authorization: Bearer '$CASTING_ASSISTANT_TOKEN''
```

##### Sample Response

- `movies` - list of movies _(list)_
    - `id `- id of movie in database _(integer)_
    - `release_year` - year movie was released _(string)_
    - `title` - name of the movie _(string)_
- `success` - denotes whether an error has occured _(boolean)_

```json
{
  "movies": [
    {
      "id": 1,
      "release_year": "2001",
      "title": "The Princess Diaries"
    },
    {
      "id": 2,
      "release_year": "2017",
      "title": "Baby Driver"
    },
    {
      "id": 3,
      "release_year": "2014",
      "title": "The Fault In Our Stars"
    },
    {
      "id": 4,
      "release_year": "2001",
      "title": "Harry Potter and the Philosopher's Stone"
    }
  ],
  "success": true
}
```

#### `GET /movies/{{movie_id}}`

- retrieves all details for movie based on id
- `get:movie` permission needed in JWT

##### Sample Request

```bash
curl --location 'http://localhost:5000/movies/1' \
--header 'Authorization: Bearer '$CASTING_ASSISTANT_TOKEN''
```

##### Sample Response

- `movie` - contains all the details for the request movie _(object)_
    - `actors `- list of actors in the movie _(list)_
    - `release_date` - date the movie was released _(string)_
    - `title` - name of the movie _(string)_
- `success` - denotes whether an error has occured _(boolean)_

```json
{
  "movie": {
    "actors": [
      "Anne Hathaway"
    ],
    "release_date": "December 21, 2001",
    "title": "The Princess Diaries"
  },
  "success": true
}
```

#### `POST /movies`

- adds a new movie to the database
- `post:movies` permission needed in JWT
- any actors in request must already exist in database before being added to movie
- an empty list can be passed successfully, but `actors` key is required in request body

##### Sample Request

- headers:
    - `Content-Type` - specifying the request body format, which is json _(string: required)_
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_
- body:
    - `title` - name of the movie _(string:required)_
    - `release_date` - date the movie was released, provided in format `dd-mm-yyyy` _(string:required)_
    - `actors `- list of actors in the movie _(list:required)_

```bash
curl --location --request POST 'http://localhost:5000/movies' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer '$EXECUTIVE_PRODUCER_TOKEN'' \
--data '{
    "title": "The Fault In Our Stars",
    "release_date": "16-06-2014",
    "actors": [
        "Shailene Woodley"
    ] 
}'
```

##### Sample Response

- `movie_id `- id of newly created movie in database _(integer)_
- `success` - denotes whether an error has occured _(boolean)_

```json
{
  "movie_id": 5,
  "success": true
}
```

#### `PATCH /movies/{{movie_id}}`

- edits an exsiting movie in the database based on id
- only changes details for values existent in the body, but at least one value must be provided
- `patch:movies` permission needed in JWT

##### Sample Request

- headers:
    - `Content-Type` - specifying the request body format, which is json _(string: required)_
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_
- body:
    - `title` - name of the movie _(string:optional)_
    - `release_date` - date the movie was released, provided in format `dd-mm-yyyy` _(string:optional)_
    - `actors `- list of actors in the movie _(list:optional)_

```bash
curl --location --request PATCH 'http://localhost:5000/movies/1' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer '$CASTING_DIRECTOR_TOKEN'' \
--data '{
    "release_date": "27-07-2017"
}'
```

##### Sample Response

- `movie` - contains all the details for the request movie _(object)_
    - `release_date` - date the movie was released _(string)_
    - `title` - name of the movie _(string)_
- `success` - denotes whether an error has occured _(boolean)_

```json
{
  "movie": {
    "release_date": "July 27, 2017",
    "title": "The Princess Diaries"
  },
  "success": true
}
```

#### `DELETE /movies/{{movie_id}}`

- removes a movie from the database
- this will not remove any actors for the movie in question
- `delete:movies` permission needed in JWT

##### Sample Request

- headers:
    - `Authorization` - contains JWT with 'Bearer' preceding _(string: required)_

```bash
curl --location --request DELETE 'http://localhost:5000/movies/1' \
--header 'Authorization: Bearer '$EXECUTIVE_PRODUCER_TOKEN''
```

##### Sample Response

- `movie_id `- id of movie that has been removed from the database _(integer)_
- `success` - denotes whether an error has occured _(boolean)_

```json
{
  "movie_id": 1,
  "success": true
}
```

## Testing

Similar to [running the application locally](#running-the-server), run the [`test_app_setup.sh`](test_app_setup.sh) script in the root directory to set up the test database and export test database url as environment variable (feel free to change database url accordingly for you system):

```bash
. ./test_app_setup.sh
```

To run the tests execute:

```bash
python test_app.py
```