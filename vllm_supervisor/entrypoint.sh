#!/bin/bash
# Take everything passed to 'docker run' and put it in an env var
export EXTRA_ARGS="$@"

# Start supervisor
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf 
