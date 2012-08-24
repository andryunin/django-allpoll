
AllPoll
=======

AllPoll is simple polling appication for Django.

Install
-------

1. Run in your favorite shell
    
        python setup.py install

2. add django-polls to your INSTALLED_APPS:

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
        python manage.py collectstatic

Usage
-----

You can use {% allpoll_latest %} template tag to include latest poll in template.