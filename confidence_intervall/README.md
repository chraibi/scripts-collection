# Create fit of nearly orthogonal data

This script fits data as shown in Fig. 5 in
[this Paper](https://juser.fz-juelich.de/record/904621/).

The following actions are executed:

1. Turn data by some angle.
2. Fit turned data and calculate the error.
3. (optional) plot for each angle the resulting fit.
4. Return a plot of the optimal plot.

## Usage

```bash
python rotate_fit.py freesm1.txt vm1.txt --step 0.01
```

run with `--help` to see options.

## Requirements

Apart from some standard Python3 libraries this script uses

- [statsmodels](https://www.statsmodels.org/stable/index.html).

## Result

For the data in files [freesm1.txt](freesm1.txt) and [vm1.txt](vm1.txt).

we get the following results:

### Testing all possible angles

![result](result.gif)

### Optimal angle

![optimal angle](theta_1.76.png)
