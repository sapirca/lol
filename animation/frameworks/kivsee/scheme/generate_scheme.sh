#!/bin/bash

cd /Users/sapir/repos/lol/animation/frameworks/kivsee/scheme
protoc --protobuf-to-pydantic_out=. effects.proto