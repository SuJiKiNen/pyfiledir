#!/usr/bin/env bash
git config core.symlinks true
find .. -type l -delete
git reset --hard
