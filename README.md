# Jupyter Book template for PseudoLab studies

This is a template for configuring Jupyter Book pages for PseudoLab studies. 

1. make a new repo in PseudoLab Github with the study group name as repo name

   ```
   Pseudo-Lab/2021-Kaggle-Study
   ```

2. clone the repo on your local computer

   ```
   git clone https://github.com/Pseudo-Lab/2021-Kaggle-Study.git
   ```

3. clone this repo

   ```
   git clone https://github.com/Pseudo-Lab/Jupyter-Book-Template
   ```

4. move `book` folder to the `2021-Kaggle-Study` folder which has been created at step 2. 

5. change the contents in `book/docs` folder with the contents from your studies

6. configure `_toc.yml` file

7. build the book using Jupyter Book command

   ```
   jupyter-book build 2021-Kaggle-Study/book
   ```

8. sync your local and remote repositories

   ```
   cd 2021-Kaggle-Study
   git add .
   git commit -m "adding my first book!"
   git push
   ```

9. Publish your Jupyter Book with Github Pages

   ```
   ghp-import -n -p -f book/_build/html -m "initial publishing"
   ```
