
from os.path import isdir, join , isfile
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-asf4")
assert isdir(FRAMEWORK_DIR)


def get_startup_file():
    
    search_path = join(
        FRAMEWORK_DIR, "samd21a", "gcc", "gcc", "startup_samd21.c"
    )


    startup_file = glob(search_path)

    if not startup_file:
        sys.stderr.write(
            """Error: There is no default startup file for MCU!
            Please add initialization code to your project manually!""" )
        env.Exit(1)
    return startup_file

linker_script = join(FRAMEWORK_DIR, "samd21a", "gcc", "gcc", "samd21g18a_flash.ld")
   


def get_linker_script(script_name, ldscript):
    
    ram = env.BoardConfig().get("upload.maximum_ram_size", 0)
    flash = env.BoardConfig().get("upload.maximum_size", 0)
    content = ""
    with open(ldscript) as fp:
        content = fp.read()
        # original:     rom      (rx)  : ORIGIN = 0x00000000, LENGTH = 0x00040000
        # transformed:  rom      (rx)  : ORIGIN = 0x00000000+0x2000, LENGTH = 0x00040000-0x2000
        content = re.sub(
            ram=str(int(ram/1024)) + "K",
            flash=str(int(flash/1024)) + "K"
        )

    offset_script = os.path.join(BUILD_DIR, "%s_flash.ld" % (script_name))

    with open(offset_script, "w") as fp:
        fp.write(content)

    return offset_script

linker_script = get_linker_script(env.subst('$PIOENV'), linker_script)
env.Replace(LDSCRIPT_PATH=linker_script)




env.Append(
   
    CCFLAGS=[
        "-mthumb",
        "-mcpu=%s" % board.get("build.cpu"),
    ],
    CPPDEFINES=[
                ("F_CPU", "$BOARD_F_CPU"),
                "USBCON",
                "PLATFORMIO=50205",
                "__SAMD21J18A__",
                ""
            ],
    CPPPATH=[
        join(FRAMEWORK_DIR, "hal", "include"),
        join(FRAMEWORK_DIR, "hal", "utils", "include"),
        join(FRAMEWORK_DIR, "CMSIS", "Core", "Include"),
        join(FRAMEWORK_DIR, "samd21a", "include"),

        join(FRAMEWORK_DIR, "hpl", "core"),
        join(FRAMEWORK_DIR),
        join(FRAMEWORK_DIR, "config"),

        join(FRAMEWORK_DIR, "hpl", "gclk"),
        join(FRAMEWORK_DIR, "hpl", "pm"),
        join(FRAMEWORK_DIR, "hpl", "pore"),
        join(FRAMEWORK_DIR, "hri"),
    ],
    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions"
    ],
     LINKFLAGS=[
        "-mthumb",
        "-mcpu=%s" % board.get("build.cpu")
    ],
    

    LIBPATH=[
        join(FRAMEWORK_DIR),
    
        join(FRAMEWORK_DIR, "samd21a", "gcc", "gcc"),
    ]
             
)    

#
# Target: Build Core Library
#

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "frameworkAsf4"),    
))

env.Append(LIBS=libs)
