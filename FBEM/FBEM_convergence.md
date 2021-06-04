These are my technical notes [from 2020-09] on internal parameters of FBEM and how the affect convergence.
No warranty. Use them at your own risk!

# Convergence

Issue : many simulations converge in ~30 iterations, but some stagnate, and can't converge in 500.

Mesh improvement:
- Consistently better with finer cilium mesh: 60x8 grid
- Cilium radius to r=0.125: r=0.11 => 6% out of 100 fail in a test.
- Cilium elevation: set to 0.25. Could go higher?

FBEM/GMRES improvement
- **jpre->2 maxl->30** (but could be bigger)
- kmp, jscal - neutral to convergence

- Adjusting `jpre` and `maxl` makes convergence faster
  when it would most likely converge either way.
  But when it doesn't converge, changing `jpre` and `maxl` doesn't help!

- **ratio->1.15** => almost all converged
- For those which have not converged, changing ratio->1.05 helped.

# GMRES and FBEM parameters
- we need to save all the old vectors -> that's why reset => inner and outer iterations


### jscal
- jscal:  "A flag indicating whether arrays SR and SZ are used.": http://www.lahey.com/docs/lgf13help/slatec/SXLCAL.htm
- jscal=0,1,2,3: doesn't make any difference

### jpre
- jpre:  "The preconditioner type flag": http://www.lahey.com/docs/lgf13help/slatec/SXLCAL.htm
- jpre=0,1,2,3: 2 - evidently fastest convergence
- jpre=4 - is not supported
- Hypothesis: `jpre=2` means no pre-conditioner (in output error estimates `bePRE` and `beUNPRE` are the same)`


### maxl
- MAXL = number of inner iterations before restart
- TESTS: higher MAXL - faster convergence;
- more memory is needed; but it wasn't critical


### nrmax
- NRMAX - maximum number of outer iterations
- total number of iterations: maxl * nres

### kmp
- tuning doesn't influence number of iterations
- KMP could stand for Krylov Minimization / Projection


### maxepc
- max number of elements in the leaf


### FBEM parameters 
(I think this is FMM parameters, rather than GMRES)

ngauss
- ngauss=3 & ratio=1.05 => faster and better convergence
- Longer test: ngauss=7.16 => did not influence convergence (or very small influence compared with `ratio` influence)


ratio
- ratio: 1.005->1.15 => better convergence
- not found this parameter in the FBEM book
- ratio: 1.15->1.5 - takes more time to compute with approx. equal number of iterations
- Longer test: ratio=1.15 - OK, ratio=1.5 -> failed some
- varying ratio may help fixing the convergence problems.
- ! changing ratio changes forces output => it could be some regularization parameter
  - However, resulting g11 and g12 change is around 1e-4 and 1e-3 respectively (tested only a few phases)

maxdep 
- maxdep: 10->20 => no change


---
Ref:
- notebooks `try03#`
- computation scripts `2020-09-02_cilia_explore_parameters`, `2020-09-07_cilia_explore_parameters2/FBEM_run_failed2.py`, `2020-09-07_cilia_explore_parameters2/FBEM_run_random4.py`
