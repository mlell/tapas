---
title:
- Dependencies of the scripts
---

Dependencies of the scripts
===========================

The scripts consisting this software depend on 

  * A Python 3 installation
  * R

Furthermore, the scripts depend on several packages for R and Python.

To check whether all dependencies are met, execute the following
command. It is included in the `scripts/` folder.

```
scripts/setup_check_dependencies
```

Check the output of this script to find package names which are not
installed or can't be loaded because of eventual errors.

Then install these packages manually by using 

Install packages for R
----------------------

Install missing packages in R by executing the following command
inside the R command prompt (type `R` into your shell to invoke it)

```{.r}
install.packages("PACKAGENAME")
```

Install packages for Python
---------------------------

Invoke the Python package manager `pip3` to install packages for
Python:

```
pip3 install PACKAGENAME...
```

You may specify multiple package names by writing them one after
another, separated by whitespace.



