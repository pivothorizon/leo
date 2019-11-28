from setuptools import find_packages, setup

setup(
    name='leo-python',
    version='0.0.5',
    author='Pivot Horizon',
    author_email='leo@pivothorizon.com',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'coverage>=4.5.4',
        'Jinja2>=2.10.1',
        'marshmallow>=3.0.0',
        'pytest>=5.0.1',
        'python-logstash>=0.4.6',
        'sphinx>=2.2.1',
        'pylama>=7.7.1',
        'PyInquirer>=1.0.3'
    ],
    extras_require={"test": ["pytest", "coverage"]},
    entry_points='''
    [console_scripts]
    leo=leo.cli:main
    ''',
    keywords='ml api leo pivothorizon ph kong elk logstash elasticsearch kibana prometheus pylama',
)

