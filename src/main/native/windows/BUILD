package(default_visibility = ["//visibility:private"])

exports_files(
    ["resources.o"],
    visibility = ["//src/main/cpp:__pkg__"],
)

filegroup(
    name = "srcs",
    srcs = glob(["**"]),
    visibility = ["//src/main/native:__pkg__"],
)

filegroup(
    name = "cc-srcs",
    srcs = glob([
        "*.cc",
        "*.h",
    ]),
)

filegroup(
    name = "embedded_tools",
    srcs = [
        "BUILD",
        ":cc-srcs",
    ],
    visibility = ["//src/main/native:__pkg__"],
)

cc_library(
    name = "lib-file",
    srcs = ["file.cc"],
    hdrs = ["file.h"],
    visibility = [
        "//src/main/cpp:__subpackages__",
        "//src/test/cpp:__subpackages__",
        "//src/test/native:__subpackages__",
        "//tools/test:__pkg__",
    ],
    deps = [":lib-util"],
)

cc_library(
    name = "lib-util",
    srcs = ["util.cc"],
    hdrs = ["util.h"],
)

cc_binary(
    name = "windows_jni.dll",
    srcs = [
        ":cc-srcs",
        "//src/main/native:jni.h",
        "//src/main/native:jni_md.h",
    ],
    linkshared = 1,
    visibility = [
        "//src:__pkg__",
        "//src/test/java/com/google/devtools/build/lib:__subpackages__",
        "//src/tools/android/java/com/google/devtools/build/android:__subpackages__",
    ],
)
