.PHONY: debug build tidy release deploy clean tool lint help

.DEFAULT_GOAL=inspect
.ONESHELL:

name := version-checker
version := 1.0.0
date := $(shell date '+%Y-%m-%d %H:%M:%S')

tidy:
	poetry install

inspect: clean tidy
	poetry run version-checker inspect -i git
	poetry run version-checker inspect -i git-for-windows
	poetry run version-checker inspect -i clash_for_windows_pkg
	poetry run version-checker inspect -i clash
	poetry run version-checker inspect -i clash-premium
	poetry run version-checker inspect -i ClashForAndroid
	poetry run version-checker inspect -i Clash.Meta
	poetry run version-checker inspect -i compose
	poetry run version-checker inspect -i graalvm-ce-builds
	poetry run version-checker inspect -i stonedb
	poetry run version-checker inspect -i libmaxminddb
	poetry run version-checker inspect -i geoipupdate
	poetry run version-checker inspect -i zfs
	poetry run version-checker inspect -i upx
	poetry run version-checker inspect -i curl
	poetry run version-checker inspect -i libgd
	poetry run version-checker inspect -i openssl
	poetry run version-checker inspect -i corretto-8
	poetry run version-checker inspect -i corretto-11
	poetry run version-checker inspect -i corretto-17
	poetry run version-checker inspect -i corretto-21
	poetry run version-checker inspect -i python
	poetry run version-checker inspect -i php
	poetry run version-checker inspect -i go
	poetry run version-checker inspect -i redis
	poetry run version-checker inspect -i composer
	poetry run version-checker inspect -i httpd
	poetry run version-checker inspect -i kafka
	poetry run version-checker inspect -i doris
	poetry run version-checker inspect -i maven
	poetry run version-checker inspect -i hbase
	poetry run version-checker inspect -i groovy
	poetry run version-checker inspect -i dolphinscheduler
	poetry run version-checker inspect -i echarts
	poetry run version-checker inspect -i dubbo
	poetry run version-checker inspect -i spark
	poetry run version-checker inspect -i airflow
	poetry run version-checker inspect -i rocketmq
	poetry run version-checker inspect -i druid
	poetry run version-checker inspect -i zookeeper
	poetry run version-checker inspect -i nginx
	poetry run version-checker inspect -i njs
	poetry run version-checker inspect -i ansible
	poetry run version-checker inspect -i coredns
	poetry run version-checker inspect -i etcd
	poetry run version-checker inspect -i consul
	poetry run version-checker inspect -i vagrant
	poetry run version-checker inspect -i vault
	poetry run version-checker inspect -i gpdb
	poetry run version-checker inspect -i netdata
	poetry run version-checker inspect -i elasticsearch
	poetry run version-checker inspect -i logstash
	poetry run version-checker inspect -i kibana
	poetry run version-checker inspect -i beats
	poetry run version-checker inspect -i opensearch
	poetry run version-checker inspect -i kubernetes
	poetry run version-checker inspect -i rke2
	poetry run version-checker inspect -i gradle
	poetry run version-checker inspect -i memcached
	poetry run version-checker inspect -i ant-design
	poetry run version-checker inspect -i ant-design-vue
	poetry run version-checker inspect -i haproxy
	poetry run version-checker inspect -i mongo
	poetry run version-checker inspect -i rabbitmq
	poetry run version-checker inspect -i mysql
	poetry run version-checker inspect -i postgres
	poetry run version-checker inspect -i centos
	poetry run version-checker inspect -i almalinux
	poetry run version-checker inspect -i rockylinux
	poetry run version-checker inspect -i debian
	poetry run version-checker inspect -i ubuntu
	poetry run version-checker inspect -i gitlab-ce
	poetry run version-checker inspect -i gitlab-runner
	poetry run version-checker inspect -i percona-server
	poetry run version-checker inspect -i flume
	poetry run version-checker inspect -i nexus
	poetry run version-checker inspect -i nodejs
	poetry run version-checker inspect -i ruby
	poetry run version-checker inspect -i virtualbox
	poetry run version-checker inspect -i tortoisesvn
	poetry run version-checker inspect -i tortoisegit
	poetry run version-checker inspect -i github-desktop

lint:

clean:
	@rm -rf dist/*

help:
	@echo "make: compile packages and dependencies"
	@echo "make tool: run specified python tool"
	@echo "make lint: pylint ./..."
	@echo "make clean: remove object files and cached files"
	@echo "make release: release binary."
