# 3IXAM

## Requirements

**Git (with Git-LFS ext), CMake, Xcode**

## Build

Firstly, clone this repository by command in terminal:

```
git clone https://github.com/3IXAMSOFTWARE/3ixam.git
```

Then you need to get libs from https://github.com/3IXAMSOFTWARE/3ixam_libs.git. You can clone it with installed Git-LFS extension and place next to 3ixam folder with name 'lib'.

```
mv <path to cloned libs>/3ixam_libs <path to dir with 3ixam repo>/lib
```

After that tou need to go into 3ixam folder:
```
cd <path to 3ixam repo>
```
Now you can generate Xcode project:
```
cmake . -B ../build_xcode/ -G 'Xcode'
```
And now you can open your project in Xcode and build it:
```
open ../build_xcode/3IXAM.xcodeproj
```
