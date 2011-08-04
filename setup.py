from setuptools import setup, find_packages
setup(
    name = "bettercache",
    version = "0.3",
    packages = find_packages(),
    author = "Cox Media Group",
    author_email = "opensource@coxinc.com",
    description = "A suite of better cache tools for Django.",
    license = "MIT",
    url = "https://github.com/coxmediagroup/django-better-cache",
    # could also include long_description, download_url, classifiers, etc.

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine

    # Testing removing from install_requires -MH
    #'django>=1.3,<1.4',

    install_requires = [
        'docutils>=0.3',
    ],

    include_package_data=True,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the package, too:
        '': ['*.msg'],
    },

)

