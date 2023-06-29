# Galeras

## What is Galeras?

Galeras is a collection of Python snippets created specifically for evaluating the AsC-Eval approach. It provides a fresh and unique set of code samples that were not used in training the selected LLMs , addressing the issue of data contamination.

## Background

To accurately evaluate AsC-Eval, it was crucial to avoid using samples in the evaluation that had already been used for LLM training. Additionally, popular code datasets such as CodesearchNet or CodeXglue were not suitable due to potential data contamination.

## Data Collection Process

To ensure a clean and uncontaminated dataset, Galeras takes the following steps to collect data:

1. Selection of Python repositories: Python repositories on GitHub with more than one hundred stars were identified, indicating their popularity and relevance. These repositories served as the source for collecting the code snippets.

2. Timeframe: The focus was on collecting recent commits performed between January 1st, 2022, and January 1st, 2023. This ensured that the dataset would not contain code contamination from Chat-GPT, which was trained with data through 2021.

3. Snippet extraction: Code snippets were extracted from new and updated Python methods found in the selected repositories.

4. Deduplication: The commits' history was utilized to identify and remove duplicate code snippets, ensuring that the Galeras dataset only contained unique Python code samples.

5. Feature description and validation: The data points in Galeras include various fields, such as commit ID, repository name, path, file name, function name, commit message, code, and documentation. The documentation field contains the docstring and related confounders such as the number of words, vocabulary size, number of whitespaces, and language. The validation process involved manually verifying the meaningfulness of the docstring and commit messages against the code, as well as checking the consistency and correctness of features like the number of nodes, token counts, and AST (Abstract Syntax Tree) features.

6. Data Specialization: Following the validation process, the data was refined based on the specific requirements of software engineering tasks. Data points containing docstrings were identified as suitable for code generation tasks, whereas data points with test cases were deemed valuable for test generation tasks. Each specialization filter resulted in the creation of a new JSON file containing the relevant data.

## Usage

The Galeras code dataset is valuable for evaluating approaches, techniques, and models in the field of Software Engineering, particularly those related to large language models and deep learning for software engineering. Researchers, developers, and data scientists can utilize this dataset to assess the performance and effectiveness of their methodologies, as well as conduct comparative studies.

## Updates and Contributions

Galeras introduces a code-based benchmark to interpret LLMc, focusing on answering causal queries of interest. It enables ML researchers in the software engineering field to explain the causal effects of a set of confounders associated with the treatment input prompt. Galeras also provides a new pipeline for obtaining updated data.

The main contributions of Galeras are:

- A filtered dataset with non-contaminated code snippets for benchmarking LLMs.
- Additional features in the dataset, including AST errors, AST levels, whitespaces, tokens, cyclomatic complexity, and the number of lines.
- A pipeline to generate new datasets for specific software engineering tasks.
- A causal effect benchmarking framework for interpreting code generation in LLMs.

For the raw dataset, curated dataset, and Galeras prompts used in experiments, the dataset is available on Zenodo and Huggingface.