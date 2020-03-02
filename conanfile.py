from conans import ConanFile,AutoToolsBuildEnvironment,tools
from conans.tools import download, unzip


class GperfToolsConan(ConanFile):
    name = "gperftools"
    description = "The fastest malloc we have seen."
    version = "2.7"
    options = { "shared":[True, False], 
                "cpuprof":[True, False], 
                "heapprof":[True, False], 
                "heapchecker":[True, False]
                }
    default_options = "shared=True", "cpuprof=False", "heapprof=False", "heapchecker=False"
    url = "https://github.com/gperftools/gperftools"
    license = "https://github.com/gperftools/gperftools/blob/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    def requirements(self):

        if self.settings.os == 'Macos':
            self.options.cpuprof = self.options.heapprof = self.options.heapchecker = False
            print("!!!!!    libunwind is not supported on MacOS, disabling all associated functionality.    !!!!!")

        if self.options.cpuprof or self.options.heapprof or self.options.heapchecker:
            self.requires("libunwind/1.3.1@bincrafters/stable")

    def source(self):
         zip_name = "gperftools-%s.zip" % self.version 

         download( "https://github.com/gperftools/gperftools/releases/download/gperftools-%s/%s" %(self.version,zip_name),zip_name)
         unzip(zip_name)

         tools.replace_in_file("%s/configure" % ("gperftools-%s" % self.version), r"-install_name \$rpath/", "-install_name @rpath/" )
         self.run("chmod +x ./%s/configure" % ("gperftools-%s" % self.version))
         self.run("chmod +x ./%s/install-sh" % ("gperftools-%s" % self.version))

    def build(self):
        with tools.chdir("gperftools-%s" % self.version):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure( 
                                 args = [ "" if self.options.cpuprof or self.options.heapprof or self.options.heapchecker else "--enable-minimal",
                                         "--enable-shared" if self.options.shared else "--disable-shared",
                                         "--enable-static" if not self.options.shared else "--disable-static",
                                         "--enable-cpu-profiler" if self.options.cpuprof else "--disable-cpu-profiler",
                                         "--enable-heap-profiler" if self.options.heapprof else "--disable-heap-profiler",
                                         "--enable-heap-checker" if self.options.heapchecker else "--disable-heap-checker" ])
            env_build.make()
    

    def package_info(self):
        if self.options.cpuprof or self.options.heapprof or self.options.heapchecker:
            self.cpp_info.libs = ["tcmalloc"]
        else:
            self.cpp_info.libs = ["tcmalloc_minimal"]


    def package(self):
        with tools.chdir("gperftools-%s" % self.version):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.install()




