cmake_minimum_required(VERSION 2.8)

include(RezBuild)

file(GLOB_RECURSE py_files "python/BlackPepper/*.py")
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

file(GLOB_RECURSE img_files "*.png")
rez_install_files(
    ${img_files}
    DESTINATION .
)

file(GLOB_RECURSE ui_files "*.ui")
rez_install_files(
    ${ui_files}
    DESTINATION .
)



