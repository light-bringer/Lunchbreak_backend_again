import getpass
import json
import os
import sys 
import requests
from fabric.api import env, lcd, local, run, sudo
from fabric.context_managers import cd, hide, quiet, settings
from fabric.contrib import django
from fabric.contrib.files import exists
from fabric.operations import put
import pendulum

django.project('Lunchbreak')
django.settings_module('lunchbreak.Lunchbreak.settings')
started_at = pendulum.now()

# Host
HOST = os.environ.get('LUNCHBREAK_HOST')
HOST = '127.0.0.1'
if not HOST:
    HOST = input('Host: ')

# Fabric environment
env.hosts = [HOST]

env.user = 'root'
env.shell = '/bin/bash -c -l'

# Git information
with hide('running', 'output'):
    with settings(warn_only=True), hide('warnings'):
        git_tag = os.environ.get(
            'TRAVIS_TAG',
            local(
                'git describe --exact-match --tags $(git log -n1 --pretty=\'%h\')',
                capture=True
            )
        )
        
        # sys.exit(git_tag)
    git_commit = os.environ.get(
        'TRAVIS_COMMIT',
        local(
            'git rev-parse --verify HEAD',
            capture=True
        )
    )
    git_previous_commit = local(
        'git rev-parse --verify HEAD~1',
        capture=True
    )
    git_branch = os.environ.get(
        'TRAVIS_BRANCH',
        local(
            'git rev-parse --abbrev-ref HEAD',
            capture=True
        )
    )

if git_tag:
    print('Current git tag: ' + str(git_tag))
    # TRAVIS_BRANCH is set to TRAVIS_TAG when a build is created for a tag
    # This is a bug: https://github.com/travis-ci/travis-ci/issues/4745
    git_branch = 'master'
else:
    print('No current git tag.')
print('Current git commit: ' + str(git_commit))
print('Current git branch: ' + str(git_branch))

is_production = bool(git_tag)
if is_production:
    print('We\'re currently on production!')
is_staging = git_branch == 'master' and not is_production
is_development = git_branch == 'development'
version = 'production' if is_production else 'staging' if not is_development else 'development'

os.environ.setdefault(
    'DJANGO_SETTINGS_VERSION',
    version
)

with lcd('lunchbreak'):
    from django.conf import settings as django_settings  # NOQA
    OPBEAT_APP_ID = getattr(django_settings, 'OPBEAT_APP_ID', None)
    OPBEAT_SECRET_TOKEN = getattr(django_settings, 'OPBEAT_SECRET_TOKEN', None)

    if OPBEAT_APP_ID is None or OPBEAT_SECRET_TOKEN is None:
        OPBEAT_APP_ID = os.environ.get(
            'OPBEAT_APP_ID_PRODUCTION' if is_production else 'OPBEAT_APP_ID_STAGING'
        )
        OPBEAT_SECRET_TOKEN = os.environ.get(
            'OPBEAT_SECRET_TOKEN_PRODUCTION' if is_production else 'OPBEAT_SECRET_TOKEN_STAGING'
        )


def test():
    """Run tox tests."""
    local('tox')


def deploy(username=None, password=None, skiptests=False, check_deploy=False):
    """The regular deployment.

    Tests, pushes new image and updates server."""

    if not skiptests:
        test()
    if check_deploy and git_branch not in ['master', 'development']:
        print('Not deploying, not on the master or development branch.')
        return
    deployer = Deployer()
    push(deployer=deployer)
    deployer.update_server()
    deployer.add_release()


def add_release():
    deployer = Deployer()
    deployer.add_release()


def push(username=None, password=None, deployer=None):
    """Only builds and pushes new image."""
    if deployer is None:
        deployer = Deployer(
            username=username,
            password=password
        )
    deployer.push_images()


def upload_compose_config():
    """Upload new docker-compose configs."""
    deployer = Deployer()
    deployer.update_compose_config()


def upload_docker_folders(everything=True):
    """Upload new docker folders."""
    deployer = Deployer()
    deployer.upload_docker_folders(everything=everything)


def setup():
    """Setup the server."""
    deployer = Deployer()
    deployer.setup()


def nothing():
    """Test constant initialisation."""
    pass


class Deployer:

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def push_images(self):
        """Build and push the image with the associated tags."""
        self._docker_login(remote=False)

        # Create all tags associated with this image
        docker_tags = [
            # Each commit will have a history in the registry
            git_commit,
        ]
        # Each tag will have a history in the registry
        if git_tag:
            docker_tags.append(git_tag)
        if is_production:
            docker_tags.append('production')
        if is_staging:
            docker_tags.append('staging')
        if is_development:
            docker_tags.append('development')

        # Generate all the image names from the tags
        image_names = [self._image_name(tag=tag) for tag in docker_tags]

        build_args = {
            'version': version,
            'certificate_type': 'production' if is_production or is_staging else 'development'
        }

        # Build the image and tag it with all of the names
        local(
            'docker build -t {image_names} --build-arg {build_args} .'.format(
                image_names=' -t '.join(image_names),
                build_args=' --build-arg '.join(
                    ['%s=%s' % (key, value) for key, value in build_args.items()]
                )
            )
        )

        # Push all associated tags
        for image_name in image_names:
            local(
                'docker push {image_name}'.format(
                    image_name=image_name
                )
            )

    def update_server(self):
        """Make sure the remote server updates its containers."""
        self._setup_ufw()
        self._setup_fail2ban()

        self._compose_up(
            service='lunchbreak_' + version
        )

    def update_compose_config(self, configs=None):
        self._compose_up(
            configs=configs
        )

    def upload_docker_folders(self, everything=False):
        folders = ['lunchbreak', 'config']
        if everything:
            for folder in folders:
                put(
                    local_path='docker/' + folder,
                    remote_path='/etc/lunchbreak/docker'
                )
        else:
            for folder in folders:
                put(
                    local_path='docker/' + folder + '/*',
                    remote_path='/etc/lunchbreak/docker/' + folder + '/'
                )

    def setup(self, **kwargs):
        """Install all of the required software.

        Only works on Ubuntu 16.04 LTS.
        """

        with hide('output'):
            # Networking
            # Disable local search domain
            put(
                local_path='docker/config/dhcp/dhclient.conf',
                remote_path='/etc/dhcp/dhclient.conf',
                use_sudo=True
            )
            # Set custom nameservers
            put(
                local_path='docker/config/resolv.conf.d/base',
                remote_path='/etc/resolvconf/resolv.conf.d/base',
                use_sudo=True
            )
            # Apply DHCP changes
            sudo('service networking restart')
            # Regenerate resolvconfig
            sudo('resolvconf -u')

            # Certificate requirements
            sudo('apt-get install apt-transport-https ca-certificates -y')

            # Add Docker certificates and repository
            sudo('apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')
            sudo('echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" > /etc/apt/sources.list.d/docker.list')

            # Add PostgreSQL certificates and repository
            sudo('echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list')
            sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')

            sudo('apt-get update')
            sudo('apt-get -o Dpkg::Options::="--force-confnew" upgrade -y')
            sudo('apt-get purge lxc-docker')
            sudo('apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual -y')

            # Docker config
            sudo('mkdir -p /etc/docker/')
            put(
                local_path='docker/config/docker/daemon.json',
                remote_path='/etc/docker/daemon.json',
                use_sudo=True
            )
            sudo('apt-get -o Dpkg::Options::="--force-confnew" install docker-engine -y')

            # Disable docker service iptables before starting
            sudo('mkdir -p /etc/systemd/system/docker.service.d')
            put(
                local_path='docker/config/docker/disable-iptables.conf',
                remote_path='/etc/systemd/system/docker.service.d/disable-iptables.conf'
            )
            sudo('systemctl daemon-reload')
            sudo('service docker restart')
            sudo('systemctl enable docker')

            with settings(warn_only=True):
                sudo('docker network create -d bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 host_network')

            # Docker compose installation
            sudo('apt-get install python-pip -y')
            sudo('pip install --no-input docker-compose')

            # PostgreSQL installation
            sudo('sudo apt-get install postgresql-9.6')
            sudo('sudo systemctl enable postgresql')
            sudo('sudo systemctl start postgresql')

            # MySQL installation
            sudo('debconf-set-selections <<< "mysql-server-5.7 mysql-server/root_password password ditiseenzeerlangwachtwoorddatveranderdzalzijn"')
            sudo('debconf-set-selections <<< "mysql-server-5.7 mysql-server/root_password_again password ditiseenzeerlangwachtwoorddatveranderdzalzijn"')
            sudo('apt-get -y install mysql-server-5.7')
            sudo('sudo systemctl enable mysql')
            sudo('sudo systemctl start mysql')

            # Fail2Ban
            sudo('apt-get install fail2ban -y')

            self._setup_ufw()
            self._setup_fail2ban()

        sudo('mkdir /etc/lunchbreak/docker -p')
        self.upload_docker_folders(everything=True)
        self.update_compose_config(**kwargs)

        if not exists('/swap', use_sudo=True):
            sudo('fallocate -l 3G /swap')
            sudo('chmod 600 /swap')
            sudo('mkswap /swap')
            sudo('swapon /swap')
            sudo('echo \'/swapfile none swap sw 0 0\' | sudo tee -a /etc/fstab')
            sudo('sysctl vm.swappiness=10')
            sudo('echo "vm.swappiness=10" >> /etc/sysctl.conf')
            sudo('sysctl vm.vfs_cache_pressure=50')
            sudo('echo "vm.vfs_cache_pressure=50" >> /etc/sysctl.conf')

    def _image_name(self, tag):
        return '{username}/lunchbreak:{tag}'.format(
            username=self.username,
            tag=tag
        )

    def _setup_ufw(self):
        """Firewall settings."""
        # Allow UFW forwarding for docker
        put(
            local_path='docker/config/ufw/default_ufw',
            remote_path='/etc/default/ufw'
        )
        put(
            local_path='docker/config/ufw/after.rules',
            remote_path='/etc/ufw/after.rules'
        )
        put(
            local_path='docker/config/ufw/sysctl.conf',
            remote_path='/etc/ufw/sysctl.conf'
        )
        sudo('ufw default deny incoming')
        sudo('ufw default allow outgoing')
        sudo('ufw allow ssh')
        sudo('ufw allow http')
        sudo('ufw allow https')
        sudo('ufw --force enable')
        sudo('ufw --force reload')

    def _setup_fail2ban(self):
        put(
            local_path='docker/config/fail2ban/fail2ban.local',
            remote_path='/etc/fail2ban'
        )

        # Ensure Fail2ban is running
        with settings(warn_only=True):
            sudo('fail2ban-client start')
        sudo('fail2ban-client reload')

    def _docker_login(self, remote=True):
        self.username = self.username \
            if self.username is not None \
            else os.environ.get('DOCKER_USERNAME')
        if not self.username:
            self.username = input('Docker Hub username: ')
            os.environ['DOCKER_USERNAME'] = self.username

        self.password = self.password \
            if self.password is not None \
            else os.environ.get('DOCKER_PASSWORD')
        if not self.password:
            self.password = getpass.getpass('Docker Hub password: ')
            os.environ['DOCKER_PASSWORD'] = self.password

        with quiet():
            method = local if not remote else sudo
            method(
                'docker login -u="{username}" -p="{password}"'.format(
                    username=self.username,
                    password=self.password
                )
            )

    def _compose_up(self, configs=None, service=None):
        """Update docker compose containers.

        Will restart all container if no service is given.
        Else it will only restart that specific service.

        Args:
            configs (:obj:`string`): Configs that need to be used, will be uploaded if found.
            service (:obj:`string`, optional): Specific service that needs to be restarted.
        """
        self.upload_docker_folders()
        if configs is None:
            configs = [
                './docker/docker-compose.yml',
                './docker/docker-compose.production.yml'
            ]

        with cd('/etc/lunchbreak'):
            put(
                local_path='docker/*.*',
                remote_path='/etc/lunchbreak/docker'
            )

            self._docker_login()

            config_params = '-f ' + ' -f '.join(
                [
                    os.path.normpath(
                        os.path.join(
                            '/etc/lunchbreak/docker',
                            os.path.basename(config)
                        )
                    ) for config in configs
                ]
            )

            run(
                'docker-compose {config_params} pull'.format(
                    config_params=config_params
                )
            )

            if service is not None:
                run(
                    'docker-compose {config_params} up --build --no-deps -d {service}'.format(
                        service=service,
                        config_params=config_params
                    )
                )
            else:
                run(
                    'docker-compose {config_params} down'.format(
                        config_params=config_params
                    )
                )
                run(
                    'docker-compose {config_params} up --build -d'.format(
                        config_params=config_params
                    )
                )

        # Delete all dangling images
        with settings(warn_only=True), hide('warnings'):
            run('docker images -q -f dangling=true | xargs --no-run-if-empty docker rmi')

    def add_release(self):
        data = {
            'version': git_tag if git_tag else git_commit,
            'url': 'https://github.com/AndreasBackx/Lunchbreak-Backend/commit/' + git_commit,
            'refs': [
                {
                    'repository': 'Lunchbreak-Backend',
                    'commit': git_commit,
                    'previousCommit': git_previous_commit,
                }
            ],
            'projects': [
                'backend',
            ],
            'dateStarted': started_at.isoformat(),
        }
        response = requests.post(
            'https://sentry.io/api/hooks/release/builtin/130866/6470dd2af48c751aeeea53d5833c2dc5add47596e3bc76b5157e97ebba312f62/',
            json=data
        )
        if response.status_code == 201:
            print('Release committed successfully to Sentry.io!')
        else:
            print('Failed to commit release to Sentry.io!')
        print('Request:')
        print(
            json.dumps(
                data,
                indent=4
            )
        )
        print('Response:')
        print(
            json.dumps(
                response.json(), indent=4
            )
        )
