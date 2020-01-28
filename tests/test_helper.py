import unittest
from leo.helper import *
from .shared import *
from os import path
import shutil


class HelperTest(unittest.TestCase):

    def read_file_content_from_resources(self, filename: str):
        with open(path.join(path.dirname(__file__), 'resources', filename), 'r') as f:
            return f.read()

    def assert_file_content(self, template: str, filename: str):
        content = self.read_file_content_from_resources(filename)
        assert template == content

    def test_make_model_template(self):
        template = make_model_template(test_context)
        self.assert_file_content(template, 'model.py')

    def test_make_schema_template(self):
        template = make_schema_template(test_context)
        self.assert_file_content(template, 'schema.py')

    def test_make_dockerfile(self):
        template = make_dockerfile(test_context)
        self.assert_file_content(template, 'Dockerfile')

    def test_make_readme_template(self):
        template = make_readme_template(test_context)
        self.assert_file_content(template, 'readme.md')

    def test_make_docker_compose_file(self):
        template = make_docker_compose_file(test_context)
        self.assert_file_content(template, 'docker-compose.yaml')

    def test_make_api_template(self):
        template = make_api_template(test_context)
        self.assert_file_content(template, 'api.py')

    def test_make_gitignore_template(self):
        template = make_gitignore_template(test_context)
        self.assert_file_content(template, 'gitignore')

    def test_make_cli_template(self):
        template = make_cli_template(test_context)
        self.assert_file_content(template, 'cli.py')

    def test_make_config_template(self):
        template = make_config_template(test_context)
        self.assert_file_content(template, 'config.py')

    def test_make_model_repo_template(self):
        template = make_model_repo_template(test_context)
        self.assert_file_content(template, 'model_repo.py')

    def test_make_data_template(self):
        template = make_data_template(test_context)
        self.assert_file_content(template, 'data.py')

    def test_make_train_template(self):
        template = make_train_template(test_context)
        self.assert_file_content(template, 'train.py')

    def test_make_sphinx_index(self):
        template = make_sphinx_index(test_context)
        self.assert_file_content(template, 'index.rst')

    def test_make_prometheus_config_template(self):
        template = make_prometheus_config_template(test_context)
        self.assert_file_content(template, 'prom_config.yaml')

    def test_make_init_template(self):
        template = make_init_template(test_context)
        self.assert_file_content(template, 'init.py')

    def test_make_metrics_template(self):
        template = make_metrics_template(test_context)
        self.assert_file_content(template, 'metrics.py')

    def test_make_test_template(self):
        template = make_test_template(test_context)
        self.assert_file_content(template, 'tests.py')

    def test_make_kong_template(self):
        template = make_kong_template(test_context)
        self.assert_file_content(template, 'kong_setup_service.sh')

    def test_make_requirements_template(self):
        template = make_requirements_template(test_context)
        self.assert_file_content(template, 'requirements.txt')

    # =========================== GENERATED FILES TEST ==================================#
    resources_folder_path = path.join(path.dirname(__file__), 'resources')
    generated_folder_path = path.join(resources_folder_path, 'generated')

    def assert_generated_file_content(self, parent_folder: str, folder: str, filename: str, subfolder: str = None):
        subpath = path.join(folder, subfolder) if subfolder is not None else folder
        expected_file_path = path.join(self.resources_folder_path, parent_folder, subpath)
        generated_file_path = path.join(self.resources_folder_path, 'generated', parent_folder, subpath)

        self.assert_files(expected_file_path, generated_file_path, filename)

    def assert_files(self, expected_file_path: str, generated_file_path: str, filename: str):
        with open(path.join(expected_file_path, filename), 'r') as f:
            expected_content = f.read()
        with open(path.join(generated_file_path, filename), 'r') as f:
            generated_content = f.read()
        assert expected_content == generated_content

    def assert_kubernetes_files(self, folder: str, filename: str):
        self.assert_generated_file_content(parent_folder='kubernetes', folder=folder, filename=filename)

    def assert_grafana_files(self, folder: str, filename: str, subfolder: str = None):
        self.assert_generated_file_content(parent_folder='grafana', folder=folder, filename=filename,
                                           subfolder=subfolder)

    def test_make_kubernetes_template(self):
        target_directory = path.join(self.generated_folder_path, 'kubernetes')
        make_kubernetes_templates(test_context, target_directory)
        self.assert_kubernetes_files('local', 'elastic_pod_template.yml')
        self.assert_kubernetes_files('local', 'elastic_service.yml')
        self.assert_kubernetes_files('local', 'grafana_pod_template.yml')
        self.assert_kubernetes_files('local', 'grafana_service.yml')
        self.assert_kubernetes_files('local', 'kibana_pod_template.yml')
        self.assert_kubernetes_files('local', 'kibana_service.yml')
        self.assert_kubernetes_files('local', 'kong_db_pod_template.yml')
        self.assert_kubernetes_files('local', 'kong_db_service.yml')
        self.assert_kubernetes_files('local', 'kong_pod_template.yml')
        self.assert_kubernetes_files('local', 'kong_service.yml')
        self.assert_kubernetes_files('local', 'logstash_pod_template.yml')
        self.assert_kubernetes_files('local', 'logstash_service.yml')
        self.assert_kubernetes_files('local', 'prometheus_pod_template.yml')
        self.assert_kubernetes_files('local', 'prometheus_service.yml')
        self.assert_kubernetes_files('local', 'main_deployment.yml')
        self.assert_kubernetes_files('local', 'main_service.yml')
        self.assert_kubernetes_files('prod', 'main_deployment.yml')
        self.assert_kubernetes_files('prod', 'main_service.yml')
        # Clean up generated files and folders
        kubernetes_dir = os.path.join(path.dirname(__file__), 'resources', 'generated', 'kubernetes')
        shutil.rmtree(kubernetes_dir)
        local_dir = os.path.join(kubernetes_dir, 'local')
        prod_dir = os.path.join(kubernetes_dir, 'prod')
        os.mkdir(kubernetes_dir)
        os.mkdir(local_dir)
        os.mkdir(prod_dir)
        open(path.join(local_dir, '.gitkeep'), 'a').close()
        open(path.join(prod_dir, '.gitkeep'), 'a').close()

    def test_make_grafana_templates_with_prometheus(self):
        target_directory = path.join(self.generated_folder_path, 'grafana')
        make_grafana_templates(test_context, target_directory)
        self.assert_grafana_files(folder='provisioning', subfolder='dashboards', filename='prometheus.json')
        self.assert_grafana_files(folder='provisioning', subfolder='dashboards', filename='provisioning.yaml')
        self.assert_grafana_files(folder='provisioning', subfolder='datasources', filename='prometheus.yaml')
        generated_graphite_dir = path.join(path.dirname(__file__), 'resources', 'generated', 'grafana')
        graphite_dir = path.join(path.dirname(__file__), 'resources', 'grafana')

        self.assert_files(graphite_dir, generated_graphite_dir, 'grafana.ini')

        shutil.rmtree(generated_graphite_dir)
        os.mkdir(generated_graphite_dir)
        open(path.join(generated_graphite_dir, '.gitkeep'), 'a').close()

    def test_make_elk_templates(self):
        target_directory = path.join(self.generated_folder_path, 'elk')
        make_elk_templates(test_context, target_directory)
        generated_elk_folder_path = target_directory
        expected_elk_folder_path = path.join(self.resources_folder_path, 'elk')
        self.assert_files(expected_elk_folder_path, generated_elk_folder_path, 'elasticsearch.yml')
        self.assert_files(expected_elk_folder_path, generated_elk_folder_path, 'kibana.yml')
        self.assert_files(expected_elk_folder_path, generated_elk_folder_path, 'logstash.yml')
        self.assert_files(expected_elk_folder_path, generated_elk_folder_path, 'logstash.conf')
        shutil.rmtree(generated_elk_folder_path)
        os.mkdir(generated_elk_folder_path)
        open(path.join(generated_elk_folder_path, '.gitkeep'), 'a').close()


    def test_make_graphite_templates(self):
        target_directory = path.join(self.generated_folder_path, 'graphite')
        make_graphite_templates(test_context, target_directory)
        generated_graphite_folder_path = target_directory
        expected_graphite_folder_path = path.join(self.resources_folder_path, 'graphite')
        self.assert_files(expected_graphite_folder_path, generated_graphite_folder_path, 'aggregation-rules.conf')
        self.assert_files(expected_graphite_folder_path, generated_graphite_folder_path, 'relay-rules.conf')
        self.assert_files(expected_graphite_folder_path, generated_graphite_folder_path, 'rewrite-rules.conf')
        self.assert_files(expected_graphite_folder_path, generated_graphite_folder_path, 'carbon.conf')
        self.assert_files(expected_graphite_folder_path, generated_graphite_folder_path, 'storage-aggregation.conf')
        self.assert_files(expected_graphite_folder_path, generated_graphite_folder_path, 'storage-schemas.conf')
        shutil.rmtree(generated_graphite_folder_path)
        os.mkdir(generated_graphite_folder_path)
        open(path.join(generated_graphite_folder_path, '.gitkeep'), 'a').close()


if __name__ == '__main__':
    unittest.main()
