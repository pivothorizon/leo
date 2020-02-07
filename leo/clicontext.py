import os


from .enums import MonitoringOptions, LoggingOptions, GatewayOptions, WSGIOptions, WebFrameworkOptions, \
                   EnvironmentOptions, LibrarySupport


class CliContext(object):
    def __init__(self, args):
        self._cli_context_dict = {}
        for option, (enum, default) in {'log': (LoggingOptions, None),
                                        'gateway': (GatewayOptions, None),
                                        'wsgi': (WSGIOptions, WSGIOptions.GUNICORN.value),
                                        'web_framework': (WebFrameworkOptions, WebFrameworkOptions.FALCON.value),
                                        'environment_type': (EnvironmentOptions, None),
                                        'monitor': (MonitoringOptions, None)}.items():
            choice = args[option] if args[option] is not None else default
            self._cli_context_dict.update(**{f'use_{name.lower()}': choice == val.value
                                             for name, val in enum.__members__.items()})
            self._cli_context_dict.update(**{option: choice})

        self._cli_context_dict.update(**{f'use_{name.lower()}': val.value in args['libraries']
                                         for name, val in LibrarySupport.__members__.items()})

        self._cli_context_dict.update(**{
            'name': args['name'],
            'version': args['version'],
            'author': args['author'],
            'root_dir_name': args['name'],
            'project_name': args['name'],
            'module_name': args['name'].lower(),
            'package_path': os.path.join(args['name'], args['name'].lower()),
            'package_files_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'package_files'),
            'prometheus_dir_path': os.path.join(args['name'], 'prometheus'),
            'docs_dir_path': os.path.join(args['name'], 'docs'),
            'cwd': os.path.abspath(os.path.join('.', args['name'])),
            'app_object_name': 'application',
            'kubernetes': args['kubernetes'],
            'docker': args['docker'] or args['kubernetes'],
        })

    def __getattr__(self, item):
        if item.startswith('__') or item not in self._cli_context_dict:
            return self.__dict__[item]
        return self._cli_context_dict[item]

    def get_cli_dict(self):
        return self._cli_context_dict.copy()
