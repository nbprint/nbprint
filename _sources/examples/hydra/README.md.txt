# Running `nbprint` with [hydra](https://hydra.cc)

[hydra](https://hydra.cc) is a powerful tool for configuration management, and it pairs very well with `nbprint`.
In this folder, we break out our configuration into a few more mangement sections. In particular, we configure our page
in [page/report.yaml](./page/report.yaml), and we configure two sets of parameters in [parameters](./parameters/).

This lets use easily run our same report with different layours or inputs:

```bash
# Parameter set 1
nbprint hydra examples/hydra.yaml config=inline page=report parameters=string1

# Parameter set 2
nbprint hydra examples/hydra config=inline page=report parameters=string1
```
