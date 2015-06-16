# Monasca CI
A continuous integration build environment with automatic and regular testing is a necessity for modern projects. With Monasca
we are not shipping only a single project but rather are shipping a group of projects tightly coupled together as a single system.
This means that CI for the system as a whole is more important than that for individual projects, though it isn't a replacement for
simpler project based CI. This Docker image is a Monasca CI environment that is our solution for testing Monasca as a whole.

## Goals
The goals for our Monasca CI overlap but differ a bit from those of standard project level CI. The primary goals are:

  - Tests the integrated Monasca system not just individual components.
  - Easy Maintenance.
    - Fully automated.
    - Easy to incrementally improve. Most importantly this should apply to the tests run but also the the CI system as a whole.
    - Easy to replicate in different environments.
  - Flexible test configuration.
    - Should be easy to test various configurations, ie different components in our system, ssl or not, fully clustered, large cluster, standalone, etc.
    - Able to simultaneously run multiple environments enabling multiple test configurations and long running tests.
  - Improves team Velocity. The tool needs to improve velocity by enabling fast fail not slow the rate of change as we wait for tests.
    - CI tools that trigger long runs for minor changes then gate on these can slow down team velocity.
      An asynchronous model triggered by checkins and/or a schedule without gating rather with notification of failures
      is used for long running tests to improve velocity.
  - Execution speed.
    - Though it is expected that tests take time a fair amount of optimization work should be done.

As with most CI systems there are number of capabilities it should have including:
  - Notifies the team on any failures.
  - Includes a dashboard with status and build history.
  - Builds the code directly from any branch. Any checkin from master should build, branch checkins optionally.
  - The ability to be running multiple instances at one time so multiple configurations can be tested simultaneously.

There are few things to note that aren't goals:
  - This doesn't require reference production hardware. 
    - Our software should be exactly what is run in production but the hardware this runs on need not be.
    - Relative performance testing can be done but it shouldn't be considered the load production will run.

## Running/Design
Simply run this Docker container and you will have Jenkins server loaded with some CI jobs for Monasca.
You can run the container and have it listen on port 8080 with `docker run -d -p 8080:8080 --name jenkins -v /var/run/docker.sock:/var/run/docker.sock monasca/ci`
For a long running Jenkins you may want to setup a persister volume, `-v /your/home:/var/jenkins_home`

After starting the container will load up the standard Jenkins jobs for Monasca CI. These jobs watch all of the Monasca git repos,
if one has a change it will build it then trigger the Monasca job.
  - The main job will build a clustered Monasca setup using other Docker containers and hit it with tests.
    - For this to work the container needs access to the Docker API. For most installations the arguments '-v /var/run/docker.sock:/var/run/docker.sock'
      accomplish this and this is the assumed setup. For some installations it may be necessary to install a key/cert for Docker and set the DOCKER_HOST
      environmental variable. In such cases the jenkins jobs will need to be modified appropriately.
    - A non-clustered version is possible also.

Notes:
  - The integration tests are in a repo that is also built by Jenkins and for which changes triggers new runs.
  - To facilitate the ease of maintenance and setup the system is built entirely with configuration management tools and stored in a git repo.
    All test jobs and code are pulled from various git repos. The Jenkins jobs are built with
    [Jenkins Job Builder](http://docs.openstack.org/infra/jenkins-job-builder/index.html)
  - The Monasca/CI container is built on the Jenkins offical docker repo with Jenkins, plugins, jjb, vagrant and build Monasca dependencies.
    It should only need updates when one of those components is upgraded.
  - Ideally the build artifacts coming from Jenkins should be Docker containers which we start and link for testing. However we don't yet deploy docker
    in production, so I build the artifacts we do deploy then install and configure each time with the Monasca Ansible roles.

## Todo
- Document recommended minimum requirements.
- Explore better reporting tools for Jenkns.
- Can I watch gerrit patchsets and trigger builds based on them like I could for branches?
- There is an official docker repo for sonarqube, consider adding that to the mix.
