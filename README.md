# ZTE DSL Modem Prometheus Exporter

This is a prometheus exporter for the ZTE H186 VDSL2 Bonding Bridge Super Vectoring Modem.
It is highly experimental.

The modem has the worst webinterface known to humanity. It requires multiple requests before allowing you to fetch a specific piece of XML which is not proper XML. Please don't ever look at it, it will cause you nightmares.

Put the URL of your modem and the read-only credentials in the file and run it. It's listening on `0.0.0.0:9157`.
Have fun.
