miscDir = "../pc_libs"
phyapiIncDir = os.path.join(miscDir, "phyapi-3.0.0/inc")
phyapiLibDir = os.path.join(miscDir, "phyapi-3.0.0")
f8apiIncDir = os.path.join(miscDir, "f8api-2.0.0/inc/f8api")
f8apiLibDir = os.path.join(miscDir, "f8api-2.0.0/src")
picoifIncDir = os.path.join(miscDir, "libpicoif-1.3.1/include")
picoifLibDir = os.path.join(miscDir, "libpicoif-1.3.1/localbus")
picogpioIncDir = os.path.join(miscDir, "libpicogpio-1.1.0/include")
picogpioLibDir = os.path.join(miscDir, "libpicogpio-1.1.0/src")
libradioIncDir = os.path.join(miscDir, "libradio-1.0.4/lib")
libradioLibDir = os.path.join(miscDir, "libradio-1.0.4/lib")
openSslIncDir = os.path.join(miscDir, "openssl-0.9.8k/include")
openSslLibDir = os.path.join(miscDir, "openssl-0.9.8k/lib")

crossCompiler = "arm-none-linux-gnueabi-"

compiler = crossCompiler + "gcc"
linker = crossCompiler + "gcc"
ar = crossCompiler + "ar"
commonCFlags = ["-Wall", "-O3", "-Wcast-qual", "-Wstrict-prototypes"]
commonDefines = ["OAM_CLI_FEATURE", "FAP_DEBUG_SWITCH=1", "FWEXT_UTILITY",
    "PC302", "_SON_RANDOMIZE_PSC_", "_ALARM_OPTIMIZATION_",
    "CLEAN_NPT_LOCK_FILE"]
     # "_SON_RANDOMIZE_LAC_", "_FAULT_RECOVERY_OPTIMIZATION_",
     # "OPEN_384K"
commonLdFlags = ["-Xlinker", "--start-group"]
buildDir = ".build"
activeConfiguration = "debug"
configurations = {
    "debug": {
        "cflags": commonCFlags + ["-g"],
        "ldflags": commonLdFlags,
        "defines": commonDefines,
        "buildsubdir": "Debug",
    },
    "release": {
        "cflags": commonCFlags,
        "ldflags": commonLdFlags,
        "defines": commonDefines,
        "buildsubdir": "Release",
    },
}
libraryPaths = ["rrm/rncwrapper/lib", "rns/release",
    phyapiLibDir, f8apiLibDir, picoifLibDir, picogpioLibDir,
    libradioLibDir, openSslLibDir, "osl/asn1", "syn/ntp/lib",
    "oam/libsoap", "rrm/l1if"]
libraries = ["rns", "rncwrapper", "l1if", "phyApi",
    "picoif", "asn1", "picogpio", "PICONTPF",
    "nsl", "rt", "m", "crypto", "ssl", "crypt", "dl",
    "f8api", "radio", "soap", "pthread"]
modules = {
    "cmm" : {
        "incpaths": ["cmm/inc"]},
    "oam" : {
        "depends": ["cmm", "rrm", "son", "sec", "syn"],
        "sourcefilter": '(not "test" in ?) and (not "oam/soap" in ?)',
        "incpaths": ["oam/inc", "oam/client/inc", "oam/cmm/inc",
            "oam/app/inc", "oam/cm/inc", "oam/pm/inc", "oam/swm/inc",
            "oam/fm/inc", "oam/api", "oam/libsoap"],
        "extincpaths": [openSslIncDir, picogpioIncDir,
            "osl/openssl/include"]
    },
    "son" : {
        "depends": ["oam", "cmm"],
        "sourcefilter": 'not "test" in ?',
        "incpaths": ["son/hdl/inc", "son/gsd/inc", "son/api/inc",
            "son/alg/inc", "son/npc/inc"]
        "extincpaths": [phyapiIncDir, picoifIncDir, libradioIncDir,
            "osl/asn1/usrDec/inc"],
        "defines": ["PC302=1", "NEC_IOT=1"]
    },
    "sec" : {
        "depends": ["oam", "cmm"],
        "sourcefilter": 'not "test" in ?',
        "incpaths": ["sec/inc"],
    },
    "syn" : {
        "depends": ["cmm"],
        "sourcefiles": ["syn/ntp/src/" + s for s in
            ("PC73X2_4_core.c", "msg.c", "sync.c",
            "storage.c", "startup.c", "ctrl.c", "oscillator.c",
            "PC73X2_4_ntpf.c", "ntpf_utils.c")],
        "incpaths": ["syn/ntp/src"],
        "extincpaths": [picogpioIncDir, picoifIncDir]
        "cflags": ["-mabi=aapcs-linux", "-mfloat-abi=soft"],
        "defines": ["GNU_CC", "xPC73X2_BUILD", "FREQ=19.2", "DEBUG",
            "API_BUILD", "TOOLS_BSP=4", "KERNEL_2_6_30_PLUS"],
    },
    "fmw" : {
        "depends": ["oam", "son", "rrm", "sec", "cmm"]
        "extincpaths": ["osl/openssl/include"],
        "cflags": ["-O2", "-Wshadow", "-Wcast-qual", "-Wstrict-prototypes"],
        "defines": ["FAP_DEBUG_SWITCH=1", "FWEXT_UTILITY"],
    },
    "rrm": {
        "depends": ["cmm", "oam"],
        "sourcefilter":
            '(not "test" in ?) and (not "rncwrapper" in ?)' \
            'and (not "l1if" in ?)',
        "incpaths": ["rrm/inc",
            "rrm/l1if/LittleEndianMsgAccess/inc",
            "rrm/l1if/MsgDecHdlrs/inc",
            "rrm/l1if/MsgEncHdlrs/inc",
            "rrm/l1if/ProcDecHdlrs/inc",
            "rrm/l1if/ProcEncHdlrs/inc",
            "rrm/l1if/StructDefs/inc",
            "rrm/l1if/UserProcDecHdlrs/inc",
            "rrm/l1if/UserProcEncHdlrs/inc"],
        "extincpaths": ["rns", "rrm/rncwrapper", picoifIncDir,
            f8apiIncDir, phyapiIncDir,libradioIncDir]
        "defines": ["SUNOS", "SS", "SS_MT", "ANSI", "_GNU_SOURCE",
            "SS_LINUX", "_REENTRANT", "__EXTENSIONS__",
            "DEBUGNOEXIT", "RX", "RR", "LR", "RX", "SM",
            "LCLRX", "MK", "RR", "REL5_HS", "LCRRLICMK",
            "LCMKUICMK", "LCCMK", "LCHRT", "LCHRUIHRT",
            "LCLXLIHRT", "LCXULIHRT", "LCHRMILHR", "RL",
            "RR", "LCRRLICRL", "LCRLUICRL", "LCCRL", "RL", "RR",
            "LR", "TC", "LCRLU", "LCRLUIRLU", "LCRRLICTC",
            "LCTCUICTC", "LCCTC", "LCSMMILRR", "LCRRMILRR",
            "LCSMMILRX", "LCRXMILRX", "RU", "LCRULIRPT",
            "LCRAUIRPT", "LCRPT", "RPT_REL5", "LXT_V1", "GT",
            "LX", "HR", "XU", "RNC", "xFP_NODEB",
            "CMINET_BSDCOMPAT", "FAP_IUH",
            "RA_HNB", "SS_TICKS_SEC=1000", "CMFILE_REORG_1",
            "CM_INET2", "_GNU_SOURCE", "CMFILE_REORG_2", "SSINT2",
            "CMKV2", "SS_PERF", "NO_ERRCLS", "NOERRCHK",
            "SS_M_PROTO_REGION", "RLC_R6", "MK_HSDPA", "MK_HSUPA",
            "MK_MBMS", "MK_EHS", "OP_IU", "GTP_U", "GTP_U_3G",
            "GR", "GI", "RU", "LCRULIRPT", "LCRAUIRPT", "LCRPT",
            "RPT_REL5", "LCLRA", "FP_RELEASE6", "SM", "RA",
            "LCSMRAMILRA", "LCRAMILRA", "SM", "RA_UTRAN",
            "RPT_REL99_360", "RESET_PROCEDURE", "RRM_VBR_ENABLED"]
             + ["xRRM_L1_DIAG_SELF_DEBUG", "xRRM_L1_DIAG_ENABLE"]
             + ["RRM_RADIOAPI"]
             + ["RRM_ENV_PARAM"]
    },
}

program = "fap"
executableName = program + "." + activeConfiguration

@cache
def getModuleDirectory(moduleName):
    return modules.get("directory", moduleName)

@cache
def getActiveBuildPath():
    p = os.path.join(buildDir,
        configurations[activeConfiguration]["buildsubdir"])
    if not os.path.exists(p):
        os.makedirs(p)
    return p

@cache
def getExecutablePath():
    return os.path.join(getActiveBuildPath(), executableName)

# Example:
# --------
# .PHONY: all
# all: fap

Phony("all")
@rule("all", program)
def makeAll(target):
    pass

# Example:
# --------
# .PHONY: fap
# fap: ./build/Debug/fap.debug

Phony(program)
@rule(program, getExecutablePath())
def makeProgram(target):
    runShellCommand(["cp", getExecutablePath(), "."])

# Example:
# --------
# ./build/Debug/fap.debug: ./build/Debug/oam/liboam.a \
#     ./build/Debug/rrm/librrm.a ...

@cache
def getModuleOutputPath(moduleName):
    return os.path.join(
        getActiveBuildPath(),
        getModuleDirectory(moduleName),
        "lib%s.a" % moduleName)


@rule(getExecutablePath(), [getModuleOutputPath(m) for m in list(modules)])
def makeExecutable(target):
    config = configurations[activeConfiguration]
    moduleOutputDirs = [os.path.join(getActiveBuildPath(),
        getModuleDirectory(m)) for m in modules]
    link(linker=linker,
        libpaths=libraryPaths + moduleOutputDirs,
        libraries=libraries + list(modules),
        ldFlags=config["ldflags"],
        executable=getExecutablePath())

# Example:
# --------
# ./build/Debug/fap.debug: rns rncwrapper

@rule(getExecutablePath(), ["rns", "rncwrapper"])
def makeExecutable2(target):
    pass

# Example:
# --------
# .PHONY: rns
# rns:
#     cd rns
#     make
#     cd ..

Phony("rns")
@rule("rns", None)
def makeRns(target):
    with cd("rns"):
        runShellCommand("make", verbose=True)

# Example:
# --------
# .PHONY: rncwrapper
# rncwrapper:
#     cd rrm/rncwrapper
#     make
#     cd ../..

Phony("rncwrapper")
@rule("rncwrapper", None)
def makeRncwrapper(target):
    with cd("rrm/rncwrapper"):
        runShellCommand("make", verbose=True)

# Example:
# --------
# (Repeat the following for each module name (oam, rrm, ...))
# .PHONY: oam
# oam: ./build/Debug/oam/liboam.a
# ...

[Phony(m) for m in list(modules)]
@rule(list(modules), getModuleOutputPath)
def makeModule(target):
    pass

# Example:
# --------
# (Repeat the following for each module name (oam, rrm, ...))
# .build/Debug/oam/liboam.a: .build/Debug/oam/oam.o \
#     .build/Debug/oam/dataModel.o ...

@cache
def getObjects2(_, moduleName):
    objects = []
    module = modules[moduleName]
    moduleDirectory = module.get("directory", moduleName)
    query = module.get("sourcefilter")
    sourceFiles = module.get("sourcefiles")
    def handleFile(absf):
        if query and not eval(query.replace("?", "absf")):
            return
        basePath, ext = os.path.splitext(absf)
        if not ext in (".c", ".cpp"):
            return
        objects.append(os.path.join(
            getActiveBuildPath(),
            basePath + ".o"))
    if sourceFiles:
        map(lambda f: handleFile(f), sourceFiles)
    else:
        for rootDir, subdirs, files in os.walk(moduleDirectory):
            for f in files:
                absf = os.path.join(rootDir, f)
                handleFile(absf)
    return objects

def getObjects1(moduleName):
    return getObjects2(None, moduleName)

for m in modules:
    @rule(getModuleOutputPath(m), getObjects2, m)
    def makeModule(target, moduleName):
        archive(objects=getObjects1(moduleName),
            archive=target)

# Example:
# --------
# .build/Debug/oam/app/src/appVersion.o: version_header

@rule(os.path.join(getActiveBuildPath(), "oam/app/src/appVersion.o"), "version_header")
def makeOamAppVersion(target):
    pass

# Example:
# --------
# Repeat the following for each object in each module:
# .build/Debug/oam/oam.o: oam/oam.c oam/oam.h soap/soap.h ...
#     gcc -o .build/Debug/oam/oam.o -c oam/oam.c ...

import string

@cache
def getDepends(objectFile, moduleName):
    dependPath = os.path.join(
        os.path.splitext(objectFile)[0] + ".d")
    if not os.path.exists(dependPath):
        return []
    with file(dependPath) as f:
        trans = string.maketrans('\\\n', '  ')
        _, _, d = (t.strip() for t in
            f.read().translate(trans).strip().partition(":"))
        return d.split()

for m in modules:
    @rule(getObjects1(m), getDepends, m)
    def makeObject(target, moduleName):
        config = configurations[activeConfiguration]
        module = modules[moduleName]
        cFlags = module.get("cflags", []) + config.get("cflags", [])
        defines = module.get("defines", []) + config.get("defines", [])
        includePaths = module.get("incpaths", ["."])
        dependentModules = module.get("depends"):
        if dependentModules:
            map(lambda m: includePaths.extend(modules[m].get("incpaths",
                [getModuleDirectory(m)])), dependentModules)
        includePaths += module.get("extincpaths", [])
        prefix = os.path.splitext(target)[0]
        depend = prefix + ".d"
        source = prefix.partition(
            getActiveBuildPath() + "/")[-1] + ".c"
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        buildObject(compiler=compiler,
            includePaths=includePaths,
            cFlags=config.get("cflags"),
            defines=defines,
            source=source,
            object=target)
        buildDepend(compiler=compiler,
            includePaths=includePaths,
            cFlags=config.get("cflags"),
            defines=defines,
            source=source,
            depend=depend)

# Example:
# --------
# .build/Debug/oam/app/src/appVersion.o: version_header
# .PHONY: version_header
# version_header:
#     touch oam/app/src/appVersion.c

import datetime

Phony("version_header")
@rule("version_header", None)
def makeVersionHeader(target):
    with file("oam/app/inc/version.h", "w") as f:
	f.write(
"""#ifndef VERSION_HEADER__
#define VERSION_HEADER__
#define FAP_BUILD_DATE "%(buildDate)s"
#define FAP_BUILD_USER "%(buildUser)s"
#endif  /* VERSION_HEADER__ */""" % {
	    "buildUser": os.getlogin(),
	    "buildDate": datetime.datetime.now()})

# Example:
# --------
# .PHONY: clean
# clean: clean_fap

Phony("clean")
@rule("clean", "clean_" + program)
def makeClean(target):
    pass

# Example:
# --------
# .PHONY: clean_fap
# clean_fap: clean_oam clean_rrm ...
#     rm .build/Debug/fap.debug
# clean_fap: clean_rns clean_rncwrapper

import shutil

Phony("clean_" + program)
@rule("clean_" + program, ["clean_" + m for m in list(modules)])
def makeCleanApp(target):
    runShellCommand(["rm", "-rf", getExecutablePath()], verbose=True)

@rule("clean_" + program, ["clean_rns", "clean_rncwrapper"])
def makeCleanApp2(target):
    pass

# Example:
# --------
# (Repeat the following for each module name (oam, rrm, ...))
# .PHONY: clean_oam
# clean_oam:
#     rm -rf .build/Debug/oam

for m in modules:
    Phony("clean_" + m)
    @rule("clean_" + m, None, m)
    def makeCleanModule(target, moduleName):
        runShellCommand(["rm", "-rf", os.path.join(
            getActiveBuildPath(), getModuleDirectory(moduleName))],
            verbose=True)

# Example:
# --------
# .PHONY: clean_rns
# clean_rns:
#     cd rns
#     make clean
#     cd ..

Phony("clean_rns")
@rule("clean_rns")
def makeCleanRns(target):
    with cd("rns"):
        runShellCommand("make clean", verbose=True)

# Example:
# --------
# .PHONY: clean_rncwrapper
# clean_rncwrapper:
#     cd rrm/rncwrapper
#     make clean
#     cd ../..

Phony("clean_rncwrapper")
@rule("clean_rncwrapper")
def makeCleanRncwrapper(target):
    with cd("rrm/rncwrapper"):
        runShellCommand("make clean", verbose=True)
