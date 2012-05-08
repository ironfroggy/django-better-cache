from setuptools import setup, find_packages
setup(
    name = "bettercache",
    version = "0.3.1-cmg",
    packages = find_packages(),
    author = "Cox Media Group",
    author_email = "opensource@coxinc.com",
    description = "A suite of better cache tools for Django.",
    license = "MIT",
    url = "https://github.com/coxmediagroup/django-better-cache",
    install_requires = [
        "django==1.3",
        "celery==2.4.2",
        "httplib2==0.6.0"
    ]
)
