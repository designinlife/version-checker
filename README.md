# Software latest version detector

![GitHub CI](https://github.com/designinlife/version-checker/actions/workflows/ci.yml/badge.svg)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdesigninlife%2Fversion-checker%2Fmain%2Fpyproject.toml)
![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)

**:boom:Note: Updated every 6 hours!**

> The latest JSON data file is automatically generated by GitHub Action every 6 hours.

## Usage

```bash
curl -sSL --fail https://raw.githubusercontent.com/designinlife/version-checker/main/data/all.json | jq
```

## Supported software list

<!-- prettier-ignore -->
| Name | Summary | Link |
| :-- | :-- | :-- |
| Git | Git 命令行工具 | [git](https://raw.githubusercontent.com/designinlife/version-checker/main/data/git.json) |
| Git for Windows | Git for Windows 版本 | [git-for-windows](https://raw.githubusercontent.com/designinlife/version-checker/main/data/git-for-windows.json) |
| Clash for Windows | Clash Windows 版本 | [clash_for_windows_pkg](https://raw.githubusercontent.com/designinlife/version-checker/main/data/clash_for_windows_pkg.json) |
| Clash | Clash Linux 版本 | [clash](https://raw.githubusercontent.com/designinlife/version-checker/main/data/clash.json) |
| Clash Premium | Clash Linux 闭源版(支持 Rule Provider 等高级特性) | [clash-premium](https://raw.githubusercontent.com/designinlife/version-checker/main/data/clash-premium.json) |
| Clash for Android | Clash 手机版 | [ClashForAndroid](https://raw.githubusercontent.com/designinlife/version-checker/main/data/ClashForAndroid.json) |
| Clash.Meta | Clash 另一个发行版 | [Clash.Meta](https://raw.githubusercontent.com/designinlife/version-checker/main/data/Clash.Meta.json) |
| Swoole | PHP 高性能协程开发扩展库 | [swoole](https://raw.githubusercontent.com/designinlife/version-checker/main/data/swoole.json) |
| gRPC | Google 出品的 RPC 框架 | [grpc](https://raw.githubusercontent.com/designinlife/version-checker/main/data/grpc.json) |
| Protobuf | Google Protobuf 序列化框架 | [protobuf](https://raw.githubusercontent.com/designinlife/version-checker/main/data/protobuf.json) |
| Harbor | Docker 私有仓库服务器 | [harbor](https://raw.githubusercontent.com/designinlife/version-checker/main/data/harbor.json) |
| Docker Compose | Docker 容器命令行管理工具 | [compose](https://raw.githubusercontent.com/designinlife/version-checker/main/data/docker-compose.json) |
| GraalVM CE | GraalVM 社区版 | [graalvm-ce-builds](https://raw.githubusercontent.com/designinlife/version-checker/main/data/graalvm-ce-builds.json) |
| StoneDB | 一个分布式 OLAP 数据库 | [stonedb](https://raw.githubusercontent.com/designinlife/version-checker/main/data/stonedb.json) |
| Solon | 国产 Java 生态框架 | [solon](https://raw.githubusercontent.com/designinlife/version-checker/main/data/solon.json) |
| Libmaxminddb | C library for the MaxMind DB file format | [libmaxminddb](https://raw.githubusercontent.com/designinlife/version-checker/main/data/libmaxminddb.json) |
| GeoIP Update | GeoIP 数据库更新工具 | [geoipupdate](https://raw.githubusercontent.com/designinlife/version-checker/main/data/geoipupdate.json) |
| OpenZFS | ZFS 分布式存储 | [zfs](https://raw.githubusercontent.com/designinlife/version-checker/main/data/zfs.json) |
| UPX | 二进制程序压缩工具 | [upx](https://raw.githubusercontent.com/designinlife/version-checker/main/data/upx.json) |
| cURL | 最流行的 HTTP 命令行客户端工具 | [curl](https://raw.githubusercontent.com/designinlife/version-checker/main/data/curl.json) |
| LibGD | GD 库 | [libgd](https://raw.githubusercontent.com/designinlife/version-checker/main/data/libgd.json) |
| OpenSSL | OpenSSL 加密库 | [1.1](https://raw.githubusercontent.com/designinlife/version-checker/main/data/openssl-1.1.json) / [3.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/openssl-3.0.json) / [3.1](https://raw.githubusercontent.com/designinlife/version-checker/main/data/openssl-3.1.json) / [3.2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/openssl-3.2.json) |
| Amazon Corretto 1.8 | Amazon Corretto JDK 1.8 | [corretto-8](https://raw.githubusercontent.com/designinlife/version-checker/main/data/corretto-8.json) |
| Amazon Corretto 11 | Amazon Corretto JDK 11 | [corretto-11](https://raw.githubusercontent.com/designinlife/version-checker/main/data/corretto-11.json) |
| Amazon Corretto 17 | Amazon Corretto JDK 17 | [corretto-17](https://raw.githubusercontent.com/designinlife/version-checker/main/data/corretto-17.json) |
| Amazon Corretto 21 | Amazon Corretto JDK 21 | [corretto-21](https://raw.githubusercontent.com/designinlife/version-checker/main/data/corretto-21.json) |
| Python | Python 编程语言 | [3.8](https://raw.githubusercontent.com/designinlife/version-checker/main/data/python-3.8.json) / [3.9](https://raw.githubusercontent.com/designinlife/version-checker/main/data/python-3.9.json) / [3.10](https://raw.githubusercontent.com/designinlife/version-checker/main/data/python-3.10.json) / [3.11](https://raw.githubusercontent.com/designinlife/version-checker/main/data/python-3.11.json) / [3.12](https://raw.githubusercontent.com/designinlife/version-checker/main/data/python-3.12.json) |
| PHP | PHP 脚本编程语言 | [7.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-7.0.json) / [7.1](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-7.1.json) / [7.2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-7.2.json) / [7.3](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-7.3.json) / [7.4](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-7.4.json) / [8.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-8.0.json) / [8.1](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-8.1.json) / [8.2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-8.2.json) / [8.3](https://raw.githubusercontent.com/designinlife/version-checker/main/data/php-8.3.json) |
| Golang | Go 语言 | [1.16](https://raw.githubusercontent.com/designinlife/version-checker/main/data/go-1.16.json) / [1.18](https://raw.githubusercontent.com/designinlife/version-checker/main/data/go-1.18.json) / [1.19](https://raw.githubusercontent.com/designinlife/version-checker/main/data/go-1.19.json) / [1.20](https://raw.githubusercontent.com/designinlife/version-checker/main/data/go-1.20.json) / [1.21](https://raw.githubusercontent.com/designinlife/version-checker/main/data/go-1.21.json) / [1.22](https://raw.githubusercontent.com/designinlife/version-checker/main/data/go-1.22.json) |
| Redis | 最流行的 KV 内存数据库 | [5.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/redis-5.0.json) / [6.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/redis-6.0.json) / [6.2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/redis-6.2.json) / [7.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/redis-7.0.json) / [7.2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/redis-7.2.json) |
| PHP Composer | PHP 包管理工具 | [1.10](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-1.10.json) / [2.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-2.0.json) / [2.1](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-2.1.json) / [2.2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-2.2.json) / [2.3](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-2.3.json) / [2.4](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-2.4.json) / [2.5](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-2.5.json) / [2.6](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-2.6.json) / [2.7](https://raw.githubusercontent.com/designinlife/version-checker/main/data/composer-2.7.json) |
| Apache HTTP Server | Apache HTTP 服务器 | [httpd](https://raw.githubusercontent.com/designinlife/version-checker/main/data/httpd.json) |
| Kafka | Apache Kafka 流式消息服务器 | [kafka](https://raw.githubusercontent.com/designinlife/version-checker/main/data/kafka.json) |
| Apache Doris | 一个基于 MPP 架构的高性能、实时的分析型数据库 | [1.1](https://raw.githubusercontent.com/designinlife/version-checker/main/data/doris-1.1.json) / [1.2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/doris-1.2.json) / [2.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/doris-2.0.json) |
| Maven | Java 依赖包管理工具 | [maven](https://raw.githubusercontent.com/designinlife/version-checker/main/data/maven.json) |
| HBase | 开源的非关系型分布式数据库 | [hbase](https://raw.githubusercontent.com/designinlife/version-checker/main/data/hbase.json) |
| Groovy | 用于 Java 虚拟机的一种敏捷的动态语言 | [2.4](https://raw.githubusercontent.com/designinlife/version-checker/main/data/groovy-2.4.json) / [2.5](https://raw.githubusercontent.com/designinlife/version-checker/main/data/groovy-2.5.json) / [3.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/groovy-3.0.json) / [4.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/groovy-4.0.json) |
| Apache DolphinScheduler | 一个分布式、去中心化、易扩展的可视化 DAG 工作流任务调度系统 | [dolphinscheduler](https://raw.githubusercontent.com/designinlife/version-checker/main/data/dolphinscheduler.json) |
| ECharts | 一款基于 JavaScript 的数据可视化图表库 | [echarts](https://raw.githubusercontent.com/designinlife/version-checker/main/data/echarts.json) |
| Apache Dubbo | 阿里巴巴公司开源的一个高性能优秀的服务框架 | [dubbo](https://raw.githubusercontent.com/designinlife/version-checker/main/data/dubbo.json) |
| Apache Spark | 用于分布式数据处理和并行计算的开源项目 | [spark](https://raw.githubusercontent.com/designinlife/version-checker/main/data/spark.json) |
| Apache Airflow | 一个以编程方式创作、调度和监控工作流程的平台 | [airflow](https://raw.githubusercontent.com/designinlife/version-checker/main/data/airflow.json) |
| Apache RocketMQ | 由阿里捐赠给 Apache 的一款低延迟、高并发、高可用、高可靠的分布式消息中间件 | [rocketmq](https://raw.githubusercontent.com/designinlife/version-checker/main/data/rocketmq.json) |
| Apache Druid | 一个实时分析型数据库，旨在对大型数据集进行快速查询和分析 OLAP | [druid](https://raw.githubusercontent.com/designinlife/version-checker/main/data/druid.json) |
| ZooKeeper | 一个分布式的，开放源码的分布式应用程序协调服务 | [zookeeper](https://raw.githubusercontent.com/designinlife/version-checker/main/data/zookeeper.json) |
| Nginx | 一个高性能的 HTTP 和反向代理服务器，特点是占有内存少，并发能力强 | [nginx](https://raw.githubusercontent.com/designinlife/version-checker/main/data/nginx.json) |
| NJS | 为了 NGINX 和 NGINX Plus 而开发的 JavaScript 实现 | [njs](https://raw.githubusercontent.com/designinlife/version-checker/main/data/njs.json) |
| Ansible | 新出现的自动化运维工具，基于 Python 开发，集合了众多运维工具的优点 | [ansible](https://raw.githubusercontent.com/designinlife/version-checker/main/data/ansible.json) |
| CoreDNS | 一个灵活可扩展的 DNS 服务器，可以作为 Kubernetes 集群 DNS | [coredns](https://raw.githubusercontent.com/designinlife/version-checker/main/data/coredns.json) |
| Etcd | 开源的分布式统一键值存储，用于分布式系统或计算机集群的共享配置、服务发现和的调度协调 | [etcd](https://raw.githubusercontent.com/designinlife/version-checker/main/data/etcd.json) |
| Consul | 一个服务网格解决方案，提供了一个功能齐全的控制平面，具有服务发现、配置和分段功能 | [consul](https://raw.githubusercontent.com/designinlife/version-checker/main/data/consul.json) |
| Vagrant | 一个构件虚拟开发环境的工具 | [vagrant](https://raw.githubusercontent.com/designinlife/version-checker/main/data/vagrant.json) |
| HashiCorp Vault | 用来安全的存储秘密信息的工具 | [vault](https://raw.githubusercontent.com/designinlife/version-checker/main/data/vault.json) |
| VMware Greenplum | 用于大规模分析和数据仓库的大规模并行处理(MPP) 数据平台 | [gpdb](https://raw.githubusercontent.com/designinlife/version-checker/main/data/gpdb.json) |
| Netdata | 一个高效，高度模块化的指标管理引擎 | [netdata](https://raw.githubusercontent.com/designinlife/version-checker/main/data/netdata.json) |
| Elasticsearch (ES) | 一个开源的、高扩展的、分布式的、提供多用户能力的全文搜索引擎 | [elasticsearch](https://raw.githubusercontent.com/designinlife/version-checker/main/data/elasticsearch.json) |
| Logstash | 免费且开放的服务器端数据处理管道，能够从多个来源采集数据，转换数据 | [logstash](https://raw.githubusercontent.com/designinlife/version-checker/main/data/logstash.json) |
| Kibana | 针对大规模数据快速运行数据分析，以实现可观测性、安全和搜索 | [kibana](https://raw.githubusercontent.com/designinlife/version-checker/main/data/kibana.json) |
| Elastic Beats | 一个免费且开放的平台，集合了多种单一用途数据采集器 | [beats](https://raw.githubusercontent.com/designinlife/version-checker/main/data/beats.json) |
| OpenSearch | 分布式，由社区驱动并取得 Apache 2.0 许可的 100% 开源搜索和分析套件 | [opensearch](https://raw.githubusercontent.com/designinlife/version-checker/main/data/opensearch.json) |
| Kubernetes (k8s) | 用于自动部署、扩缩和管理容器化应用程序的开源系统 | [kubernetes](https://raw.githubusercontent.com/designinlife/version-checker/main/data/kubernetes.json) |
| RKE2 | RKE Government，是 Rancher 的下一代 Kubernetes 发行版 | [rke2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/rke2.json) |
| Gradle | 一个基于 Apache Ant 和 Apache Maven 概念的项目自动化构建开源工具 | [gradle](https://raw.githubusercontent.com/designinlife/version-checker/main/data/gradle.json) |
| Memcached | 一款开源、高性能、分布式内存对象缓存系统 | [memcached](https://raw.githubusercontent.com/designinlife/version-checker/main/data/memcached.json) |
| Ant Design | 一个致力于提升『用户』和『设计者』使用体验的中台设计语言 | [ant-design](https://raw.githubusercontent.com/designinlife/version-checker/main/data/ant-design.json) |
| Ant Design Vue | Ant Design Vue 版本 | [ant-design-vue](https://raw.githubusercontent.com/designinlife/version-checker/main/data/ant-design-vue.json) |
| HAProxy | 使用 C 语言编写的高可用性、负载均衡，以及基于 TCP 和 HTTP 的应用程序代理 | [haproxy](https://raw.githubusercontent.com/designinlife/version-checker/main/data/haproxy.json) |
| MongoDB | 由 C++语言编写的，是一个基于分布式文件存储的开源数据库系统 | [mongo](https://raw.githubusercontent.com/designinlife/version-checker/main/data/mongo.json) |
| RabbitMQ | 一个开源的 AMQP 实现，服务器端用 Erlang 语言编写 | [rabbitmq](https://raw.githubusercontent.com/designinlife/version-checker/main/data/rabbitmq.json) |
| MySQL | 互联网上最流行的开源关系数据库 | [mysql](https://raw.githubusercontent.com/designinlife/version-checker/main/data/mysql.json) |
| PostgreSQL | 一款高级的企业级开源关系数据库 | [11](https://raw.githubusercontent.com/designinlife/version-checker/main/data/postgres-11.json) / [12](https://raw.githubusercontent.com/designinlife/version-checker/main/data/postgres-12.json) / [13](https://raw.githubusercontent.com/designinlife/version-checker/main/data/postgres-13.json) / [14](https://raw.githubusercontent.com/designinlife/version-checker/main/data/postgres-14.json) / [15](https://raw.githubusercontent.com/designinlife/version-checker/main/data/postgres-15.json) / [16](https://raw.githubusercontent.com/designinlife/version-checker/main/data/postgres-16.json) |
| CentOS | CentOS 7 操作系统 | [7.x](https://raw.githubusercontent.com/designinlife/version-checker/main/data/centos-7.json) / [8.x](https://raw.githubusercontent.com/designinlife/version-checker/main/data/centos-8.json) |
| AlmaLinux | CentOS 8/9 的替代发行版 | [8.x](https://raw.githubusercontent.com/designinlife/version-checker/main/data/almalinux-8.json) / [9.x](https://raw.githubusercontent.com/designinlife/version-checker/main/data/almalinux-9.json) |
| RockyLinux | CentOS 8/9 的替代发行版 | [8.x](https://raw.githubusercontent.com/designinlife/version-checker/main/data/rockylinux-8.json) / [9.x](https://raw.githubusercontent.com/designinlife/version-checker/main/data/rockylinux-9.json) |
| Debian | Debian 开源操作系统 | [debian](https://raw.githubusercontent.com/designinlife/version-checker/main/data/debian.json) |
| Ubuntu | Ubuntu 操作系统 | [ubuntu](https://raw.githubusercontent.com/designinlife/version-checker/main/data/ubuntu.json) |
| GitLab Community Edition | Gitlab 社区版 | [gitlab-ce](https://raw.githubusercontent.com/designinlife/version-checker/main/data/gitlab-ce.json) |
| Gitlab Runner | GitLab CI 是 GitLab 随附的开源持续集成服务 | [gitlab-runner](https://raw.githubusercontent.com/designinlife/version-checker/main/data/gitlab-runner.json) |
| Percona Server for MySQL | Percona 公司的增强 MySQL 发行版 | [5.6](https://raw.githubusercontent.com/designinlife/version-checker/main/data/percona-server-5.6.json) / [5.7](https://raw.githubusercontent.com/designinlife/version-checker/main/data/percona-server-5.7.json) / [8.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/percona-server-8.0.json) |
| Apache Flume | 一个分布式，高可用的数据收集系统 | [flume](https://raw.githubusercontent.com/designinlife/version-checker/main/data/flume.json) |
| Sonatype Nexus | 自建私有仓库的服务器系统。支持常见的 yum,apt,pypi 等仓库格式 | [nexus](https://raw.githubusercontent.com/designinlife/version-checker/main/data/nexus.json) |
| NodeJS | NodeJS 编程语言 | [nodejs](https://raw.githubusercontent.com/designinlife/version-checker/main/data/nodejs.json) |
| Ruby | Ruby 编程语言 | [ruby](https://raw.githubusercontent.com/designinlife/version-checker/main/data/ruby.json) |
| VirtualBox | 开源的虚拟机管理工具 | [virtualbox](https://raw.githubusercontent.com/designinlife/version-checker/main/data/virtualbox.json) |
| TortoiseSVN | 流行的 SVN 管理客户端 GUI 工具 | [tortoisesvn](https://raw.githubusercontent.com/designinlife/version-checker/main/data/tortoisesvn.json) |
| TortoiseGit | 一个开源的 Git 管理 GUI 工具 | [tortoisegit](https://raw.githubusercontent.com/designinlife/version-checker/main/data/tortoisegit.json) |
| GitHub Desktop | Github 出品的桌面端 Git 版本管理工具 | [github-desktop](https://raw.githubusercontent.com/designinlife/version-checker/main/data/github-desktop.json) |
| JetBrains AppCode | 适用于 iOS/macOS 开发的智能 IDE | [JetBrains.AppCode](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.AppCode.json) |
| JetBrains CLion | JetBrains 公司旗下新推出的一款专门为开发 C/C++所设计的跨平台的 IDE | [JetBrains.CLion](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.CLion.json) |
| JetBrains ReSharperUltimate | 为 .NET 开发者专门打造的插件工具 | [JetBrains.ReSharperUltimate](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.ReSharperUltimate.json) |
| JetBrains DataGrip | 有助于您更快速地编写 SQL 代码 | [JetBrains.DataGrip](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.DataGrip.json) |
| JetBrains Goland | Go 语言集成开发工具 IDE | [JetBrains.Goland](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.Goland.json) |
| JetBrains IntelliJIDEA | Java 集成开发工具 IDE | [JetBrains.IntelliJIDEA](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.IntelliJIDEA.json) |
| JetBrains PhpStorm | PHP 集成开发工具 IDE | [JetBrains.PhpStorm](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.PhpStorm.json) |
| JetBrains PyCharm | Python 集成开发工具 IDE | [JetBrains.PyCharm](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.PyCharm.json) |
| JetBrains Rider | JetBrains 出品的 .NET 集成开发工具 IDE | [JetBrains.Rider](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.Rider.json) |
| JetBrains RubyMine | Ruby 集成开发工具 IDE | [JetBrains.RubyMine](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.RubyMine.json) |
| JetBrains WebStorm | JavaScript/Vue/React 集成开发工具 IDE | [JetBrains.WebStorm](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.WebStorm.json) |
| JetBrains Fleet | JetBrains 轻量级开发工具，可替代 VSCode | [JetBrains.Fleet](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.Fleet.json) |
| JetBrains RustRover | Rust 集成开发工具 IDE | [JetBrains.RustRover](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.RustRover.json) |
| JetBrains DataSpell | 适用于数据分析的 IDE | [JetBrains.DataSpell](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.DataSpell.json) |
| JetBrains Aqua | 一款可以感知上下文的智能 IDE | [JetBrains.Aqua](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.Aqua.json) |
| JetBrains TeamCity | JetBrains 开发的持续集成服务器 | [JetBrains.TeamCity](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.TeamCity.json) |
| JetBrains Writerside | JetBrains 的全新技术写作环境 | [JetBrains.Writerside](https://raw.githubusercontent.com/designinlife/version-checker/main/data/JetBrains.Writerside.json) |
| Dart | Dart 编程语言 | [dart](https://raw.githubusercontent.com/designinlife/version-checker/main/data/dart.json) |
| Flutter | 一个跨平台的 UI 工具集 | [flutter](https://raw.githubusercontent.com/designinlife/version-checker/main/data/flutter.json) |
| Android Studio | 用于开发 Android 应用的官方集成开发环境(IDE) | [android-studio](https://raw.githubusercontent.com/designinlife/version-checker/main/data/android-studio.json) |
| VSCode | 一款由微软开发且跨平台的免费源代码编辑器 | [vscode](https://raw.githubusercontent.com/designinlife/version-checker/main/data/vscode.json) |
| DotNet | 微软公司发布的免费的跨平台开源开发人员平台 | [6.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/dotnet-6.0.json) / [7.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/dotnet-7.0.json) / [8.0](https://raw.githubusercontent.com/designinlife/version-checker/main/data/dotnet-8.0.json) |
| Google Chrome | Google 浏览器 | [chrome](https://raw.githubusercontent.com/designinlife/version-checker/main/data/chrome.json) |
| Firefox | Firefox 浏览器 | [firefox](https://raw.githubusercontent.com/designinlife/version-checker/main/data/firefox.json) |
| AWS CLI v2 | AWS 命令行工具 | [awscli](https://raw.githubusercontent.com/designinlife/version-checker/main/data/awscli.json) |
| React | Facebook 内部开源出来的一个前端 UI 开发框架 | [react](https://raw.githubusercontent.com/designinlife/version-checker/main/data/react.json) |
| Vue.js | 一款用于构建用户界面的 JavaScript 框架 | [vue](https://raw.githubusercontent.com/designinlife/version-checker/main/data/vue.json) |
| Jenkins LTS | 基于 Java 开发的持续集成工具 | [jenkins](https://raw.githubusercontent.com/designinlife/version-checker/main/data/jenkins.json) |
| Bytebase | 一款开源的数据库 CI/CD 工具 | [bytebase](https://raw.githubusercontent.com/designinlife/version-checker/main/data/bytebase.json) |
| Caddy | 一个强大的、可扩展的平台, 用于伺服你的站点、服务以及应用 | [caddy](https://raw.githubusercontent.com/designinlife/version-checker/main/data/caddy.json) |
| Visual Studio | 微软旗下的集成开发环境（IDE） | [vs](https://raw.githubusercontent.com/designinlife/version-checker/main/data/vs.json) |
| .NET Framework | Windows 的托管执行环境，可为其运行的应用提供各种服务 | [dotnetfx](https://raw.githubusercontent.com/designinlife/version-checker/main/data/dotnetfx.json) |
| OpenWrt | 一个高度模块化、高度自动化的嵌入式 Linux 系统 | [openwrt](https://raw.githubusercontent.com/designinlife/version-checker/main/data/openwrt.json) |
| MSYS2 | 一个 MSYS 的独立改写版本，主要用于 Windows shell 命令行开发环境 | [msys2](https://raw.githubusercontent.com/designinlife/version-checker/main/data/msys2.json) |
| Prometheus | 一个开源的系统监控和警报工具 | [prometheus](https://raw.githubusercontent.com/designinlife/version-checker/main/data/prometheus.json) |
| PushGateway for Prometheus | 另一种数据采集的方式，采用被动推送来获取监控数据的 prometheus 插件 | [pushgateway](https://raw.githubusercontent.com/designinlife/version-checker/main/data/pushgateway.json) |
| VMware Workstation Pro | VMware 出品的著名虚拟机软件 | [vmware-workstation-pro](https://raw.githubusercontent.com/designinlife/version-checker/main/data/vmware-workstation-pro.json) |
| VMware ESXi | ESXi 是用于创建并运行虚拟机和虚拟设备的虚拟化平台 | [vmware-esxi](https://raw.githubusercontent.com/designinlife/version-checker/main/data/vmware-esxi.json) |
| VMware vSphere (ESXi) | 业界领先且最可靠的虚拟化平台 | [vmware-vsphere](https://raw.githubusercontent.com/designinlife/version-checker/main/data/vmware-vsphere.json) |
| Sublime Text 4 | 功能强大的代码文本编辑器 | [sublime](https://raw.githubusercontent.com/designinlife/version-checker/main/data/sublime.json) |
| NetSarang Xshell | 一个强大的安全终端模拟软件，它支持 SSH1, SSH2, 以及 Microsoft Windows 平台的 TELNET 协议 | [xshell](https://raw.githubusercontent.com/designinlife/version-checker/main/data/xshell.json) |
| Helm | Helm 是 Kubernetes 的包管理工具 | [helm](https://raw.githubusercontent.com/designinlife/version-checker/main/data/helm.json) |

## Add Source

```bash
poetry source add --priority=default PyPi https://pypi.org/simple/
```

## Build wheel

```bash
poetry build -f wheel
```

## Run

```bash
poetry run version-checker inspect
```
