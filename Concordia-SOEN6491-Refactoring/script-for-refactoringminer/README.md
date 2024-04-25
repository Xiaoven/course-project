Since release 3.0.0, RefactoringMiner requires **Java 17** or newer and **Gradle 7.4** or newer.

This project uses the fat jar built from [the master branch of RefactoringMiner](https://github.com/tsantalis/RefactoringMiner/tree/5db6ca0962a31c19a56f4b4f605c1a3a5184fb0a) (accessed on Mar 12, 2024).
Its path is `libs/RefactoringMiner-3.0.4-all.jar`.


# RQ 3
> RQ 3: How do the identified refactorings influence code metrics that serve as indicators of design quality and maintainability in software projects?

RQ3 requires to collect refactorings between tags.

1. Prepare a list of tags to detect.

    If your project is git-based, the following command can list the tags of that project, and save it into a file.

    Git command to list the tags of a git project:
    ```shell
    git tag --sort=version:refname > tags.txt
    ```
   
2. Run `refactoring.GitVersionAnalyzer`.

   `refactoring.GitVersionAnalyzer` is based on the `void detectAtDirectories(File var1, File var2, RefactoringHandler var3)` API.
   Therefore, you need to clone your git projects to two places, so that `refactoring.GitVersionAnalyzer` can check them out to different tag version and detect refactorings.
    
3. Run `metrics.GitBasedMetricsCalculator`
   Command to remove unnecessary metric files:
   ```shell
   find . -type f \( -name "field.csv" -o -name "method.csv" -o -name "variable.csv" \) -delete
   ```