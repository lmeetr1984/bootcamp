#!/bin/sh

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
find . -path "*/log/*/*.log" -delete
find . -path "*/media/*/*.*" -delete
