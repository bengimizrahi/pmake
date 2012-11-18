COLOR = True

COMPILER = "g++"
LINKER = "g++"
COMMON_CFLAGS = ["-O3", "-Wall",]
LDFLAGS = ["-Xlinker", "--start-group"]

BUILD_DIR = ".build"

ACTIVE_CONFIGURATION = "debug"
CONFIGURATIONS = {
    "debug" : {
	"flags" : COMMON_CFLAGS + ["-g"],
	"buildsubdir" : "Debug",
    },
    "release" : {
	"flags" : COMMON_CFLAGS,
	"buildsubdir" : "Release",
    },
}

LIBRARY_PATHS = []
LIBRARIES = []

MODULES = {
    "main" : {
        "incpaths" : ["system"],
        "defines" : [],
    },
    "system" : {
        "incpaths" : [],
        "defines" : [],
    },
}

APPLICATION_NAME = "fap." + ACTIVE_CONFIGURATION


# Rules for building

@rule("all", APPLICATION_NAME)
def makeAll(target):
    pass

@rule(APPLICATION_NAME, list(MODULES))
def makeApp(target):
    pass

@rule(list(MODULES), getObjectsByModule)
def makeModule(target):
    pass

for module in MODULES:
    @rule(getObjectsByModule(module), getSourceByObject)
    def makeObject(target):
        pass

for module in MODULES:
    @rule(getSourcesByModule(module), getDependsBySource)
    def makeDepends(target):
        pass


# Rules for cleaning

@rule("clean", "clean_" + APPLICATION_NAME)
def makeClean(target):
    pass

@rule("clean_" + APPLICATION_NAME, ["clean_" + m for m in MODULE.keys()])
def makeCleanApp(target):
    pass

@rule(["clean_" + m for m in MODULE.keys()])
def makeCleanModule(target):
    pass
