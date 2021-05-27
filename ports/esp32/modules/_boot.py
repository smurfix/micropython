import uos
try:
    _DT_T
    uos.dupterm_notify
except AttributeError:
    pass
except NameError:
    from machine import Timer as _Timer
    _DT_T = _Timer(3)
    _DT_T.init(mode=_Timer.PERIODIC, callback=uos.dupterm_notify, freq=50)

import gc
from flashbdev import bdev

try:
    if bdev:
        uos.mount(bdev, "/")
except OSError:
    import inisetup

    vfs = inisetup.setup()

gc.collect()
