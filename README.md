# jupyter-test

JUlia + PYThon + R

to pick up python skill again

## setup runtime environment by annaconda

please refer to the [cheatsheet of conda](./conda-cheatsheet.pdf)

- to create environment by cloning base

   ```shell
   conda create --name fine --clone base
   ```

- to check the environment of conda

   ```shell
   conda info -e
   ```

- start jupyter

   ```shell
   jupyter lab
   ```

## jupyter in cloud

mybinder URL: <https://mybinder.org/v2/gh/hdouhua/jupyter-test.git/master>

## jupyter magic method

<https://ipython.readthedocs.io/en/stable/interactive/magics.html>
<https://www.dataquest.io/blog/jupyter-notebook-tips-tricks-shortcuts/>

- %env
- %run
- %load
- %store
- %%time
- %timeit
- %%writefile
- %pycat
- %prun
- %pdb
