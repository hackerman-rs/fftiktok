#!/bin/bash
# run.sh port

hypercorn app:app -b "0.0.0.0:$@"
