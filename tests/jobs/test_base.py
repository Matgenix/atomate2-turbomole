from atomate2.turbomole.jobs.base import BaseTurbomoleMaker
from atomate2.turbomole.sets.core import TurbomoleDefineInputGenerator
from jobflow.core.job import Job


def test_base_turbomole_empty_maker():
    """Test correct return type from BaseTurbomoleMaker make.
    TODO: improve with more significant case
    """
    tm_dig = TurbomoleDefineInputGenerator()
    bnm = BaseTurbomoleMaker(tm_dig, "ridft", "ScfTaskDocument")
    res = bnm.make()
    assert isinstance(res, Job)
    assert res.output.attributes == ()
