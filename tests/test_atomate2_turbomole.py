# Part of atomate2-turbomole package.

"""General tests of the atomate2-turbomole package."""


from atomate2.turbomole import __version__


def test_version():
    assert isinstance(__version__, str)
