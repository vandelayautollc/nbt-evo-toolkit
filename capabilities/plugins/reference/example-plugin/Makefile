# Cross-build the Diagnostics HMI plugin for NBT-Evo (QNX/ARM). gcc 4.4.2 == OEM toolchain.
# Source your QNX SDP 6.5.0 env first (sets QNX_HOST/QNX_TARGET + the ntoarm toolchain on PATH);
# see ../../docs/08-building-and-deploying.md.
# CARVE points at YOUR OWN extracted HMI tree (SWFL 00002720 istep) — supply it, e.g.:
#   export NBTEVO_CARVE=/path/to/your/carved/00002720/fs/sda0/repository/istep
# The reference plugin's headers (bmw_abi.h, bmw_list.h) live in ../sdk.
CXX      := ntoarm-g++
CARVE    := $(NBTEVO_CARVE)
LIBS     := $(CARVE)/opt/hmi/ID5/lib/libAppFramework.A.so $(CARVE)/opt/hmi/ID5/lib/libCoreFramework.A.so
CXXFLAGS := -shared -fPIC -O2 -fno-strict-aliasing -Wall -fno-exceptions -I../sdk
LDFLAGS  := -Wl,--allow-shlib-undefined -Wl,-soname,libDiagnostics.so

# SRC = diagnostics.cpp for the full reference plugin, or hello_plugin_stage1.cpp for the
# minimal "does it even load?" stage-1 proof (see ../../docs/08-building-and-deploying.md).
SRC      := diagnostics.cpp

libDiagnostics.so: $(SRC) ../sdk/bmw_list.h ../sdk/bmw_abi.h
	$(CXX) $(CXXFLAGS) $(SRC) $(LIBS) $(LDFLAGS) -o $@

clean:
	rm -f libDiagnostics.so
