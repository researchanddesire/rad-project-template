#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
test_binary=$(mktemp /tmp/buttplug-r0-test.XXXXXX)
trap 'rm -f "$test_binary"' EXIT
cc -std=c11 -Wall -Wextra -Werror -fsanitize=undefined -I main tests/test_control.c main/proto_control.c -o "$test_binary"
"$test_binary"
