from pfs_etc_web.pfs_etc_utils import _active_arm_keys


def test_active_arm_keys_normal_mode():
    assert _active_arm_keys(mr_mode=False) == ["b", "r", "n"]


def test_active_arm_keys_medium_resolution_mode():
    assert _active_arm_keys(mr_mode=True) == ["b", "m", "n"]
