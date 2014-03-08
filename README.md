# Bountyful Coins Bounty Directory

### App version 0.5a

[![Build Status](https://travis-ci.org/asfaltboy/bountyfulcoins.png?branch=registration)](https://travis-ci.org/asfaltboy/bountyfulcoins)
[![Coverage Status](https://coveralls.io/repos/asfaltboy/bountyfulcoins/badge.png)](https://coveralls.io/r/asfaltboy/bountyfulcoins)


## Deployment

1. Clone this repository
2. (optional) Create [a virtualenv](http://www.virtualenv.org/en/latest/virtualenv.html); source into the virtualenv.
3. Install [requirements](http://www.pip-installer.org/en/1.1/requirements.html) by running `pip install -r requirements.txt`
4. Set up host specific settings in a custom settings module (for an example of new available settings to override - with their defaults, see below)
5. run the following set of django management commands:
    1. `python manage.py syncdb --noinput`
    2. `python manage.py migrate`
    3. `python manage.py collectstatic --noinput`
6. Run or restart your wsgi server.
7. Enter the site's `admin` panel and configure the correct [Site hostname](https://docs.djangoproject.com/en/1.6/ref/contrib/sites/).
8. Add the decay_balance management command as a cronjob. For instance to run it every day at 12:00am (this needs to be done only once):

        crontab -l > temp_jobs
        echo  "0 0 * * * python manage.py decay_balance" >> temp_jobs
        crontab < temp_jobs
        rm temp_jobs

(in the future we will also support: `python manage.py compilemessages`)

### Running Tests

To run the test suite, simply run:

    python manage.py test --settings=bountyfulcoins.test_settings


## Release Flow

### Tag Release

After a version is complete, the following needs to be done:

1. Tag the version in github and selecting 'Draft new release'. Name the tag using the [Semantic versioning](http://semver.org/) format.

    For example: `v0.3.0` to release the version 0.3. You may omit the last version (PATCH) if it's zero, e.g: v0.3.
2. Connect to the target server machine, and git clone from this tag

        git fetch --tags origin master
        git checkout tags/<new_tag_name>

        # e.g: git checkout tags/v0.3

3. Run the deployment steps detailed above (usually, only the django commands need
to be repeated)
4. Test the target server for regressions and critical issues. If any problems arise, revert to the previously tagged release by running:

        git checkout tags/<previous_tag_name>

5. If reverted to a previous version, and new version had a new migration, then south migrations should be reversed back to the previous version by running:

        python manage.py migrate bountyfullapp <previous migration>
