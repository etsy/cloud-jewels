#!/bin/bash
#
# This script scans all resource usage over a trailing thirty day period and
# estimates consumption by using a hard-coded coefficient lookup table.

USAGE_SQL='sql/usage_by_jewel_class.sql'

function print_help() {
  echo "
  Usage:    $ cloud-jewels.sh -p <google project id>
  Example:  $ cloud-jewels.sh -p my-billing-project
  "
}

function get_usage() {
  local project_id=$1
  local usage_sql=$2

  echo "Estimating resource consumption using project '${project_id}'..."
  bq query --project_id ${project_id} --nouse_legacy_sql "$(cat ${usage_sql})"
}

while getopts "p:h" opt; do
  case $opt in
    p) PROJECT_ID="${OPTARG}";;
    h) print_help 
       exit 1;;
  esac
done

get_usage ${PROJECT_ID} ${USAGE_SQL}
