from charms.reactive import when
from charms.reactive import when_file_changed
from charms.reactive import when_not
from charms.reactive import set_state
from charms.reactive import remove_state

from charms.templating.jinja2 import render

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.hookenv import config
from charmhelpers.core.host import service_restart
from charmhelpers.core.unitdata import kv

from charmhelpers.fetch import configure_sources
from charmhelpers.fetch import apt_install

from subprocess import check_call


@when_not('filebeat.installed')
def install_filebeat():
    status_set('maintenance', 'Installing filebeat')
    configure_sources(update=True)
    apt_install(['filebeat'], fatal=True)
    set_state('filebeat.installed')


@when('filebeat.installed')
@when_not('logstash.connected', 'elasticsearch.connected')
def blocked_messaging():
    status_set('blocked', 'Waiting on relationship: elasticsearch or logstash')


@when('logstash.available')
def enable_logstash_shipping(logstash):
    units = logstash.list_unit_data()
    cache = kv()
    if cache.get('filebeat.logstash'):
        hosts = cache.get('filebeat.logstash')
    else:
        hosts = []
    for logstash in units:
        host_string = "{0}:{1}".format(logstash['private_address'],
                                       logstash['port'])
        if host_string not in hosts:
            hosts.append(host_string)

    cache.set('filebeat.logstash', hosts)
    set_state('filebeat.render')


@when('filebeat.render')
def render_filebeat_template():
    ''' Render filebeat template from global state context '''
    status_set('maintenance', 'Configuring filebeat')
    cache = kv()
    context = config()

    logstash_hosts = cache.get('filebeat.logstash')
    elasticsearch_hosts = cache.get('filebeat.elasticsearch')

    if logstash_hosts:
        context.update({'logstash': logstash_hosts})
    if elasticsearch_hosts:
        context.update({'elasticsearch': elasticsearch_hosts})
    # Split the log paths
    if context['logpath']:
        context['logpath'] = context['logpath'].split(' ')

    template = 'filebeat.yml'
    target = '/etc/filebeat/filebeat.yml'
    render(template, target, context)
    remove_state('filebeat.render')
    status_set('active', 'filebeat ready')
    enable_filebeat_on_boot


@when('config.changed')
def config_changed():
    ''' trigger a template re-render on configuration option updates'''
    set_state('filebeat.render')


@when('config.changed.install_sources')
@when('config.changed.install_keys')
def reinstall_filebeat():
    remove_state('filebeat.installed')


@when_file_changed('/etc/filebeat/filebeat.yml')
def restart_filebeat():
    ''' Anytime we touch the config file, cycle the service'''
    service_restart('filebeat')


def enable_filebeat_on_boot():
    """ Enable the beat to start automaticaly during boot """
    check_call(['update-rc.d', 'filebeat', 'defaults', '95', '10'])
