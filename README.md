
AllPoll
=======

> **:warning: WARNING:** this project was abandoned many years ago. Please do not use it.


AllPoll is simple polling appication for Django. Includes single and list views, ajax support.

Install
-------

1. Run in your favorite shell
    
        python setup.py install

2. add django-allpoll to your INSTALLED_APPS:

        INSTALLED_APPS = (...
            ...
            'allpoll',
            ...
        )

3. add urls to urlpatterns:

        # urls.py
        urlpatterns = patterns('',
            ...
            (r'^polls/', include('allpoll.urls')),
            ...
        )

4. finally:

        python manage.py syncdb

Usage
-----

You can use predefined AllPoll views and/or template tags:

* `allpoll_get`: get poll as context variable
* `allpoll_render`: include and render poll template

**NOTE**: `allpoll.views.poll_vote` view is required for voting
