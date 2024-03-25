# Part of atomate2-turbomole package.

# Automatically get the version of the package
# For python versions < 3.8, importlib.metadata module did not exist,
# had to use importlib_metadata instead.
try:  # pragma: no cover
    from importlib.metadata import version
except ModuleNotFoundError:  # pragma: no cover
    from importlib_metadata import version  # type: ignore

__version__ = version("atomate2-turbomole")
