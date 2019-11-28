# Leo - A Machine Learning Industrialization Tool

Leo makes it easier to deploy your trained models by wrapping them in a common API, generating API documentation, 
and providing a variety of popular tools for tasks such as logging, monitoring and CI/CD pipelines out of the box.

## The Leo interface
Leo provides a common interface for using trained models. 
A number of popular models have implementations for this interface, 
and more can be written to support any type of model.

Using Leo one can generate a project structure which will include all the 
necessary components for industrialization of ML models

## Workflow

Leo can be installed by installing the python package from PyPI:
`pip install leo-python`

A new Leo project may be generated using the `leo create` command.
This will start an interactive process in which you can choose to
enable components of various types, which are listed below. Except for a
choice of web framework, all of these are optional.

Once the project has been generated, you will be able to implement the Leo
interface. The module containing it is `<<project name>>.model`, and the
name of the class is the same as the project name. The only method which must
always be implemented by the user is `predict`, which should invoke the model
on the provided input. Additionally, it may be necessary to implement
`load_model`, which should read a trained model from a file. The default
implementation will assume the model is stored as a 
[pickle](https://docs.python.org/3/library/pickle.html), though no assumptions
are made as to the type of the pickled object. If your model is stored in a
different format, or if special steps must be taken to load it, you will have to override `load_model`.

After the interface is implemented and a model has been trained, the API can
be deployed. If you chose to enable Docker and/or Kubernetes support (see below),
the required files will have already been generated. Remember to add any dependencies
which you have added yourself to the `requirements.txt` file before deploying.
Refer to the next section for details on how to deploy the API.

## Project CLI
As part of creating a new project, Leo will generate a project-specific CLI.
This interface can be used to deploy the API using either Docker or Kubernetes,
provided that those options were enabled during the creation of the project.

It goes without saying that in order to deploy the API through Docker, Docker
must first be correctly installed. If so, then the command
`python <<project name>>cli.py deploy docker` will create and start the
required containers. It is recommended to run this command within the
project's virtual environment. The command 
`python <<project name>>cli.py undeploy docker` will stop the containers,
though it will not delete them.

To deploy with Kubernetes, both it and Docker must be installed. Additionally,
Kubernetes must be properly configured. The CLI will use `kubectl` to start
the required Pods and Services, and so it will use whatever cluster `kubectl` is
configured to use. If you have not set up a Kubernetes cluster, consider
using [Minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/).
The command for deploying with Kubernetes is 
`python <<project name>>cli.py deploy kubernetes`, and the command for stopping it is
`python <<project name>>cli.py undeploy kubernetes`. If the deployment is
unsuccessful for any reason, it is recommended to run the `undeploy` command
before trying again.

## Available Components
### Web Frameworks (Required)
Unlike the other components, a choice of web framework 
is required to generate a project. The chosen framework will be used to
generate the API.

- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Falcon](https://falconframework.org)

### Environment (Recommended)
It is generally considered good practice to maintain separate environments
for each Python project being developed on a system. The tools below can be
used to generate such an environment, but if you want to use your own or
don't want to use any, simply don't select any of these.

- [Virtualenv](https://virtualenv.pypa.io/en/latest/)
- [Conda](https://docs.conda.io/en/latest/)

### Logging (Optional)
Currently, Leo only supports a single logging framework, the ELK
[(Elasticsearch, Logstash, Kibana)](https://www.elastic.co/products/elastic-stack)
Stack. However, you may choose not to use it if you prefer.

### Monitoring (Optional)
The following tools may be used to collect metrics on the API's performance.
The data collected by either tool can be viewed using [Grafana](https://grafana.com),
which will also be installed if a monitoring tool is selected.

- [Prometheus](https://prometheus.io)
- [Graphite](https://graphiteapp.org)

### API Gateway (Optional)
Currently, Leo only supports [Kong](https://konghq.com) as an API gateway.
Initially, Leo creates a basic Kong setup, which can be extended by the user
with the many available plugins. When using Kong, the API will only be accessible
through it. See the port list below for details

### Docker (Optional)
[Docker](https://www.docker.com) is a much used containerization tool. If Docker
support is selected, a Dockerfile will be generated, which can then be used
to build an appropriate Docker image.

### Kubernetes (Optional)
[Kubernetes](https://kubernetes.io) may be used to ease deployment and management.
If Kubernetes support is selected, the required configuration files for each
component will be created. Specifically, Leo will generate a Pod and a Service
for each independent component.

Note that if Kubernetes is selected, Docker support will also be enabled
even if that is not explicitly selected itself.

### Spark
Leo supports the use of [Apache Spark](https://spark.apache.org) for training and evaluating models. 
If Spark support is enabled during project creation, Leo will set up the data and training code to use
Spark Pipelines, instead of leaving it fully up to you. Of course, you may still change these functions 
to use Spark in a different way, if desired. Certain other features will be enabled as well, such as
modifications to the Dockerfile (if Docker support is selected) and lazy initialization of a Spark Session
object.

To use Spark, it must first be installed on the system, with the $SPARK_HOME environment variable correctly set.
