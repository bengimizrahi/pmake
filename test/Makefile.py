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
applicationName = "fap." + activeConfiguration

@cache
def getModuleDirectory(moduleName):
    return modules.get("directory", moduleName)

@cache
def getBuildConfigurationDirectoryPath(configName):
    p = os.path.join(buildDir,
        configurations[configName]["buildsubdir"])
    if not os.path.exists(p):
        os.makedirs(p)
    return p

@cache
def getArchivePaths():
    archives = [os.path.join(
        getBuildConfigurationDirectoryPath(activeConfiguration),
        getModuleDirectory(m)) for m in modules]
    return archives

@cache
def getObjectsOfModule(moduleName):
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
	    basename, ext = os.path.splitext(absf)
	    if not ext in (".c", ".cpp"):
		continue
            objects.append(basename + ".o")
    return objects

@cache
def getSourceOfObject(objectFile):
    return os.path.splitext(objectFile)[0] + ".c"

@cache
def getDependsOfObject(objectFile):
    dependPath = os.path.join(
        getBuildConfigurationDirectoryPath(activeConfiguration),
        os.path.splitext(objectFile)[0] + ".d")
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

@rule(applicationName, list(modules))
def makeApp(target):
    archivePaths = getArchivePaths()
    exePath = os.path.join(
	getBuildConfigurationDirectoryPath(activeConfiguration), applicationName)
    rt = link(libraries=list(modules) + libraries,
        libpaths=archivePaths + libraryPaths,
        executable=exePath)
    if rt: return rt
    runShellCommand(["cp", exePath, "."], verbose=True)

@rule([Phony(m) for m in list(modules)], getObjectsOfModule)
def makeModule(target):
    archiveFile = os.path.join(
        getBuildConfigurationDirectoryPath(activeConfiguration),
        target, "lib%s.a" % target)
    obj = map(lambda o: os.path.join(
	getBuildConfigurationDirectoryPath(activeConfiguration), o),
	getObjectsOfModule(target))
    rt = archive(objects=obj,
        archive=archiveFile)
    if rt: return rt

for m in modules:
    @rule(getObjectsOfModule(m), getDependsOfObject, m)
    def makeObject(target, moduleName):
	module = modules[moduleName]
        prefix = os.path.splitext(target)[0]
        source, depend = (prefix + ext for ext in (".c", ".d"))
	obj = os.path.join(
	    getBuildConfigurationDirectoryPath(activeConfiguration), target)
	if not os.path.exists(os.path.dirname(obj)):
	    os.makedirs(os.path.dirname(obj))
        rt = compilee(compiler=compiler,
            includePaths=module.get("incpaths"),
            source=source,
            object=obj)
	if rt: return rt
        rt = makeDepend(compiler=compiler,
            includePaths=module.get("incpaths"),
            source=source,
            depend=depend)
	if rt: return rt

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
