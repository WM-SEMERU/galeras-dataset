from pydriller import Repository
from datetime import datetime
import re
import json
import os

import ast_tree
from tree_sitter import Language, Parser

start_date = datetime(2022, 1, 1, 0, 0, 0)
end_date = datetime(2023, 1, 1, 0, 0, 0)
repo_name =  "cassandra"
remote_repo_path = "https://github.com/apache/{}.git".format(repo_name)
commits = Repository(remote_repo_path, since=start_date, to=end_date, only_no_merge = True,
                     only_modifications_with_file_types=['.py'], only_in_branch='trunk').traverse_commits()
print("staring mining ", repo_name)
#'/scratch/danielrc/dataset_extractor/repos/{}'.format(repo_name)
# repo: the owner/repo
# path: the full path to the original file
# func_name: the function or method name
# original_string: the raw string before tokenization or parsing
# language: the programming language
# code/function: the part of the original_string that is code
# code_tokens/function_tokens: tokenized version of code
# docstring: the top-level comment or docstring, if it exists in the original string
# docstring_tokens: tokenized version of docstring
# url: the url for the example (identify natural language)
# idx: the index of code (identify code)


methods = ()


class TreeSitterManager():
    def __init__(self, lang):
        self.language = self.get_language(lang)
        self.parser = Parser()
        self.parser.set_language(self.language)

    def get_language(self, lang):
        return Language(f"{ast_tree.__path__[0]}/grammars/tree-sitter-languages.so", lang)

    def get_ast_errors_and_deep(self, code):
        node_tree = self.parser.parse(bytes(code, "utf8"))
        return self.__detect_ast_errors_and_deep(node_tree.root_node)

    def __detect_ast_errors_and_deep(self, node_root, level=0, max_level=0, count = 0):
        """Traverses the tree catch errors and evaluate tree levels"""
        # if not node_root.has_error:
        #     return [], 0
        counter = node_root.child_count

        results = []
        if node_root.type == "ERROR":
            results.append(node_root.text.decode("utf-8"))
        level += 1
        for n in node_root.children:
            x, y, max_level, count = self.__detect_ast_errors_and_deep(n, level, max_level)
            max_level = max(y, max_level)
            counter += count
            if len(x) > 0:
                results.extend(x)

        return results, max_level, level, counter


ast_error_detector = TreeSitterManager("python")


def extract_methods(source_code, methods):
    regex = r"(\n(\s{4})*)(def |class |async |    @[a-zA-Z]*)"  # r"\n(def |[ {4}]*def |class |    @[a-zA-Z]*)"
    if source_code is None:
        return
    search = re.finditer(regex, source_code, flags=re.MULTILINE)
    start_index = 0
    index_line = {}
    counter = 0
    for s in search:
        if start_index == 0:
            start_index = s.start() + 1
            code = source_code[:start_index]
            counter = len(re.findall("\n", code)) + 1
            continue
        code = source_code[start_index:s.start()]
        index_line[str(counter)] = code.lstrip()
        counter = counter + len(re.findall("\n", code)) + 1
        start_index = s.start() + 1
    code = source_code[start_index:]
    index_line[str(counter)] = code.lstrip()

    list_filtered_methods = []
    for n in methods:
        try:
            final_method = index_line[str(n.start_line)]
            if n.long_name.replace(" ", "") in final_method.split(":")[0].replace(" ", ""):
                ast_errors, ast_deep, level, count = ast_error_detector.get_ast_errors_and_deep(final_method)
                list_filtered_methods.append((n.name, final_method, ast_errors, n.complexity, n.nloc, n.token_count, ast_deep, count))
            elif n.long_name in source_code:
                '''Confirm method does not exist:'''
                print("method exists but failed to recover")
        except KeyError:
            continue

    return list_filtered_methods


def create_json(repo, path, file_name, func_name, commit_message, code, doc_string, url, language, ast_errors,
                complexity, nloc, tokens, ast_deep, ast_node_count):
    return {"repo": repo, "path": path, "file_name": file_name, "fun_name": func_name,
            "commit_message": commit_message, "code": code, "doctring": doc_string,
            "url": url, "language": language, "ast_errors": ast_errors,
            "n_ast_errors": len(ast_errors), "ast_levels": ast_deep, "n_whitespaces_": len(code.split()),
            "complexity": complexity, "nloc": nloc, "token_counts": tokens, "n_ast_nodes": ast_node_count}


def split_code_docstring(original_code):
    regex = "(\"\"\"|\'\'\')"
    if re.search(regex, original_code) is None:
        return None, original_code
    split = re.split(regex, original_code)
    code = ""
    doc_string = ""
    is_doc = False
    for text in split:
        is_comment = re.search(regex, text) is not None
        is_doc = is_comment != is_doc
        if is_comment:
            continue
        if is_doc:
            doc_string = doc_string + re.sub(regex, "", text)
        else:
            code = code + text

    return doc_string, code


save_path = "/nfs/semeru/semeru_datasets/custom_dataset_ast/{}/{}"
save_path1 = "/nfs/semeru/semeru_datasets/custom_dataset_ast/{}"

def save(name, data):
    if not os.path.exists(save_path1.format(repo_name)):
        os.mkdir(save_path1.format(repo_name))
    with open(save_path.format(repo_name,name), 'w') as f:
        print("saving data")
        json.dump(data, f, ensure_ascii=False, indent=4)


json_list = []
counter = 0
data_files = 1

try:
    for commit in commits:
        
        for file in commit.modified_files:
            if not file.filename.endswith('.py'):
                continue
            methods = extract_methods(file.source_code, file.changed_methods)
            if methods is None:
                continue

            for method in methods:
                doc_string, actual_code = split_code_docstring(method[1])
                json_method = create_json(commit.project_name, file.new_path, file.filename, method[0], commit.msg,
                                        actual_code, doc_string, remote_repo_path, "python", method[2], method[3],
                                        method[4], method[5], method[6],method[7])
                json_list.append(json_method)
            if len(json_list) > 5000:
                save("data_{}.json".format(str(data_files)), json_list)
                data_files = data_files + 1
                json_list = []
except:
    print("missed commit error")
    save("data_{}.json".format(str(data_files)), json_list)
    
save("data_{}.json".format(str(data_files)), json_list)
    

#save("data_{}.json".format(str(data_files)), json_list)


##git config --global -add safe.directory
