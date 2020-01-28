from leo.clicontext import CliContext

project_name = "testleo"
version = "1.0.0"
author = "vdogan"
log = "elk"
monitor = "prometheus"
gateway = "kong"
wsgi = "gunicorn"
web = "flask"
environ = "conda"
libraries = "pyspark"
args = {
    "name": project_name,
    "version": version,
    "author": author,
    "log": log,
    "monitor": monitor,
    "gateway": gateway,
    "wsgi": wsgi,
    "web_framework": web,
    "environment_type": environ,
    "libraries": libraries,
    "kubernetes": True,
    "docker": True
}

test_context = CliContext(args)