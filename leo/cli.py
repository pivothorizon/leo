import subprocess
from enum import Enum

import PyInquirer
import shutil
import os
import sys
import keyword
from typing import Callable, Optional, List, Mapping, Type, Union
from getpass import getuser
import socket


from .clicontext import CliContext
from .enums import GatewayOptions, LoggingOptions, MonitoringOptions, WSGIOptions, WebFrameworkOptions, \
    EnvironmentOptions, OSType, LibrarySupport

from .helper import make_dockerfile, make_docker_compose_file, make_readme_template, make_api_template, \
    make_cli_template, make_test_template, \
    make_config_template, make_prometheus_config_template, make_model_template, make_kong_template, \
    make_sphinx_index, make_init_template, make_requirements_template, make_kubernetes_kong_template, \
    make_kubernetes_templates, make_metrics_template, make_graphite_templates, make_elk_templates, \
    make_schema_template, make_grafana_templates, make_data_template, make_model_repo_template, \
    make_train_template


def _copy_files(source: str, destination: str, suffix: Optional[str] = '',
                listener: Optional[Callable[[str, str, str], None]] = (lambda a, b, c: None)):
    root_len = len(source) + 1
    suff_len = len(suffix)

    if os.path.isdir(source):
        for (dirpath, _, filenames) in os.walk(source):
            for f in filenames:
                source_path = os.path.join(dirpath, f)
                target_path = os.path.join(destination, dirpath[root_len:], f[:-suff_len])
                listener(f, source_path, target_path)
                shutil.copyfile(source_path, target_path)
    else:
        shutil.copyfile(source, destination)


download_dependencies = True


def _validate_project_name(candidate: str) -> Union[str, bool]:
    if len(candidate) == 0:
        return 'You must specify a value.'
    if not candidate.isidentifier():
        return f'{candidate} is not a valid Python identifier.'
    if keyword.iskeyword(candidate):
        return f'{candidate} is a reserved keyword.'
    if candidate in dir(__builtins__):
        return f'{candidate} is the name of a Python built-in.'
    return True


def _choices_for_enum(enum_cls: Type[Enum], none_is_an_option: bool) -> List[Mapping[str, str]]:
    choices = [{'name': name, 'value': enum.value}
               for name, enum in enum_cls.__members__.items()]
    if none_is_an_option:
        choices.append({'name': 'None', 'value': 'None'})
    return choices


def _not_empty(candidate: str) -> Union[str, bool]:
    if len(candidate) == 0:
        return 'You must specify a value.'
    return True


def _validate_library_choices(choices: List[str]) -> None:
    if len(choices) == 1 and choices[0] == LibrarySupport.MLEAP.value:
        print('\033[1mError: MLeap depends upon at least one other library, like Spark or Tensorflow. '
              'You cannot select it by itself.\033[0m', file=sys.stderr)
        exit(1)


_create_questions = [
    {
        'type': 'input',
        'name': 'author',
        'message': 'Who is the author of the new project?',
        'default': getuser(),
        'validate': _not_empty
    }, {
        'type': 'input',
        'name': 'name',
        'message': 'What is the name of the new project? (Should be a valid Python identifier)',
        'validate': _validate_project_name
    }, {
        'type': 'input',
        'name': 'version',
        'message': 'What is the version number of the project?',
        'default': '1.0.0',
        'validate': _not_empty
    }, {
        'type': 'list',
        'name': 'web_framework',
        'message': 'Which web framework would you like to use?',
        'choices': _choices_for_enum(WebFrameworkOptions, False),
        'default': WebFrameworkOptions.FLASK.value
    }, {
        'type': 'list',
        'name': 'environment_type',
        'message': 'Which type of Python environment would you like to use?',
        'choices': _choices_for_enum(EnvironmentOptions, True),
        'default': 'None'
    }, {
        'type': 'list',
        'name': 'log',
        'message': 'Which logging type would you like to use?',
        'choices': _choices_for_enum(LoggingOptions, True),
        'default': 'None'
    }, {
        'type': 'list',
        'name': 'monitor',
        'message': 'Which monitoring type would you like to use?',
        'choices': _choices_for_enum(MonitoringOptions, True),
        'default': 'None'
    }, {
        'type': 'list',
        'name': 'gateway',
        'message': 'Which API gateway would you like to use?',
        'choices': _choices_for_enum(GatewayOptions, True),
        'default': 'None'
    }, {
        'type': 'list',
        'name': 'wsgi',
        'message': 'Which WSGI type would you like to use?',
        'choices': _choices_for_enum(WSGIOptions, False),
        'default': WSGIOptions.GUNICORN
    }, {
        'type': 'checkbox',
        'name': 'libraries',
        'message': 'Which libraries would you like to enable support for?',
        'choices': [
            {
                'name': name,
                'value': val.value
            } for name, val in LibrarySupport.__members__.items()
        ],
    }, {
        'type': 'confirm',
        'name': 'docker',
        'message': 'Would you like to add Docker support?',
        'default': False
    }, {
        'type': 'confirm',
        'name': 'kubernetes',
        'message': 'Would you like to add Kubernetes support? Note that if you say yes, docker support will be added automatically regardless of your choice before',
        'default': False
    }
]


def create(args):
    context = CliContext(args)
    _validate_library_choices(args['libraries'])  # PyInquirer does not (yet?) support validation on checkboxes, so we have to do it manually.
    _print_console(f'Starting project generation for {context.root_dir_name}', True)
    _generate_project_files(context)
    _generate_package_files(context)
    _create_virtual_environment(context)
    _generate_documentation(context)
    _print_console(f'Created project {context.root_dir_name}', True)


def _generate_project_files(context: CliContext) -> None:
    _print_console('Generating project files', True)

    if os.path.isdir(context.root_dir_name):
        response = PyInquirer.prompt({
            'type': 'confirm',
            'name': 'overwrite',
            'message': f'A directory called {os.path.abspath(context.root_dir_name)} already exists. '
                       'Do you want to overwrite it? (This will erase the current contents of the directory.)',
            'default': False
        })
        if response['overwrite']:
            shutil.rmtree(context.root_dir_name)
        else:
            print('Cancelled.', file=sys.stderr)
            exit(1)

    # Create root directory for the new project
    os.mkdir(context.root_dir_name)
    os.mkdir(os.path.join(context.root_dir_name, 'tests'))
    os.mkdir(os.path.join(context.root_dir_name, 'models'))
    if context.kubernetes:
        _generate_kubernetes_files(context)

    if context.docker:
        _generate_docker_files(context)

    with open(os.path.join(context.root_dir_name, f'README.md'), 'w') as f:
        make_readme_template(context, f)
    with open(os.path.join(context.root_dir_name, f'{context.module_name}cli.py'), 'w') as f:
        make_cli_template(context, f)
    with open(os.path.join(context.root_dir_name, 'tests', f'{context.module_name}_tests.py'), 'w') as f:
        make_test_template(context, f)
    with open(os.path.join(context.root_dir_name, 'requirements.txt'), 'w') as f:
        make_requirements_template(context, f)

    if context.use_elk:
        _print_console('Generating ELK directories and files')
        elk_path = os.path.join(context.root_dir_name, 'elk')
        os.mkdir(elk_path)
        make_elk_templates(context, elk_path)

    if context.use_kong:
        _print_console('Generating Kong directories and files')
        os.mkdir(os.path.join(context.root_dir_name, 'kong'))
        with open(os.path.join(context.root_dir_name, 'kong', 'setup-service.sh'), 'w') as f:
            make_kong_template(context, f)
        with open(os.path.join(context.root_dir_name, 'kong', 'setup-service-kube.sh'), 'w') as f:
            make_kubernetes_kong_template(context, f)

    if context.use_prometheus or context.use_graphite:
        _print_console('Generating Grafana directories and files')
        grafana_dir = os.path.join(context.root_dir_name, 'grafana')
        os.mkdir(grafana_dir)
        make_grafana_templates(context, grafana_dir)

    _print_console(f'Project files has been created for {context.root_dir_name}', True)


def _generate_docker_files(context):
    with open(os.path.join(context.root_dir_name, 'Dockerfile'), 'w') as f:
        make_dockerfile(context, f)
    with open(os.path.join(context.root_dir_name, 'docker-compose.yml'), 'w') as f:
        make_docker_compose_file(context, f)


def _generate_kubernetes_files(context):
    os.mkdir(os.path.join(context.root_dir_name, 'kubernetes'))
    make_kubernetes_templates(context, os.path.join(context.root_dir_name, 'kubernetes'))


def _generate_package_files(context: CliContext) -> None:
    _print_console('Generating package files', True)

    # Create module directory under project root directory
    os.mkdir(context.package_path)

    def _print(_f: str, source_path: str, target_path: str) -> None:
        _print_console(f'Creating package file {target_path} from {_f} ({source_path})')

    if context.use_pyspark:
        shutil.copyfile(os.path.join(context.package_files_path, 'spark_util.py.dist'),
                    os.path.join(context.package_path, 'spark_util.py'))

    if context.use_mleap:
        shutil.copyfile(os.path.join(context.package_files_path, 'mleapsparkmodel.py.dist'),
                        os.path.join(context.package_path, 'mleapsparkmodel.py'))

    with open(os.path.join(context.package_path, '__init__.py'), 'w') as f:
        make_init_template(context, f)
    with open(os.path.join(context.package_path, 'model.py'), 'w') as f:
        make_model_template(context, f)
    with open(os.path.join(context.package_path, 'schema.py'), 'w') as f:
        make_schema_template(context, f)
    with open(os.path.join(context.package_path, 'api.py'), 'w') as f:
        make_api_template(context, f)
    with open(os.path.join(context.package_path, 'config.py'), 'w') as f:
        make_config_template(context, f)
    with open(os.path.join(context.package_path, 'modelrepo.py'), 'w') as f:
        make_model_repo_template(context, f)
    with open(os.path.join(context.package_path, 'data.py'), 'w') as f:
        make_data_template(context, f)
    with open(os.path.join(context.package_path, 'train.py'), 'w') as f:
        make_train_template(context, f)
    if context.monitor != 'None':
        _print_console(f'Generating metric files!: {context.monitor}')
        with open(os.path.join(context.package_path, 'metrics.py'), 'w') as f:
            make_metrics_template(context, f)
        _generate_metrics_files(context)
    _print_console('Package files has been generated successfully', True)


def _generate_metrics_files(context: CliContext) -> None:
    if context.use_prometheus:
        _print_console('Generating prometheus config file')
        # Create prometheus directory under project root directory
        os.mkdir(context.prometheus_dir_path)
        with open(os.path.join(context.prometheus_dir_path, 'prometheus.yml'), 'w') as f:
            make_prometheus_config_template(context, f)
    elif context.use_graphite:
        _print_console('Generating Graphite stack config files')
        dir_name = os.path.join(context.root_dir_name, 'graphite')
        os.mkdir(dir_name)
        make_graphite_templates(context, dir_name)
    elif context.monitor != 'None':
        raise AssertionError(f'Monitoring option {context.monitor} has not been implemented.')


def _create_virtual_environment(context):
    _print_console('Creating virtual environment', True)
    if context.environment_type != 'None':
        try:
            socket.setdefaulttimeout(2.0)
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect(('8.8.8.8', 80))
        except socket.error as ex:
            print(f'\033[1mAn internet connection is required to setup the environment, but you don\'t appear to have'
                  f' a working one. ({ex})\033[0m', file=sys.stderr)
            exit(1)
    if context.use_virtualenv:
        return _create_virtualenv_environment(context)
    elif context.use_conda:
        return _create_conda_environment(context)
    elif context.environment_type != 'None':
        raise AssertionError(f'Environment option {context.environment_type} has not been implemented.')


def _create_virtualenv_environment(context):
    working_directory = os.path.join(os.getcwd(), context.root_dir_name)
    _print_console(
        f'Creating {EnvironmentOptions.VIRTUALENV.value} environment named venv on path: {working_directory}')
    if download_dependencies:
        subprocess.call(['python3','-m', 'venv', '--copies','--clear', 'venv'], cwd=working_directory)
    else:
        subprocess.call(['python3','-m', 'venv', '--copies','--clear', '--without-pip', 'venv'], cwd=working_directory)
    _print_console(f'{EnvironmentOptions.VIRTUALENV.value} environment venv created successfully')
    _print_console('Installing dependencies in virtual environment venv')
    if _get_os() == OSType.POSIX:
        binary_directory_name = 'bin'
    else:  # Assuming Windows
        binary_directory_name = 'Scripts'
    subprocess.call(
        [os.path.join('venv', binary_directory_name, 'python'), '-m', 'pip', 'install', '-r', 'requirements.txt',
         '--no-warn-script-location'], cwd=working_directory)
    _print_console('Dependencies has been installed successfully')


def _create_conda_environment(context) -> None:
    working_directory = os.path.join(os.getcwd(), context.root_dir_name)
    _print_console(f'Creating {EnvironmentOptions.CONDA.value} environment on named {context.module_name}_env')
    _print_console(f'Checking {EnvironmentOptions.CONDA.value} version')
    subprocess.call(['conda', '--version'])
    subprocess.call(['conda', 'create', '-y', '-n', f'{context.module_name}_env'])
    _print_console(f'{EnvironmentOptions.CONDA.value} environment conda_env has been created successfully')


def _generate_documentation(context) -> None:
    _print_console('Generating Sphinx directories and files for documentation under docs directory', True)
    # Create docs directory under project root directory
    os.mkdir(context.docs_dir_path)
    subprocess.call(['sphinx-quickstart', '-q', '--makefile', '--ext-autodoc', '--project', context.root_dir_name,
                     '--author', context.author], cwd=context.docs_dir_path, stdout=subprocess.DEVNULL)
    _print_console('Generating sphinx files and directories')
    with open(os.path.join(context.docs_dir_path, 'index.rst'), 'w') as f:
        make_sphinx_index(context, target=f)
    with open(os.path.join(context.docs_dir_path, 'conf.py'), 'at') as f:
        f.writelines(['\nimport sys\n', 'import os\n\n', 'sys.path.insert(0, os.path.abspath(\'..\'))\n',
                      'extensions.append(\'sphinx.ext.autosummary\')\n',
                      'autosummery_generate = True'])


def _print_console(msg: str, header: bool = False):
    if header:
        print('-' * (len(msg) + 4))
        print(f'| {msg} |')
        print('-' * (len(msg) + 4))
    else:
        print(msg)


def _get_os():
    if os.name == OSType.POSIX.value:
        return OSType.POSIX
    elif os.name == OSType.WINDOWS.value:
        return OSType.WINDOWS
    else:
        return OSType.UNKNOWN


def main():
    if len(sys.argv) < 2:
        print('No command given. Currently, "create" is the only supported command.')
    elif sys.argv[1] == 'create':
        answers = PyInquirer.prompt(_create_questions)
        create(answers)
    else:
        print('Invalid command. Currently, "create" is the only supported command.')


if __name__ == '__main__':
    main()
