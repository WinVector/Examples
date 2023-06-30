from Preferences import Preferences


def test_Preferences_1():
    p = Preferences([3, 2, 1])
    assert p.considers(3)
    assert not p.considers(4)
    assert p.prefers(3, 1)
    assert not p.prefers(1, 3)
