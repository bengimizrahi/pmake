enableColor = True
compiler = "g++"
linker = "g++"
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
	"incpaths" : ["phy"]},
    "http" : {},
    "oam" : {
	"incpaths" : ["soap"]},
    "phy" : {},
}
applicationName = "fap." + activeConfiguration

def getBuildDirectoryPath():
    return getRootDirectory() + buildDir

@cache
def getConfigurationBuildDirectoryPath(configName):
    return getBuildDirectoryPath() + \
        configurations[configName]["buildsubdir"]

def getObjectsOfModule(module, filterQuery=None):
    objects = []
    if filterQuery:
        filterQuery.replace("?", "absf")
    for rootDir, subdirs, files in os.walk(module["directory"]):
        for f in files:
            absf = os.path.join(rootDir, f)
            if filterQuery and not eval(filterQuery):
                continue
            objects.append(absf)
    return objects

def getSourceOfObject(objectFile):
    return os.path.splitext(objectFile)[0] + ".c"

def getDependsOfObject(source):
    dependPath = os.path.join(
        getConfigurationBuildDirectoryPath(activeConfiguration),
        os.path.splitext(source)[0] + ".d")
    if not os.path.exists(dependPath):
        return []
    with file(dependPath) as f:
        trans = string.maketrans('\\\n', '  ')
        _, _, d = (t.strip() for t in
            f.read().translate(trans).strip().partition(":"))
        return d.split()

# Rules for building
@rule(Phony("all"), applicationName)
def makeAll(target):
    pass

@rule(applicationName, [Phony(m) for m in list(modules))
def makeApp(target):
    pass

@rule(list(modules), getObjectsOfModule)
def makeModule(target):
    archive = os.path.join(
        getBuildConfigurationDirectoryPath(activeConfiguration),
        target, "lib%s.a" % target)
    link(linker=linker,
        objects=getObjectsOfModule(target)
        archive=archive)

for m in modules:
    @rule(getObjectsOfModule(m), getDependsOfObject, m)
    def makeObject(target, m):
        prefix = os.path.splitext(target)[0]
        source = prefix + ".c"
        compilee(compiler=compiler,
            includePaths=m["incpaths"],
            source=source,
            object=target)
        depend = prefix + ".d"
        makeDepend(compiler=compiler,
            includePaths=m["incpaths"],
            source=source,
            depend=depend)

# Rules for cleaning
@rule("clean", "clean_" + applicationName)
def makeClean(target):
    pass

@rule("clean_" + applicationName,
    ["clean_" + m for m in list(modules)])
def makeCleanApp(target):
    pass

@rule(["clean_" + m for m in list(modules)])
def makeCleanModule(target):
    pass