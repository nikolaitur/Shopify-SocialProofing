# Shopify Socialproofing App Repository

[![Build Status](https://travis-ci.com/johnsliao/Shopify-SocialProofing.svg?token=e17eeXXt29Y4Pr7HVhoa&branch=development)](https://travis-ci.com/johnsliao/Shopify-SocialProofing)

### Pre-requisites
* Up to Python 3.6.3 installed

### Setting up your development environment
* Clone the repository
```
$ git clone https://github.com/johnsliao/Shopify-SocialProofing.git
```
* Set up your virtual environment

```
$ virtualenv -p python3 venv
$ source venv/bin/activate
```
* Set your environment variables.
```
$ export API_KEY=<API_KEY>
$ export API_SECRET=<API_SECRET>
$ export DEVELOPMENT_MODE=TEST  # Must be 'TEST' or 'PRODUCTION'
```
* Install dependencies
```
$ pip install -r requirements.txt
```
* Run the server
```
$ python3 manage.py runserver
```
You should see something like:
```
(venv) dtl-macbook1:Shopify-SocialProofing jliaolocal$ python3 manage.py runserver
 
Performing system checks...

System check identified no issues (0 silenced).

You have 13 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.

October 31, 2017 - 17:20:00
Django version 1.11.1, using settings 'app.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Shopify Development Store
[Shopify Partners](https://partners.shopify.com)

### Heroku
[Heroku](https://dashboard.heroku.com) is the hosting service for the app and the database (postgres).

To query the database via Heroku:

1. More -> Run Console

```
$ heroku run bash
```

2. Connect to the database
```
$ psql -h <host> -p <port> -U <username> <database>
```

3. Run a query
```
$ SELECT * FROM app_stores;

 id |           store_name            |         permanent_token
----+---------------------------------+----------------------------------
  1 | michael-john-devs.myshopify.com | 948d9463f07e4bfcc8b5324b62637898
(1 row)
```

### Trello
Trello board found [here](https://trello.com/b/EnVgpkJ4/social-proof).

### Continuous Integration
Currently using [Travis CI](https://travis-ci.org/).

### Running tests
To run the tests manually, use the following command:
```
$ python3 manage.py test
```
