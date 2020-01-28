import argparse
import sys
import subprocess
import os
import yaml

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from testleo.train import train_model
from testleo.modelrepo import ModelRepo


config.load_kube_config()
kubernetes_api = client.CoreV1Api()


class testleoCli(object):
    """
    A CLI for interacting with Leo from the testleo project.
    """

    def __init__(self):
        main_parser = argparse.ArgumentParser(prog='testleocli', description='Interact with testleo')
        main_parser.add_argument('command', help='Command to execute', choices=('train','test', 'deploy', 'undeploy'))
        args = main_parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            main_parser.print_help()
            sys.exit(1)

        getattr(self, args.command)()

    def train(self):
        model = train_model()
        ModelRepo().save_model(model)

    def test(self):
        test_parser = argparse.ArgumentParser(prog='testleocli test',
                                              description='testleo API on a development Flask server.')
        test_parser.add_argument('--flask-host', required=False, nargs=1, type=str,
                                 help='The host to run the development server on. (See "flask run --help")')
        test_parser.add_argument('--flask-port', required=False, nargs=1, type=int,
                                 help='The port to run the development server on. (See "flask run --help")')
        test_parser.add_argument('--flask-debug', action='store_true', help='Run the development server in debug mode.')
        test_parser.add_argument('--use-internal-server', required=False, action='store_true',
                                 help='Use the testing server (Werkzeug) provided by Flask, rather than gunicorn.'
                                      ' If any of the --flask-... options are used, this flag is implied.')

        test_parser.add_argument('--gunicorn-opts', required=False, nargs=argparse.REMAINDER, type=str,
                                 help='Additional options for Gunicorn may be specified after this flag.')

        args = test_parser.parse_args(sys.argv[2:])

        if args.flask_host:
            host = args.flask_host[0]
        else:
            host = '127.0.0.1'

        if args.flask_port:
            port = args.flask_port[0]
        else:
            port = 5000

        debug = args.flask_debug

        using_dev_server = args.use_internal_server or args.flask_host or args.flask_port or args.flask_debug

        if using_dev_server:
            from testleo import application
            application.testing = True
            application.run(host, port, debug)
        else:
            opts = args.gunicorn_opts if args.gunicorn_opts is not None else []
            subprocess.run(['gunicorn', *opts, 'testleo'])
            subprocess.run(['gunicorn', *opts, 'testleo'])



    def deploy(self):
        deploy_parser = argparse.ArgumentParser(prog='testleocli deploy',
                                                description='Deploy the testleo API on either a local Docker or Kubernetes.')
        deploy_parser.add_argument('platform', help='Which platform to deploy to.', choices=('docker', 'kubernetes'))
        args = deploy_parser.parse_args(sys.argv[2:3])

        if not hasattr(self, f'deploy_{args.platform}'):
            deploy_parser.print_help()
            sys.exit(1)

        getattr(self, f'deploy_{args.platform}')()

    def undeploy(self):
        undeploy_parser = argparse.ArgumentParser(prog='testleocli undeploy',
                                                  description='Remove a previous deployment of the testleo API.')
        undeploy_parser.add_argument('platform', help='Which platform the API was deployed to.', choices=('docker', 'kubernetes'))
        args = undeploy_parser.parse_args(sys.argv[2:3])

        if not hasattr(self, f'undeploy_{args.platform}'):
            undeploy_parser.print_help()
            sys.exit(1)

        getattr(self, f'undeploy_{args.platform}')()

    def deploy_docker(self):
        if self._build_docker():
            print('Image built, starting containers.')
            subprocess.run(['docker-compose', '-f', os.path.join(os.getcwd(), 'docker-compose.yml'), 'up', '-d'], capture_output=True)
        else:
            print('Image failed to build.')

    def deploy_kubernetes(self):
        def _load_yaml(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f)

        def _start_service(name: str):
            print(f'Starting {name} Service')
            kubernetes_api.create_namespaced_service(namespace='default', body=_load_yaml(f'kubernetes/local/{name}_service.yml'))

        def _start_component(name: str):
            print(f'Starting {name} Pod')
            response = kubernetes_api.create_namespaced_pod(namespace='default', body=_load_yaml(f'kubernetes/local/{name}_pod_template.yml'))
            while response.status.phase == 'Pending':
                response = kubernetes_api.read_namespaced_pod(namespace='default', name=f'testleo-{name}-pod')
            _start_service(name)

        def _start_deployment(name: str):
            print(f'Starting {name} Deployment')
            response = kubernetes_api.create_namespaced_deployment(namespace='default', body=_load_yaml(f'kubernetes/local/{name}_deployment.yaml'))
            while response.status.phase == 'Pending':
                response = kubernetes_api.read_namespaced_deployment(namespace='default', name=f'testleo-{name}-deployment')
            _start_service(name)


        if self._build_docker() and self._test_kubernetes_setup():
            print('Image built, starting Pods and Services')
            _start_component('db')
            _start_component('kong')
            _start_component('elastic')
            _start_component('kibana')
            _start_component('logstash')
            _start_component('prometheus')
            _start_component('grafana')
            _start_deployment('main')
        else:
            print('Image failed to build.')

    def undeploy_docker(self):
        subprocess.run(['docker-compose', '-f', os.path.join(os.getcwd(), 'docker-compose.yml'), 'down', '-v'], capture_output=True)

    def undeploy_kubernetes(self):
        print('Stopping main deployment')
        try:
            kubernetes_api.delete_namespaced_deployment(namespace='default', body={}, name=f'testleo-main-deployment')
        except ApiException as e:
                if e.status != 404:
                    raise e

        def _stop_component(name: str):
            print(f'Stopping {name} Service')
            try:
                kubernetes_api.delete_namespaced_service(namespace='default', body={}, name=f'testleo-{name}-service')
            except ApiException as e:
                if e.status != 404:
                    raise e

            print(f'Stopping {name} Pod')
            try:
                kubernetes_api.delete_namespaced_pod(namespace='default', body={}, name=f'testleo-{name}-pod')
            except ApiException as e:
                if e.status != 404:
                    raise e

        _stop_component('db')
        _stop_component('kong')
        _stop_component('elastic')
        _stop_component('kibana')
        _stop_component('logstash')
        _stop_component('prometheus')
        _stop_component('grafana')

    def _build_docker(self):
        if not self._test_docker_setup():
            return False
        print('Building Docker image...')
        result = subprocess.run(['docker', 'build', '-t', 'testleo-app:1.0.0', os.getcwd()], capture_output=True)
        return result.returncode == 0

    @staticmethod
    def _test_docker_setup():
        print('Testing Docker installation.')
        which = subprocess.run(['which', 'docker'], capture_output=True)
        if which.returncode == 1:
            print('Error: Could not find \'docker\' command. Check your Docker installation.', file=sys.stderr)
            return False

        which_compose = subprocess.run(['which', 'docker-compose'], capture_output=True)
        if which_compose.returncode == 1:
            print('Error: Could not find \'docker-compose\' command. Check your Docker installation.', file=sys.stderr)
            return False

        hello_world = subprocess.run(['docker', 'run', '--rm', 'hello-world'], capture_output=True)
        subprocess.run(['docker', 'rmi', 'hello-world'], capture_output=True)
        if hello_world.returncode != 0:
            print(f'Error: Running \'hello-world\' Docker image failed. Check you Docker installation. ({hello_world.returncode})', file=sys.stderr)
            return False
        return True

    @staticmethod
    def _test_kubernetes_setup():
        print('Testing Kubernetes installation.')
        which = subprocess.run(['which', 'kubectl'], capture_output=True)
        if which.returncode == 1:
            print('Error: Could not find \'kubectl\' command. Check your Kubernetes installation.', file=sys.stderr)
            return False

        make_deployment = subprocess.run(['kubectl', 'run', 'kube-test', '--image=k8s.gcr.io/echoserver:latest', '--port=8080'], capture_output=True)
        if make_deployment.returncode != 0:
            print('Error: Could not create Kubernetes deployment. Check your installation.', file=sys.stderr)
            return False

        make_service = subprocess.run(['kubectl', 'expose', 'deployment', 'kube-test', '--type=NodePort'], capture_output=True)
        if make_service.returncode != 0:
            print('Error: Could not create Kubernetes service. Check your installation.', file=sys.stderr)
            subprocess.run(['kubectl', 'delete', 'deployment', 'kube-test'])
            return False

        subprocess.run(['kubectl', 'delete', 'service', 'kube-test'], capture_output=True)
        subprocess.run(['kubectl', 'delete', 'deployment', 'kube-test'], capture_output=True)
        return True

if __name__ == '__main__':
    testleoCli()
