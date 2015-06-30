spacewalk-debian-sync
=====================

An improvised repo-sync to bring Debian packages into Spacewalk

### spacewalk-debian-sync-all.sh

A script that takes URLs and channel names from /etc/sysconfig/ and calls `spacewalk-debian-sync.pl` with the appropriate arguments.

Suiteable for calling from cron and other periodic executors.

Username is and password are specified in `/etc/sysconfig/spacewalk-debian-sync` whereas channels and URLs are set in the `/etc/spacewalk-debian-sync.d/` directory.

In this directory, the filename is the channel name, and the contents of the file contains the base URL of the remote channel to sync from.

For example, `/etc/sysconfig/spacewalk-debian-sync` can contain:

```
USERNAME=MySyncUser
PASSWORD=MySyncPassword
```

and `/etc/spacewalk-debian-sync.d/` can contain `trusty-amd64`, with contents:

```
http://mirrors.cat.pdx.edu/ubuntu/dists/trusty/main/binary-amd64/
```

### spacewalk-debian-sync-fixup.py

A script that post-processes the Spacewalk-generated `Packages` and `Package.gz` files to add missing attributes not supported by Spacewalk.

Currently, only the `Multi-Arch: allowed` attribute is added to Spacewalk's `Packages[.gz]` files to fix support for Python packaging.
