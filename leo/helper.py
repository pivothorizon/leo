import os
from typing import Optional

import jinja2
from jinja2 import FileSystemLoader
from typing.io import TextIO

from .clicontext import CliContext

_loader = jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
_jinja_env = jinja2.Environment(keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True,
                                loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'template')))
_template_folder = 'template'


def make_model_template(
        context: CliContext,
        target: Optional[TextIO] = None) -> Optional[str]:
    """
    Writes a template for implementations of the LeoModel ABC.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the output to. If None, the output is returned.

    :return: The template as a string if target is None, otherwise nothing.

    """
    return _make_template('model_template.jinja2', context, target)


def make_schema_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
        Writes a schema template for implementations of the LeoModel Request and Response parameters .

        :param context: Cli context which captures command line arguments and provides utility methods
        :param target: A stream to write the output to. If None, the output is returned.

        :return: The template as a string if target is None, otherwise nothing.

    """
    return _make_template('schema_template.jinja2', context, target)


def make_api_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Writes a basic API for accessing a BaseModel instance.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the output to. If None, the output is returned.
    :return: The API as a string if target is None, otherwise nothing.
    """
    if context.use_flask:
        return _make_template('api/flask.jinja2', context, target)
    elif context.use_falcon:
        return _make_template('api/falcon.jinja2', context, target)
    raise AssertionError(f'Web Framework {context.web_framework} has not been implemented.')


def make_readme_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Writes the README.md file for a new project.
    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the output to. If None, the output is returned.
    :return: The README as a string if target is None, otherwise nothing.
    """
    return _make_template('readme.jinja2', context, target)


def make_gitignore_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generates .gitignore file for the project with some default folders and files included
    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the output to. If None, the output is returned.
    :return: The .gitignore file content as a string if target is None, otherwise nothing.
    """
    return _make_template('gitignore.jinja2', context, target)

def make_cli_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Writes a project-specific CLI.
    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the output to. If None, the output is returned.
    :return: The cli.py file as a string if target is None, otherwise nothing.
    """
    return _make_template('cli_template.jinja2', context, target)


def make_config_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the output to. If None, the output is returned.
    :return: The config.py file as a string if target is None, otherwise nothing.
    """
    return _make_template('config.py.jinja2', context, target)


def make_model_repo_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """

        :param context: Cli context which captures command line arguments and provides utility methods
        :param target: A stream to write the output to. If None, the output is returned.
        :return: The modelrepo.py file as a string if target is None, otherwise nothing.
        """
    return _make_template('repo/modelrepo.py.jinja2', context, target)


def make_data_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """

        :param context: Cli context which captures command line arguments and provides utility methods
        :param target: A stream to write the output to. If None, the output is returned.
        :return: The modelrepo.py file as a string if target is None, otherwise nothing.
        """
    return _make_template('data.py.jinja2', context, target)


def make_train_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """

        :param context: Cli context which captures command line arguments and provides utility methods
        :param target: A stream to write the output to. If None, the output is returned.
        :return: The pipeline.py file as a string if target is None, otherwise nothing.
        """
    return _make_template('train.py.jinja2', context, target)


def _make_template(template_name: str, context: CliContext, target: Optional[TextIO] = None, **template_args) -> \
        Optional[str]:
    template = _loader.load(_jinja_env, f'{_template_folder}/{template_name}')
    all_args = context.get_cli_dict().copy()
    all_args.update(**template_args)
    result = template.render(**all_args)
    return _write(result, target)


def _write(result: str, target: Optional[TextIO] = None) -> Optional[str]:
    if target:
        target.write(result)
    else:
        return result


def make_sphinx_index(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate the index.rst file needed by Sphinx to make documentation for a new project.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the index.rst file to. If None, the file will be returned as a string.

    :return: The index.rst file contents, except if the target parameter is given.

    """
    return _make_template('index.rst.jinja2', context, target)


def make_dockerfile(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate a Dockerfile which can be used to run the API as a Flask app.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the Dockerfile file to. If None, the file will be returned as a string.

    :return: The Dockerfile contents, except if the target parameter is given.

    """
    if context.use_pyspark:
        return _make_template(os.path.join('dockerfile', 'spark.jinja2'), context, target)
    return _make_template(os.path.join('dockerfile', 'normal.jinja2'), context, target)


def make_docker_compose_file(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate a docker-compose.yml file which can be used for local development

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the Dockerfile file to. If None, the file will be returned as a string.

    :return: The docker-compose.yml contents, except if the target parameter is given.
    """
    return _make_template('docker-compose.yml.jinja2', context, target)


def make_prometheus_config_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate a prometheus.yml file which will be imported to prometheus docker image for registering api as a target

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the Dockerfile file to. If None, the file will be returned as a string.

    :return: prometheus.yml file contents, except if the target parameter is given.

    """
    return _make_template('prometheus.yml.jinja2', context, target)


def make_init_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate an __init__.py file for the 'project_name' package.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the file to. If None, the file will be returned as a string.

    :return: __init__.py file contents, except if the target parameter is given.

    """
    if context.use_flask:
        return _make_template('api/flask_init.jinja2', context, target)
    elif context.use_falcon:
        return _make_template('api/falcon_init.jinja2', context, target)
    raise AssertionError(f'Web Framework {context.web_framework} has not been implemented.')


def make_metrics_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate a class for reporting metrics to Prometheus.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the file to. If None, the file will be returned as a string.

    :return: metrics.py file contents, except if the target parameter is given.

    """
    if context.use_flask:
        return _make_template('metrics/flask.jinja2', context, target)
    elif context.use_falcon:
        return _make_template('metrics/falcon.jinja2', context, target)
    raise AssertionError(f'Web Framework {context.web_framework} has not been implemented.')


def make_test_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate a stub test file for the new project.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the file to. If None, the file will be returned as a string.

    :return: {{ project_name }}_tests.py file contents, except if the target parameter is given.

    """
    print(context.web_framework)
    return _make_template('tests.jinja2', context, target)


def make_kong_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate a script to initialize Kong for the new project.
    The script will be called by Docker Compose.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the file to. If None, the file will be returned as a string.

    :return: The script contents, except if the target parameter is given.

    """
    return _make_template('kong_setup_service.sh.jinja2', context, target)


def make_requirements_template(context: CliContext, target: Optional[TextIO] = None) -> Optional[str]:
    """
    Generate requirements txt file based on choices.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target: A stream to write the file to. If None, the file will be returned as a string.

    :return: The script contents, except if the target parameter is given.
    """
    return _make_template('requirements.txt.jinja2', context, target)


def make_kubernetes_templates(context: CliContext, target_directory: str) -> None:
    """
    Generate Kubernetes Pod templates and Services for the new project.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target_directory: The directory to place the generated files in.

    """

    def _make(name: str, sub_dir: str):
        with open(os.path.join(target_directory, sub_dir, f'{name}_pod_template.yml'), 'w') as f:
            _make_template(f'kubernetes/{sub_dir}/{name}_pod_template.yml.jinja2', context, f)
        with open(os.path.join(target_directory, sub_dir, f'{name}_service.yml'), 'w') as f:
            _make_template(f'kubernetes/{sub_dir}/{name}_service.yml.jinja2', context, f)

    def _make_main(sub_dir: str):
        with open(os.path.join(target_directory, sub_dir, f'main_deployment.yml'), 'w') as f:
            _make_template(f'kubernetes/{sub_dir}/main_deployment_template.yml.jinja2', context, f)
        with open(os.path.join(target_directory, sub_dir, f'main_service.yml'), 'w') as f:
            _make_template(f'kubernetes/{sub_dir}/main_service.yml.jinja2', context, f)

    _make_main('local')
    _make_main('prod')

    if context.use_elk:
        _make('elastic', 'local')
        _make('kibana', 'local')
        _make('logstash', 'local')
    if context.use_prometheus:
        _make('prometheus', 'local')
        _make('grafana', 'local')
    if context.use_graphite:
        _make('graphite', 'local')
    if context.use_kong:
        _make('kong', 'local')
        _make('kong_db', 'local')


def make_graphite_templates(context: CliContext, target_directory: str) -> None:
    """
    Generate configuration files for the Graphite stack used in the new project.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target_directory: The directory to place the generated files in.

    """

    def _make(name: str):
        with open(os.path.join(target_directory, f'{name}.conf'), 'w') as f:
            _make_template(f'graphite/{name}.conf.jinja2', context, f)

    _make('aggregation-rules')
    _make('carbon')
    _make('relay-rules')
    _make('rewrite-rules')
    _make('storage-aggregation')
    _make('storage-schemas')


def make_elk_templates(context: CliContext, target_directory: str) -> None:
    """
    Generate configuration files for the ELK stack used in the new project.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target_directory: The directory to place the generated files in.

    """

    def _make(name: str):
        with open(os.path.join(target_directory, f'{name}'), 'w') as f:
            _make_template(f'elk/{name}.jinja2', context, f)

    _make('elasticsearch.yml')
    _make('kibana.yml')
    _make('logstash.conf')
    _make('logstash.yml')


def make_grafana_templates(context: CliContext, target_directory: str) -> None:
    """
    Generate configuration files for the Grafana visualizations.

    :param context: Cli context which captures command line arguments and provides utility methods
    :param target_directory: The directory to place the generated files in.

    """
    with open(os.path.join(target_directory, 'grafana.ini'), 'w') as f:
        _make_template('grafana/grafana.ini.jinja2', context, f)

    os.mkdir(os.path.join(target_directory, 'provisioning'))
    os.mkdir(os.path.join(target_directory, 'provisioning', 'datasources'))
    os.mkdir(os.path.join(target_directory, 'provisioning', 'dashboards'))

    with open(os.path.join(target_directory, 'provisioning', 'dashboards', 'provisioning.yaml'), 'w') as f:
        _make_template('grafana/provisioning.yaml.jinja2', context, f)

    if context.use_prometheus:
        with open(os.path.join(target_directory, 'provisioning', 'datasources', 'prometheus.yaml'), 'w') as f:
            _make_template('grafana/prometheus_source.yaml.jinja2', context, f)

        with open(os.path.join(target_directory, 'provisioning', 'dashboards', 'prometheus.json'), 'w') as f:
            _make_template('grafana/prometheus_dashboard.json.jinja2', context, f)

    if context.use_graphite:
        with open(os.path.join(target_directory, 'provisioning', 'datasources', 'graphite.yaml'), 'w') as f:
            _make_template('grafana/graphite_source.yaml.jinja2', context, f)

        with open(os.path.join(target_directory, 'provisioning', 'dashboards', 'graphite.json'), 'w') as f:
            _make_template('grafana/graphite_dashboard.json.jinja2', context, f)
