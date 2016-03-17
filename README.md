# Filebeat

A lightweight, open source shipper for log file data. As the
next-generation Logstash Forwarder, Filebeat tails logs and quickly sends this
information to Logstash for further parsing and enrichment or to Elasticsearch
for centralized storage and analysis.

## Usage

Filebeat can be added to any principal charm thanks to the wonders of being
a subordinate charm. The following usage example will deploy the elk stack,
so we can visualize our log data once we've established the link between
Filebeat and Logstash

    juju deploy ~containers/bundle/elk-stack
    juju deploy ubuntu
    juju deploy ~containers/trusty/filebeat
    juju add-relation filebeat:beats-host ubuntu
    juju add-relation filebeat logstash


### Changing whats being shipped

by default, the filebeat charm is setup to ship everything in:

    /var/log/*/*.log
    /var/log/*.log
<!-- /* -->

If you'd rather target specific log files:

    juju set-config filebeat logpath /var/log/mylog.log


## Testing the deployment

The services provide extended status reporting to indicate when they are ready:

    juju status --format=tabular

This is particularly useful when combined with watch to track the on-going
progress of the deployment:

    watch -n 0.5 juju status --format=tabular

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can navigate to the kibana
url and view the streamed log data from the Ubuntu host.

    juju status kibana --format=yaml | grep public-address

  open http://&lt;kibana-ip&gt;/ in a browser and begin creating your dashboard
  visualizations

## Scale Out Usage

This bundle was designed to scale out. To increase the amount of log storage and
indexers, you can add-units to elasticsearch.

    juju add-unit elasticsearch

You can also increase in multiples, for example: To increase the number of
logstash parser/buffer/shipping services:

    juju add-unit -n 2 logstash

To monitor additional hosts, simply relate the filebeat subordinate

    juju add-relation filebeat:beats-host my-charm


## Contact information

- Charles Butler &lt;charles.butler@canonical.com&gt;
- Matt Bruzek &lt;matthew.bruzek@canonical.com&gt;

# Need Help?

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju Community](https://jujucharms.com/community)
