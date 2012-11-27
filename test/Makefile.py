enableColor = True
compiler = "gcc"
linker = "gcc"
ar = "ar"
commonCflags = ["-O3", "-Wall",]
ldFlags = ["-Xlinker", "--start-group"]
buildDir = ".build"
activeConfiguration = "debug"
configurations = {
    "debug" : {
        "flags" : commonCflags + ["-g"],
        "buildsubdir" : "Debug",
    },
    "release" : {
        "flags" : commonCflags,
        "buildsubdir" : "Release",
    },
}
libraryPaths = []
libraries = []
modules = {
    "app" : {
	"incpaths" : ["rrm", "son", "oam"]},
    "rrm" : {
	"incpaths" : ["phy"]},
    "son" : {
	"incpaths" : ["phy", "rrm"]},
    "http" : {},
    "oam" : {
	"incpaths" : ["soap"]},
    "phy" : {},
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

@rule(Phony("all"), program)
def makeAll(target):
    pass

# Example:
# --------
# .PHONY: fap
# fap: ./build/Debug/fap.debug

@rule(Phony(program), getExecutablePath())
def makeProgram(target):
    runShellCommand(["cp", getExecutablePath(), "."])

# Example:
# --------
# ./build/Debug/fap.debug: ./build/Debug/oam/liboam.a \
#     ./build/Debug/rrm/librrm.a ...

@cache
def getModuleOutputPath(moduleName):
    return os.path.join(
	getActiveBuildPath(), getModuleDirectory(moduleName), "lib%s.a" %
	moduleName)


@rule(getExecutablePath(), [getModuleOutputPath(m) for m in list(modules)])
def makeExecutable(target):
    moduleOutputDirs = [os.path.join(getActiveBuildPath(),
	getModuleDirectory(m)) for m in modules]
    rt = link(
	libpaths=libraryPaths + moduleOutputDirs,
	libraries=libraries + list(modules),
	executable=getExecutablePath())
    if rt: return rt

# Example:
# --------
# (Repeat the following for each module name (oam, rrm, ...))
# .PHONY: oam
# oam: ./build/Debug/oam/liboam.a
# ...

@rule([Phony(m) for m in list(modules)], getModuleOutputPath)
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
    if query:
        query.replace("?", "absf")
    for rootDir, subdirs, files in os.walk(moduleDirectory):
        for f in files:
            absf = os.path.join(rootDir, f)
            if query and not eval(query):
                continue
	    basePath, ext = os.path.splitext(absf)
	    if not ext in (".c", ".cpp"):
		continue
            objects.append(os.path.join(
		getActiveBuildPath(),
		basePath + ".o"))
    return objects

def getObjects1(moduleName):
    return getObjects2(None, moduleName)

for m in modules:
    @rule(getModuleOutputPath(m), getObjects2, m)
    def makeModule(target, moduleName):
	rt = archive(objects=getObjects1(moduleName),
	    archive=target)
	if rt: return rt

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
	module = modules[moduleName]
        prefix = os.path.splitext(target)[0]
	depend = prefix + ".d"
	source = prefix.partition(
	    getActiveBuildPath() + "/")[-1] + ".c"
	if not os.path.exists(os.path.dirname(target)):
	    os.makedirs(os.path.dirname(target))
        rt = buildObject(compiler=compiler,
            includePaths=module.get("incpaths"),
            source=source,
            object=target)
	if rt: return rt
        rt = buildDepend(compiler=compiler,
            includePaths=module.get("incpaths"),
            source=source,
            depend=depend)
	if rt: return rt

# Example:
# --------
# .PHONY: clean
# clean: clean_fap

@rule(Phony("clean"), "clean_" + program)
def makeClean(target):
    pass

# Example:
# --------
# .PHONY: clean_fap
# clean_fap: clean_oam clean_rrm ...
#     rm .build/Debug/fap.debug

import shutil

@rule(Phony("clean_" + program),
    ["clean_" + m for m in list(modules)])
def makeCleanApp(target):
    rt = runShellCommand(["rm", "-rf", getExecutablePath()], verbose=True)
    if rt: return rt

# Example:
# --------
# (Repeat the following for each module name (oam, rrm, ...))
# .PHONY: clean_oam
# clean_oam:
#     rm -rf .build/Debug/oam

for m in modules:
    @rule(Phony("clean_" + m), None, m)
    def makeCleanModule(target, moduleName):
	rt = runShellCommand(["rm", "-rf", os.path.join(
	    getActiveBuildPath(), getModuleDirectory(moduleName))],
	    verbose=True)
	if rt: return rt
