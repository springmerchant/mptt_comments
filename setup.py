from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(
    name='django-mptt-comments',
    version="0.1",
    package_dir={'mptt_comments': 'mptt_comments'},
    packages=['mptt_comments', 'mptt_comments.templatetags'],
    description='Django Mptt Comments is a simple way to display threaded comments instead of the django contrib comments.',
    author='fivethreeo',
    author_email='',
    license='BSD License',
    url='http://bitbucket.org/fivethreeo/django-mptt-comments/',
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        'Development Status :: 0.1 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
)
