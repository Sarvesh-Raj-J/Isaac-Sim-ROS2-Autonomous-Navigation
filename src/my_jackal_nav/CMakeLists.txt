cmake_minimum_required(VERSION 3.8)
project(my_jackal_nav)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch maps config urdf
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

