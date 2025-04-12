# base modules
import os
import moat.micro
emb=moat.micro.__path__[0]

freeze("$(PORT_DIR)/modules")
require("bundle-networking")

include("$(MPY_DIR)/extmod/asyncio")
include(emb+"/_embed/lib")
