freeze("$(PORT_DIR)/modules")
include("$(MPY_DIR)/extmod/uasyncio")
require("onewire")
require("ds18x20")
require("dht")
require("neopixel")

include("../../../../../moat/micro/_embed/lib")
