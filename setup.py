from setuptools import find_packages, setup
import leo

setup(
    name='leo',
    version=leo.__version__,
    author='Pivot Horizon',
    author_email='hello@pivothorizon.com',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask>=1.1.1',
        'flask-rest-api>==0.16.1',
        'Jinja2>=2.10.1',
        'marshmallow>=2.20.0',
        'python-logstash>=0.4.6',
        'sphinx>=2.1.2',
        'PyInquirer>=1.0.3',
    ],
    extras_require={"test": ["pytest", "coverage"]},
    entry_points='''
    [console_scripts]
    leo=leo.cli:main
    ''',
    keywords='ml api leo pivothorizon ph kong elk logstash elasticsearch kibana prometheus pylama',
)
