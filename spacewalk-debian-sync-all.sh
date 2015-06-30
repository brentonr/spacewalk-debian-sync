#!/bin/bash

. /etc/sysconfig/spacewalk-debian-sync

for channel in `ls "${SPACEWALK_CONF_DIR}/"`; do
	url=$(cat "${SPACEWALK_CONF_DIR}/${channel}")
	/usr/local/bin/spacewalk-debian-sync.pl --username "${USERNAME}" --password "${PASSWORD}" --channel "${channel}" --url "${url}" 2>&1 >> "/var/log/rhn/reposync/${channel}.log"
	/usr/local/bin/spacewalk-debian-sync-fixup.pl --channel "${channel}" --url "${url}" 2>&1 >> "/var/log/rhn/reposync/fixup-${channel}.log"
done
