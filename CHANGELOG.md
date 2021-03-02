# Changelog

## [Unreleased](https://github.com/metricq/metricq-python/tree/HEAD)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.4.0...HEAD)

**Fixed bugs:**

- Docker action seems to be broken on linux/arm64 [\#69](https://github.com/metricq/metricq-python/issues/69)

**Merged pull requests:**

- Spring cleanup [\#74](https://github.com/metricq/metricq-python/pull/74) ([phijor](https://github.com/phijor))
- Require python 3.8 for ssl fixes [\#70](https://github.com/metricq/metricq-python/pull/70) ([kinnarr](https://github.com/kinnarr))
- Management channel is a RobustChannel [\#64](https://github.com/metricq/metricq-python/pull/64) ([phijor](https://github.com/phijor))
- Improve Error Handling [\#63](https://github.com/metricq/metricq-python/pull/63) ([tilsche](https://github.com/tilsche))
- fix\(ci\): Fix changelog workflow [\#61](https://github.com/metricq/metricq-python/pull/61) ([bmario](https://github.com/bmario))
- Fixes missing non-historic metrics in metricq spy [\#60](https://github.com/metricq/metricq-python/pull/60) ([bmario](https://github.com/bmario))

## [v1.4.0](https://github.com/metricq/metricq-python/tree/v1.4.0) (2020-12-12)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.3.0...v1.4.0)

**Implemented enhancements:**

- Request-type-specific historic interface [\#56](https://github.com/metricq/metricq-python/issues/56)

**Fixed bugs:**

- Sporadic SSLErrors on Client close [\#18](https://github.com/metricq/metricq-python/issues/18)

**Closed issues:**

- Deprecation of HistoryClient.history\_metric\_metadata\(\) [\#55](https://github.com/metricq/metricq-python/issues/55)

**Merged pull requests:**

- Add history request convenience methods [\#57](https://github.com/metricq/metricq-python/pull/57) ([phijor](https://github.com/phijor))
- Add sphinx-based documentation [\#6](https://github.com/metricq/metricq-python/pull/6) ([phijor](https://github.com/phijor))

## [v1.3.0](https://github.com/metricq/metricq-python/tree/v1.3.0) (2020-10-14)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.2.0...v1.3.0)

**Implemented enhancements:**

- Automate changelog generation via workflow [\#38](https://github.com/metricq/metricq-python/issues/38)
- Include source version in discover response [\#24](https://github.com/metricq/metricq-python/issues/24)
- Add changelog to GitHub Release [\#41](https://github.com/metricq/metricq-python/pull/41) ([kinnarr](https://github.com/kinnarr))

**Fixed bugs:**

- stop\(\) failure [\#48](https://github.com/metricq/metricq-python/issues/48)
- Reconnect issue in Websocket [\#22](https://github.com/metricq/metricq-python/issues/22)

**Closed issues:**

- Failed to find version of HistoryClient [\#47](https://github.com/metricq/metricq-python/issues/47)
- Split release job [\#34](https://github.com/metricq/metricq-python/issues/34)
- Trigger code checks on pull requests [\#32](https://github.com/metricq/metricq-python/issues/32)
- flake8 configuration file [\#31](https://github.com/metricq/metricq-python/issues/31)
- Add isort to CI [\#30](https://github.com/metricq/metricq-python/issues/30)
- Precise Pretty Printing of durations [\#27](https://github.com/metricq/metricq-python/issues/27)

**Merged pull requests:**

- Fix release workflow [\#53](https://github.com/metricq/metricq-python/pull/53) ([kinnarr](https://github.com/kinnarr))
- Trigger python package workflow from release workflow [\#52](https://github.com/metricq/metricq-python/pull/52) ([kinnarr](https://github.com/kinnarr))
- Adds a workflow for docker image build and upload [\#49](https://github.com/metricq/metricq-python/pull/49) ([bmario](https://github.com/bmario))
- Fix mypy protobuf packaging [\#43](https://github.com/metricq/metricq-python/pull/43) ([tilsche](https://github.com/tilsche))
- Release workflow [\#42](https://github.com/metricq/metricq-python/pull/42) ([kinnarr](https://github.com/kinnarr))
- Issue 27 - Precise and Pretty Timedelta [\#28](https://github.com/metricq/metricq-python/pull/28) ([Daddelhai](https://github.com/Daddelhai))
- Fix reconnect issues [\#44](https://github.com/metricq/metricq-python/pull/44) ([bmario](https://github.com/bmario))
- Generate changelog for closed PRs and issues [\#40](https://github.com/metricq/metricq-python/pull/40) ([kinnarr](https://github.com/kinnarr))
- Split release job [\#37](https://github.com/metricq/metricq-python/pull/37) ([kinnarr](https://github.com/kinnarr))
- Test and lint: improved CI [\#36](https://github.com/metricq/metricq-python/pull/36) ([phijor](https://github.com/phijor))
- Improve output of sample tools [\#33](https://github.com/metricq/metricq-python/pull/33) ([phijor](https://github.com/phijor))
- Add client version to discover response [\#29](https://github.com/metricq/metricq-python/pull/29) ([phijor](https://github.com/phijor))
- Add mypy check for github workflow [\#3](https://github.com/metricq/metricq-python/pull/3) ([bmario](https://github.com/bmario))

## [v1.2.0](https://github.com/metricq/metricq-python/tree/v1.2.0) (2020-08-03)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.1.4...v1.2.0)

**Implemented enhancements:**

- Add "hostname" to discover response [\#19](https://github.com/metricq/metricq-python/issues/19)
- Add metricq-spy tool, which allows to search for historic metrics [\#39](https://github.com/metricq/metricq-python/issues/39)
- discover RPC: rename "version" field to "metricqVersion" [\#15](https://github.com/metricq/metricq-python/issues/15)
- Add field "hostname" to discover response [\#20](https://github.com/metricq/metricq-python/pull/20) ([phijor](https://github.com/phijor))

**Fixed bugs:**

- Python agents fail to anwser discover rpc [\#8](https://github.com/metricq/metricq-python/issues/8)
- Add setuptools as runtime dependecies [\#14](https://github.com/metricq/metricq-python/issues/14)
- Protobuf version conflict [\#10](https://github.com/metricq/metricq-python/issues/10)

**Merged pull requests:**

- Use protobuf version from compile time [\#21](https://github.com/metricq/metricq-python/pull/21) ([kinnarr](https://github.com/kinnarr))
- Fix package version related issues [\#16](https://github.com/metricq/metricq-python/pull/16) ([phijor](https://github.com/phijor))

## [v1.1.4](https://github.com/metricq/metricq-python/tree/v1.1.4) (2020-06-24)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.1.3...v1.1.4)

**Closed issues:**

- Fix protobuf building [\#2](https://github.com/metricq/metricq-python/issues/2)
- Create repo metricq-python [\#1](https://github.com/metricq/metricq-python/issues/1)

**Merged pull requests:**

- Fix protobuf compilation [\#5](https://github.com/metricq/metricq-python/pull/5) ([phijor](https://github.com/phijor))

## [v1.1.3](https://github.com/metricq/metricq-python/tree/v1.1.3) (2020-03-23)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.1.2...v1.1.3)

**Merged pull requests:**

- Cleanup shutdown [\#53](https://github.com/metricq/metricq/pull/53) ([tilsche](https://github.com/tilsche))
- GitHub actions cpp [\#52](https://github.com/metricq/metricq/pull/52) ([bmario](https://github.com/bmario))

## [v1.1.2](https://github.com/metricq/metricq-python/tree/v1.1.2) (2020-02-21)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.1.1...v1.1.2)

**Merged pull requests:**

- Adds github action for python tests and release [\#51](https://github.com/metricq/metricq/pull/51) ([kinnarr](https://github.com/kinnarr))

## [v1.1.1](https://github.com/metricq/metricq-python/tree/v1.1.1) (2020-02-21)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.1.0...v1.1.1)

**Fixed bugs:**

- metricq won't build with -Werror due to deprecated history.proto items [\#49](https://github.com/metricq/metricq/issues/49)
- connection reset by peer - channel robustness in python [\#38](https://github.com/metricq/metricq/issues/38)
- Invalid state after robust reconnect [\#23](https://github.com/metricq/metricq/issues/23)

## [v1.1.0](https://github.com/metricq/metricq-python/tree/v1.1.0) (2019-12-10)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.0.0...v1.1.0)

**Merged pull requests:**

- Robust Agents: make Agents survive reconnects [\#46](https://github.com/metricq/metricq/pull/46) ([phijor](https://github.com/phijor))
- Improvements for docker deployment [\#45](https://github.com/metricq/metricq/pull/45) ([kinnarr](https://github.com/kinnarr))
- More config options for dummy sink and source [\#43](https://github.com/metricq/metricq/pull/43) ([kinnarr](https://github.com/kinnarr))

## [v1.0.0](https://github.com/metricq/metricq-python/tree/v1.0.0) (2019-10-01)

[Full Changelog](https://github.com/metricq/metricq-python/compare/f3ad7c612e87569afc26f44268c2e4c4dc93161b...v1.0.0)

- Initial release

\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
