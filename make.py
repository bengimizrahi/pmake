#!/usr/bin/python

# Author: Bengi Mizrahi
# Date: 05.06.2012

from common import cache, COLORS
import sys
import imp
import os
import shutil

if __name__ == "__main__":

    # Get the target
    target = "all"
    if len(sys.argv) == 2:
        target = sys.argv[1]

    # Import makefile.py
    try:
        with file("Makefile.py") as f:
            exec(f.read())
    except IOError:
        print "Error: No such file: Makefile.py"
        exit(1)

    # If BUILD_DIR does not exist, create it.
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    # Check if desired configuration exists
    activeConfiguration = CONFIGURATIONS.get(ACTIVE_CONFIGURATION)
    if not activeConfiguration:
        print "Error: ACTIVE_CONFIGURATION(%s) not found in CONFIGURATIONS(%s)" % (
            activeConfiguration,
            ", ".join(CONFIGURATIONS.keys()))
        exit(1)

    # Check if desired configuration is valid
    requiredConfigurationParameters = ["buildsubdir"]
    if any(map(lambda p: activeConfiguration.get(p) is None,
            requiredConfigurationParameters)):
        print "Error: One or more required parameters are missing. The " \
              "following parameters are required: %s." % \
              ", ".join(requiredConfigurationParameters)
        exit(1)

    # Get the active configuration build sub directory
    acBuildDirectory = os.path.join(BUILD_DIR,
        activeConfiguration["buildsubdir"])

    # Clean the active configuration build sub directory
    # if target == "clean"
    if target == "clean":
        print "%sClean %s%s" % (COLORS["blue"],
            acBuildDirectory, COLORS["default"])
        try:
            shutil.rmtree(acBuildDirectory)
        except OSError:
            pass
        exit(0)

    # Create the active configuration build sub directory
    if not os.path.exists(acBuildDirectory):
        os.makedirs(acBuildDirectory)

    # Check if desired modules exists
    for moduleName in ACTIVE_MODULES:
        if not MODULES.get(moduleName):
            print "Error: No module named %s found in MODULES."
            exit(1)
    activeModules = dict(filter(lambda m: m[0] in ACTIVE_MODULES,
        MODULES.iteritems()))

    # Check if desired modules are valid
    requiredModuleParameters = ["directory", "language"]
    for name, module in activeModules.iteritems():
        for p in requiredModuleParameters:
            if not module.get(p):
                print "Error: Module %s misses parameter: %s" % (name, p)
                exit(1)

    # Build each active module
    archiveFiles = list()
    atLeastOneArchiveFileCreated = False
    for name, module in activeModules.iteritems():

        # Create module build directory
        moduleBuildDirectory = os.path.join(acBuildDirectory,
            module["directory"])
        if not os.path.exists(moduleBuildDirectory):
            os.makedirs(moduleBuildDirectory)

        # List all source files
        sourceDirectory = module["directory"]
        sourceFileExtensions = LANGUAGE_SETTINGS[module["language"]]["sourceext"]
        sourceFiles = filter(lambda f: any(map(lambda e: f.endswith(e),
            sourceFileExtensions)), os.listdir(sourceDirectory))

        # Compile each source file
        def createObjectFile():
            cmd = " ".join((
                compiler,
                " ".join(activeConfiguration["flags"]),
                " ".join(module["defines"]),
                " ".join(("-I%s" % i for i in module["incpaths"])),
                "-c",
                sourceFilePath,
                "-o",
                objectFilePath))
            print "%sCompile:%s %s%s%s" % (
                COLORS["blue"], COLORS["default"],
                COLORS["yellow"], sourceFilePath, COLORS["default"])
            print "%s%s%s" % (COLORS["white"], cmd, COLORS["default"])
            rt = os.system(cmd)
            if rt:
                print "%sError:%smake.py exited with error code %d" % (
                    COLORS["red"], COLORS["default"], rt)
                exit(rt)
        def createDependencyFile():
            cmd = " ".join((
                compiler,
                "-MM",
                " ".join(activeConfiguration["flags"]),
                " ".join(module["defines"]),
                " ".join(("-I%s" % i for i in module["incpaths"])),
                sourceFilePath,
                "-o",
                dependFilePath))
            rt = os.system(cmd)
            if rt:
                print "%sError:%smake.py exited with error code %d" % (
                    COLORS["red"], COLORS["default"], rt)
                exit(rt)
        def modifyTime(filename):
            return os.path.getmtime(filename)
        def anyDirtyFileInDependencyFile():
            try:
                with file(dependFilePath) as depend:
                    t1, _, t2 = (t.strip() for t in
                        depend.read().strip().partition(":"))
                    obj, deps = os.path.join(moduleBuildDirectory, t1), t2.split()
                    dirtyFiles = filter(lambda d: modifyTime(d) > modifyTime(obj),
                        deps)
                    if dirtyFiles:
                        print "%sDep: %s%s%s%s <- %s" % (
                            COLORS["blue"], COLORS["default"],
                            COLORS["yellow"], obj, COLORS["default"],
                             ", ".join(dirtyFiles))
                    return bool(dirtyFiles)
            except IOError:
                print "File %s not found" % dependFilePath
                return True
        (NO_OBJECT_FILE_FOUND,
         DEPENDENCIES_ARE_RECENT_THAN_OBJECT_FILE,
         OBJECT_FILE_IS_THE_MOST_RECENT) = range(3)
        compiler = LANGUAGE_SETTINGS[module["language"]]["compiler"]
        atLeastOneObjectFileCreated = False
        moduleObjectFiles = list()
        for sourceFile in sourceFiles:
            extension = filter(lambda e: sourceFile.endswith(e),
                sourceFileExtensions).pop()
            sourceFileLeftSide = sourceFile.rstrip(extension)
            sourceFilePath = os.path.join(sourceDirectory, sourceFile)
            objectFilePath = "%s/%s.o" % (moduleBuildDirectory,
                sourceFileLeftSide)
            moduleObjectFiles.append(objectFilePath)
            dependFilePath = "%s/%s.d" % (moduleBuildDirectory,
                sourceFileLeftSide)
            if not os.path.exists(objectFilePath):
                condition = NO_OBJECT_FILE_FOUND
            elif anyDirtyFileInDependencyFile():
                condition = DEPENDENCIES_ARE_RECENT_THAN_OBJECT_FILE
            else:
                condition = OBJECT_FILE_IS_THE_MOST_RECENT
            if condition != OBJECT_FILE_IS_THE_MOST_RECENT:
                createObjectFile()
                atLeastOneObjectFileCreated = True
                createDependencyFile()

        # Create library for the module
        libFilePath = os.path.join(acBuildDirectory, "lib%s.a" % name)
        archiveFiles.append(libFilePath)
        if not os.path.exists(libFilePath) or any(
                map(lambda o: modifyTime(libFilePath) < modifyTime(o),
                    moduleObjectFiles)):
            print "%sArchive:%s %s%s%s" % (
                COLORS["magenda"], COLORS["default"],
                COLORS["yellow"], libFilePath, COLORS["default"])
            objects = " ".join(moduleObjectFiles)
            cmd = " ".join((
                "%sar" % CROSS_COMPILE,
                "cr",
                libFilePath,
                objects
            ))
            print "%s%s%s" % (COLORS["white"], cmd, COLORS["default"])
            rt = os.system(cmd)
            if rt:
                print "%sError:make.py exited with error code %d%s" % (
                    COLORS["red"], rt, COLORS["default"])
                exit(rt)
            atLeastOneArchiveFileCreated = True

    # Link all object files
    targetFilePath = os.path.join(acBuildDirectory,
        APPLICATION_NAME)
    if not os.path.exists(targetFilePath) or \
            atLeastOneArchiveFileCreated or \
            any(map(lambda a: modifyTime(targetFilePath) < modifyTime(a),
                archiveFiles)):
        print "%sLink:%s %s%s%s" % (COLORS["green"], COLORS["default"],
            COLORS["yellow"], targetFilePath, COLORS["default"])
        allLibraryPaths = LIBRARY_PATHS + map(
            lambda n: os.path.join(acBuildDirectory,
                MODULES[n]["directory"]), ACTIVE_MODULES)
        allLibraries = LIBRARIES + ACTIVE_MODULES
        cmd = " ".join((
            LINKER,
            " ".join(LDFLAGS),
            " ".join(("-L%s" % d for d in allLibraryPaths)),
            " ".join(("-l%s" % l for l in allLibraries)),
            "-o",
            targetFilePath
        ))
        print "%s%s%s" % (COLORS["white"], cmd, COLORS["default"])
        rt = os.system(cmd)
        if rt:
            print "%sError:%smake.py exited with error code %d" % (
                COLORS["red"], COLORS["default"], rt)
            exit(rt)
        shutil.copy(targetFilePath, APPLICATION_NAME)
