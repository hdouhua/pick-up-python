# jupyter-test

JUlia + PYThon + R

to pick up python skill again

## setup runtime environment by annaconda

- setup jupyter or jupyter lab

- setup python env for special purpose with pyenv / conda env / mamba env

- setup ipy-kernel on the specific python env

   ```shell
   conda install -c conda-forge ipykernel

   ipython kernel install --user --name=<any_name_for_kernel>
   # or
   python -m ipykernel install --user --name=<any_name_for_kernel>
   ```

   list all kernel in jupyter

   ```shell
   jupyter kernelspec list
   ```

   delete some unwanted kernel

   ```shell
   jupyter kernelspec uninstall unwanted-kernel
   ```

- start jupyter notebook or lab, then pick up ipykernel

   ```shell
   jupyter notebook
   # or jupyter lab
   jupyter lab
   ```

other useful command, please refer to the [cheatsheet of conda](./res/conda-cheatsheet.pdf)

- to list jupyter runtime

   ```shell
   jupyter --version
   ```

- to support interactive UI, install ipywidgets, may need nodeJS

- to create environment by cloning base

   ```shell
   conda create --name fine --clone base
   ```

- to check the environment of conda

   ```shell
   conda info -e
   ```

- remove cached package tarballs

   ```shell
   conda clean --tarballs
   mmb clean --tarballs
   ```

## jupyter magic method

- [Built-in magic commands](https://ipython.readthedocs.io/en/stable/interactive/magics.html)
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

## jupyter shortcuts

- [Jupyter Notebook Keyboard Shortcuts](./res/jupyter-notebook-shortcuts.pdf)
- [28 Jupyter Notebook Tips, Tricks, and Shortcuts](https://www.dataquest.io/blog/jupyter-notebook-tips-tricks-shortcuts/)

## jupyter in cloud

mybinder URL: <https://mybinder.org/v2/gh/hdouhua/jupyter-test.git/master>
