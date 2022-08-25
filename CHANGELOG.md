# Changelog

## [Unreleased](https://github.com/metricq/metricq-python/tree/HEAD)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v4.1.0...HEAD)

**Implemented enhancements:**

- Remove virtualenv from the docker image [\#133](https://github.com/metricq/metricq-python/issues/133)

**Fixed bugs:**

- Documentation for HistoryClient and Subscriber contains errors [\#129](https://github.com/metricq/metricq-python/issues/129)
- Add ContextManager for metricq.Client [\#127](https://github.com/metricq/metricq-python/issues/127)

**Merged pull requests:**

- feat: Context manager support for metricq.Client [\#132](https://github.com/metricq/metricq-python/pull/132) ([bmario](https://github.com/bmario))

## [v4.1.0](https://github.com/metricq/metricq-python/tree/v4.1.0) (2022-07-11)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v4.0.0...v4.1.0)

**Implemented enhancements:**

- Add `dict\(\)` method to `TimeValue` and `TimeAggregate` [\#121](https://github.com/metricq/metricq-python/issues/121)

**Fixed bugs:**

- Sphix extension sphinx-autodoc-typehints 1.12.0 seems to be broken [\#98](https://github.com/metricq/metricq-python/issues/98)

**Merged pull requests:**

- feat: add `dict\(\)` to value and aggrate types [\#122](https://github.com/metricq/metricq-python/pull/122) ([bmario](https://github.com/bmario))

## [v4.0.0](https://github.com/metricq/metricq-python/tree/v4.0.0) (2022-05-30)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v3.1.1...v4.0.0)

**Breaking changes:**

- Feature: Python 3.10 support [\#119](https://github.com/metricq/metricq-python/pull/119) ([bmario](https://github.com/bmario))

**Fixed bugs:**

- Refactor `loop` parameter usage [\#51](https://github.com/metricq/metricq-python/issues/51)

**Closed issues:**

- Fix changelog in Github release [\#103](https://github.com/metricq/metricq-python/issues/103)

## [v3.1.1](https://github.com/metricq/metricq-python/tree/v3.1.1) (2021-10-20)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v3.1.0...v3.1.1)

**Fixed bugs:**

- RPC messages send without `function` [\#118](https://github.com/metricq/metricq-python/issues/118)

## [v3.1.0](https://github.com/metricq/metricq-python/tree/v3.1.0) (2021-10-19)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v3.0.0...v3.1.0)

**Implemented enhancements:**

- Consider declaring queues as "auto-delete" for transient sinks [\#67](https://github.com/metricq/metricq-python/issues/67)
- Implement drain [\#12](https://github.com/metricq/metricq-python/issues/12)
- feat: support new hidden parameter for get\_metrics RPC [\#114](https://github.com/metricq/metricq-python/pull/114) ([kinnarr](https://github.com/kinnarr))
- feat: add a connection name for better identification in the management UI [\#110](https://github.com/metricq/metricq-python/pull/110) ([kinnarr](https://github.com/kinnarr))
- feat: add required py.typed file to support typing when used as library [\#105](https://github.com/metricq/metricq-python/pull/105) ([kinnarr](https://github.com/kinnarr))
- Feature: New tool metricq-inspect [\#96](https://github.com/metricq/metricq-python/pull/96) ([bmario](https://github.com/bmario))
- Feature strict typing [\#117](https://github.com/metricq/metricq-python/pull/117) ([bmario](https://github.com/bmario))

**Fixed bugs:**

- Timedelta properties missing in documentation [\#115](https://github.com/metricq/metricq-python/issues/115)
- HistoryClient reconnects [\#58](https://github.com/metricq/metricq-python/issues/58)
- Protobuf dependency pip thingy? [\#26](https://github.com/metricq/metricq-python/issues/26)
- Handle channel errors in `HistoryClient` [\#108](https://github.com/metricq/metricq-python/issues/108)
- history client reconnect issues [\#75](https://github.com/metricq/metricq-python/issues/75)

**Closed issues:**

- Skip mypy check in workflow for external PRs [\#109](https://github.com/metricq/metricq-python/issues/109)
- Add a how-to for new projects [\#106](https://github.com/metricq/metricq-python/issues/106)
- Unify docstring style [\#71](https://github.com/metricq/metricq-python/issues/71)

**Merged pull requests:**

- Fix reconnect for HistoryClients [\#116](https://github.com/metricq/metricq-python/pull/116) ([bmario](https://github.com/bmario))
- Unify docstrings to use Google style [\#113](https://github.com/metricq/metricq-python/pull/113) ([phijor](https://github.com/phijor))
- Add project setup how-to [\#112](https://github.com/metricq/metricq-python/pull/112) ([phijor](https://github.com/phijor))
- Feature Drain and Subscription [\#111](https://github.com/metricq/metricq-python/pull/111) ([Daddelhai](https://github.com/Daddelhai))

## [v3.0.0](https://github.com/metricq/metricq-python/tree/v3.0.0) (2021-05-06)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v2.0.1...v3.0.0)

**Breaking changes:**

- fix: remove broken TimeAggregate.integral [\#102](https://github.com/metricq/metricq-python/pull/102) ([kinnarr](https://github.com/kinnarr))

**Implemented enhancements:**

- Improve the availability of the tools [\#91](https://github.com/metricq/metricq-python/issues/91)

**Closed issues:**

- RPC errors / timeouts should lead to FAILURE terminationEnsure that RPC timeouts [\#11](https://github.com/metricq/metricq-python/issues/11)
- Remove tools directory, refer to dedicated metricq-tools repo [\#99](https://github.com/metricq/metricq-python/issues/99)

**Merged pull requests:**

- Move tools to their own repository [\#101](https://github.com/metricq/metricq-python/pull/101) ([phijor](https://github.com/phijor))
- Trigger docker workflow on release [\#100](https://github.com/metricq/metricq-python/pull/100) ([kinnarr](https://github.com/kinnarr))

## [v2.0.1](https://github.com/metricq/metricq-python/tree/v2.0.1) (2021-04-21)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v2.0.0...v2.0.1)

**Fixed bugs:**

- Setting period to None in IntervalSource [\#92](https://github.com/metricq/metricq-python/issues/92)

**Closed issues:**

- Change log level for rpc logging to debug [\#93](https://github.com/metricq/metricq-python/issues/93)

**Merged pull requests:**

- IntervalSource: Raise descriptive error on period reset [\#95](https://github.com/metricq/metricq-python/pull/95) ([phijor](https://github.com/phijor))
- Reduce log level when handling RPCs to DEBUG [\#94](https://github.com/metricq/metricq-python/pull/94) ([phijor](https://github.com/phijor))
- IntervalSource.period=None is definitely not supported [\#97](https://github.com/metricq/metricq-python/pull/97) ([phijor](https://github.com/phijor))

## [v2.0.0](https://github.com/metricq/metricq-python/tree/v2.0.0) (2021-03-23)

[Full Changelog](https://github.com/metricq/metricq-python/compare/v1.4.0...v2.0.0)

**Breaking changes:**

- Make `IntervalSource.period` a `Timedelta` [\#85](https://github.com/metricq/metricq-python/pull/85) ([phijor](https://github.com/phijor))
- Fix TimeAggregate member types [\#80](https://github.com/metricq/metricq-python/pull/80) ([phijor](https://github.com/phijor))
- Remove deprecated methods [\#78](https://github.com/metricq/metricq-python/pull/78) ([phijor](https://github.com/phijor))
- Require python 3.8 for ssl fixes [\#70](https://github.com/metricq/metricq-python/pull/70) ([kinnarr](https://github.com/kinnarr))
- Augment "chunkSize" to metadata when declaring new metrics [\#68](https://github.com/metricq/metricq-python/pull/68) ([phijor](https://github.com/phijor))
- Improve Error Handling [\#63](https://github.com/metricq/metricq-python/pull/63) ([tilsche](https://github.com/tilsche))

**Implemented enhancements:**

- Add python version to discover [\#89](https://github.com/metricq/metricq-python/issues/89)
- Add python version to discover response [\#90](https://github.com/metricq/metricq-python/pull/90) ([phijor](https://github.com/phijor))

**Fixed bugs:**

- Docker action seems to be broken on linux/arm64 [\#69](https://github.com/metricq/metricq-python/issues/69)
- Timestamp.from\_iso8601 fails to parse JSON timestamp [\#9](https://github.com/metricq/metricq-python/issues/9)

**Closed issues:**

- Add chunk size to metadata [\#65](https://github.com/metricq/metricq-python/issues/65)
- Document all breaking changes for v2 [\#83](https://github.com/metricq/metricq-python/issues/83)
- IntervalSource.period should be a Timedelta, not a float. [\#81](https://github.com/metricq/metricq-python/issues/81)
- Consider updating types of TimeAggregate.{integral,active\_time} [\#76](https://github.com/metricq/metricq-python/issues/76)
- Remove deprecated methods/behavior [\#73](https://github.com/metricq/metricq-python/issues/73)
- Support HistoryResponse error messages [\#62](https://github.com/metricq/metricq-python/issues/62)
- Timestamps from iso strings [\#7](https://github.com/metricq/metricq-python/issues/7)

**Merged pull requests:**

- Prevent possibly unbound variable in history response handler [\#84](https://github.com/metricq/metricq-python/pull/84) ([phijor](https://github.com/phijor))
- Tool metric send [\#79](https://github.com/metricq/metricq-python/pull/79) ([bmario](https://github.com/bmario))
- Spring cleanup [\#74](https://github.com/metricq/metricq-python/pull/74) ([phijor](https://github.com/phijor))
- Management channel is a RobustChannel [\#64](https://github.com/metricq/metricq-python/pull/64) ([phijor](https://github.com/phijor))
- fix\(ci\): Fix changelog workflow [\#61](https://github.com/metricq/metricq-python/pull/61) ([bmario](https://github.com/bmario))
- Fixes missing non-historic metrics in metricq spy [\#60](https://github.com/metricq/metricq-python/pull/60) ([bmario](https://github.com/bmario))
- Upgrading instructions [\#87](https://github.com/metricq/metricq-python/pull/87) ([phijor](https://github.com/phijor))
- Properly parse ISO 8601 date strings to Timestamp [\#86](https://github.com/metricq/metricq-python/pull/86) ([phijor](https://github.com/phijor))
- Timedelta typing changes and proper division support [\#82](https://github.com/metricq/metricq-python/pull/82) ([phijor](https://github.com/phijor))
- Handle error messages in history responses [\#66](https://github.com/metricq/metricq-python/pull/66) ([bmario](https://github.com/bmario))

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
