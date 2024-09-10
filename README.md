# atomate2-turbomole

[![tests](https://img.shields.io/github/actions/workflow/status/Matgenix/atomate2-turbomole/testing.yml?branch=main&label=tests)](https://github.com/Matgenix/atomate2-turbomole/actions?query=workflow%3Atesting)
[![code coverage](https://img.shields.io/codecov/c/gh/Matgenix/atomate2-turbomole)](https://codecov.io/gh/Matgenix/atomate2-turbomole)
[![pypi version](https://img.shields.io/pypi/v/atomate2-turbomole?color=blue)](https://pypi.org/project/atomate2-turbomole)
![supported python versions](https://img.shields.io/pypi/pyversions/atomate2-turbomole)

**[Full Documentation][docs]**

Atomate2-turbomole is an add-on package for [atomate2](https://github.com/materialsproject/atomate2).

Atomate2-turbomole is built to work with Turbomole, and is built on top of open source
libraries such as [pymatgen](https://github.com/materialsproject/pymatgen),
[custodian](https://github.com/materialsproject/custodian),
[jobflow](https://github.com/materialsproject/jobflow)
and [turbomoleio](https://github.com/Matgenix/turbomoleio).

Currently, the jobs and flows have been implemented and tested for Turbomole version 7.6 and 7.7 series. The
atomate2-turbomole thus relies on the turbomoleio version that is compatible with Turbomole version used.
For information, hereafter is a table with compatible versions of Turbomole:

| TURBOMOLE version(s) | atomate2-turbomole version(s) | turbomoleio version(s) |
|:---------------------|:-----------------------------:|-----------------------:|
| 7.7 series           |         0.2.x series          |           1.5.x series |
| 7.6 series           |         0.1.x series          |           1.4.x series |

Note that the turbomoleio version is pinned in the atomate2-turbomole version, i.e. if you install a given
atomate2-turbomole version, the corresponding (compatible) turbomoleio version will be installed. You only
have to choose which atomate2-turbomole version to use based on the Turbomole release you have.

## Need help?

If you've found an issue with atomate2-turbomole, please submit a bug report on [GitHub Issues][issues].

## What’s new?

Track changes to atomate2-turbomole through the [changelog][changelog].

## Contributing

We greatly appreciate any contributions in the form of a pull request.
Additional information on contributing to atomate2-turbomole can be found [here][contributing].
We maintain a list of all contributors [here][contributors].

### Code of conduct

Help us keep atomate2-turbomole open and inclusive.
Please read and follow our [Code of Conduct][codeofconduct].

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

## License

This add-on is released under the same license as atomate2, modified BSD; the full text can be found [here][license].

## Citation

If you use atomate2-turbomole in your work, please cite it as follows:

- "atomate2-turbomole: an open-source add-on to atomate2 workflows for
Turbomole, [https://github.com/Matgenix/atomate2-turbomole](https://github.com/Matgenix/atomate2-turbomole)

## Acknowledgements

atomate2-turbomole is developed and maintained by Matgenix SRL.
The copyright of atomate2-turbomole is shared by Matgenix SRL and Toyota Motor Europe SA.

A full list of all contributors can be found [here][contributors].

[issues]: https://github.com//Matgenix/atomate2-turbomole/issues
[changelog]: https://github.com//Matgenix/atomate2-turbomole/blob/main/CHANGELOG.md
[contributors]: https://github.com/Matgenix/atomate2-turbomole/graphs/contributors
[contributing]: https://github.com/Matgenix/atomate2-turbomole/blob/main/CONTRIBUTING.md
[codeofconduct]: https://github.com/Matgenix/atomate2-turbomole/blob/main/CODE_OF_CONDUCT.md
[license]: https://raw.githubusercontent.com/Matgenix/atomate2-turbomole/blob/main/LICENSE
[docs]: https://Matgenix.github.io/atomate2-turbomole/
