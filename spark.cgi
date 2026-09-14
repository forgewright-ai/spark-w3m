#!/bin/sh
# the local CGI door: w3m's cgi_bin points at this clone, and this one
# line hands the request to the wrapper's --page mode.
exec "$(dirname "$0")/spark-w3m" --page
