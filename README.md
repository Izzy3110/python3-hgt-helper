# python3-hgt-helper

## Description
if you only need a few files out of a thousand (and on a network storage) it can easily turn into a long-running hardcore waiting action.
You can use this tool to first generate an index(json) and then download them files to a target path.

`
This is actually shorter than the following steps:
- look if file is online there? (looooooong waiting till finished)
- download if it is not local
- repeat every program-execution
`

These three steps take a much load of time, so i decided to shorten it up, since the directory content is not changing or is planned to be changed so far.



##### TODO:
- file checksum
- (proxified) http downloads


### Author: Sascha Frank