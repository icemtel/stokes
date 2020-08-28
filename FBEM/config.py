## Options for the input.cnd file
# -------------
# Default contents of a cnd file:
#
# 1.0D-8	10 	10 	0 	1 	50 	1.0D-4	! eps, maxl, kmp, jscal, jpre, nrmax, tol
# 10	2	100	12500	12	7	1.005	! maxdep, mindep, maxepc, maxcel, nterm, ngauss, ratio
#
# Notes:
#
# ! eps        small real value [1.0d-8]
# ! maxl       [10]
# ! kmp        [maxl]
# ! jscal      [0]
# ! jpre       [1]
# ! nrmax      [10]
# ! tol        [1.0d-5]
# !
# ! maxdep     maximum tree depth (>= 2)
# ! mindep     minimum tree depth (usually 2)
# ! maxepc     maximum # of elements in a leaf
# ! maxcel     maximum # of cells
# ! nterm      truncated term of moments and local-coefs.
# ! ngauss     # of Gaussian abcissa for integrating moments (= 3, 7, or 16)
# ! ratio      greater than 1 [1.05d0]

default_values_dict = dict(eps=1.0E-8, maxl=10, kmp=10, jscal=0, jpre=1, nrmax=50, tol=1.0E-3,
                           maxdep=10, mindep=2, maxepc=100, maxcel=12500, nterm=12, ngauss=7, ratio=1.005)

