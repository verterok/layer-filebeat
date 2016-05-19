from charms.reactive import when
from charms.reactive import when_not
from charms.reactive import when_any
from charms.reactive import set_state
from charms.reactive import remove_state
from charms.reactive import is_state


from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import service_restart
from charmhelpers.fetch import apt_install

from elasticbeats import render_without_context
from elasticbeats import enable_beat_on_boot
from elasticbeats import push_beat_index


@when('beats.repo.available')
@when_not('filebeat.installed')
def install_filebeat():
    status_set('maintenance', 'Installing filebeat')
    apt_install(['filebeat'], fatal=True)
    set_state('filebeat.installed')


@when('beat.render')
@when_any('elasticsearch.available', 'logstash.available')
def render_filebeat_template():
    render_without_context('filebeat.yml', '/etc/filebeat/filebeat.yml')
    remove_state('beat.render')
    service_restart('filebeat')
    status_set('active', 'Filebeat ready')


@when('config.changed.install_sources')
@when('config.changed.install_keys')
def reinstall_filebeat():
        remove_state('filebeat.installed')


@when('filebeat.installed')
@when_not('filebeat.autostarted')
def enlist_packetbeat():
    enable_beat_on_boot('filebeat')
    set_state('filebeat.autostarted')


@when('filebeat.installed')
@when('elasticsearch.available')
@when_not('filebeat.index.pushed')
def push_filebeat_index(elasticsearch):
    hosts = elasticsearch.list_unit_data()
    for host in hosts:
        host_string = "{}:{}".format(host['host'], host['port'])
    push_beat_index(host_string, 'filebeat')
    set_state('filebeat.index.pushed')
