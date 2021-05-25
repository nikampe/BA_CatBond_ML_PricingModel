Machine Learning-Enhanced Pricing in the Secondary Market for Cat Bonds

This README-file provides an overview in order to let the full code run. Please follow the step-by-step introduction below.

1. Start the Virtual Environment

1.1 Open the terminal or open project in the text editor of your choice (recommended: Visual Studio Code)
1.2 Navigate to BA_CatBond_ML_PricingModel/Code/virtual_environment in the terminal
1.3 Activate the virtual environment through the command „source env/bin/activate“
1.4 Navigate back to BA_CatBond_ML_PricingModel/ in order to set the correct file path for the indirect paths in the code

2. Run the Code Files

2.1 Use the text editor of your choice in order to run the files (or directly from the terminal) (recommended: Visual Studio Code)
2.2 Run import.py (processing time: 1min)
2.3 Run cleaning.py (processing time: 30min)
2.4 Run merging.py (processing time: 2min)
2.5 Run processing.py (processing time with validated hyperparameters: 2min; processing time with full grid search of hyperparameters: 72-96h)

3. Check the results

All resulting files are saved in respective folders (also working data which is needed between multiple code files).

Notes

The random forest and neural network algorithms already use the validated hyperparameters in order to keep the runtime low. This can be changed by defining the param grids in the grid search lines in the code file „processing.py“ from „…_grid_validated“ to „…_grid“ (they are always stated below each other for each model). Please be advised that the grid search has a very long runtime due to the amount of validating hyperparameters and due to the size of the data sets, as stated in 2.5.

If you use Windows or any operating systems other than MacOS, please adjust the file paths for any data import or export in all files and the reading commands „os.listdir()“ in the files „import.py“ and „cleaning.py“ to the specifications for your operating systems if necessary.

