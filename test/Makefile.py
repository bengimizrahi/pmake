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

@cache
def getBuildDirectoryPath():
    return getRootDirectory() + buildDir

@cache
def getConfigurationBuildDirectoryPath(configName):
    p = getBuildDirectoryPath() + \
        configurations[configName]["buildsubdir"]
    if not os.path.exists(p):
        os.makedirs(p)
    return p

@cache
def getArchives():
    archives = [os.path.join(
        getConfigurationBuildDirectoryPath(activeConfiguration),
        getModuleDirectory(m))] for m in modules]
    return archives

@cache
def getObjectsOfModule(module):
    objects = []
    query = module.get["sourcefilter"]
    if query:
        query.replace("?", "absf")
    for rootDir, subdirs, files in os.walk(module["directory"]):
        for f in files:
            absf = os.path.join(rootDir, f)
            if query and not eval(query):
                continue
            objects.append(absf)
    return objects

@cache
def getSourceOfObject(objectFile):
    return os.path.splitext(objectFile)[0] + ".c"

@cache
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
    archives = getArchives()
    link(libraries=archives + libraries,
        libpaths=libraryPaths,
        executable=applicationName)

@rule(list(modules), getObjectsOfModule)
def makeModule(target):
    archive = os.path.join(
        getBuildConfigurationDirectoryPath(activeConfiguration),
        target, "lib%s.a" % target)
    archive(objects=getObjectsOfModule(target)
        archive=archive)

for m in modules:
    @rule(getObjectsOfModule(m), getDependsOfObject, m)
    def makeObject(target, module):
        prefix = os.path.splitext(target)[0]
        source, depend = (prefix + ext for ext in (".c", ".d"))
        compilee(compiler=compiler,
            includePaths=module["incpaths"],
            source=source,
            object=target)
        makeDepend(compiler=compiler,
            includePaths=module["incpaths"],
            source=source,
            depend=depend)

# Rules for cleaning
@rule(Phony("clean"), "clean_" + applicationName)
def makeClean(target):
    pass

@rule(Phony("clean_" + applicationName),
    ["clean_" + m for m in list(modules)])
def makeCleanApp(target):
    os.remove(os.path.join(
        getBuildConfigurationDirectoryPath(activeConfiguration), 
        applicationName))

for m in modules:
    @rule(Phony("clean_" + m), None, m)
    def makeCleanModule(target, module):
        shutil.rmtree(os.path.join(
            getBuildConfigurationDirectoryPath(activeConfiguration),
            getModuleDirectory()))
