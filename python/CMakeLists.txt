cmake_minimum_required(VERSION 2.8)

include(RezBuild)

file(GLOB_RECURSE py_files "python/pepper/*.py")
rez_install_python(
    py
    FILES ${py_files}
    DESTINATION .
)

file(GLOB_RECURSE md_files "*.md")
rez_install_files(
    ${md_files}
    DESTINATION .
)

file(GLOB_RECURSE exec_files "bin/*")
rez_install_files(
    ${exec_files}
    DESTINATION .
)
