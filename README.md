# Presentation

Cygen is an independent project that aims to simplify the integration of **cython** inside of c++ projects.
It is an executable that aims to generate the `.pyx` and `.pxd` based on your `.cpp` files.

# Requirements

The requirements can be found in the `env.yml` file.

You can create a conda environment for this project using:

```sh
conda env create -n cygen -f env.yml # replace cygen by your env name
```

# Installation

You can install cygen using:
```sh
$ git clone https://github.com/Frayzen/Cygen
$ cd Cygen
$ pip install .
```

# Usage

```
$ 
usage: cygen [-o directory] [-p] [-v|-vv] [-s] files...
cygen: error: the following arguments are required: files
```

# Related content

- [Cython](http://cython.org)
- [TreeSitter](https://github.com/Frayzen/Cygen)
