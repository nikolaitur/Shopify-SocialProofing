# Shopify Socialproofing App Repository

[![Build Status](https://travis-ci.com/johnsliao/Shopify-SocialProofing.svg?token=e17eeXXt29Y4Pr7HVhoa&branch=development)](https://travis-ci.com/johnsliao/Shopify-SocialProofing)

### Pre-requisites
* Up to Python 3.6.3 installed

### Setting up your development environment
* Clone the repository
* Set up your virtual environment

```buildoutcfg
$ virtualenv -p python3 venv
$ source venv/bin/activate
```

* Install dependencies
```buildoutcfg
$ pip install -r requirements.txt
```
* Run the server
```buildoutcfg
$ python3 manage.py runserver
```
You should see something like:
```buildoutcfg
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

### Running tests
To run the tests manually, use the following command:
```buildoutcfg
$ python3 manage.py test
```
