from construct_ast import *
from llm import *
from code_editor import *
from gitapi import *


def create_file_graphs(filepath):
    """ 
    Create and display call graph for a given file
    """
    print(f"Processing file and displaying graph for: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read() 
        tree = CreateTree(code, filepath)
        G, list_functions = tree.call_graph()
        tree.draw_graph()
    return tree, list_functions
        
    
def transform(directory):
    """ 
    Transform the files of a directory using llm
    """
    tree_dict = {}
    function_dict = {}
    # traverse each file in directory and create call graph for each
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                tree, list_functions = create_file_graphs(filepath)
                tree_dict[filepath] = tree
                function_dict[filepath] = list_functions
    
    #prompt the llm using user input                         
    prompt, function_name = get_user_input_for_llm(function_dict, tree_dict)
    tree_, filepath_ = get_tree_of_function(function_name, function_dict, tree_dict)
    response_prev = get_approved_llm_response(prompt, function_dict, tree_dict)
    #update the code given by llm to the code file
    editor = CodeEditor(filepath_)
    a = tree_.get_st_and_end_points(function_name)
    editor.replace_code(a[0],a[1], response_prev)
    code = ''
    with open(filepath_, 'r') as file:
        code = file.read()
    #update the tree as start and end points of functions have now changes
    tree_.update_tree(code)
    
    #update and correct the function calls in the callers of the function
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                update_callers_code(filepath, function_name, tree_dict[filepath], editor.remove_triple_backticks(response_prev), function_dict, tree_dict)
    
    #display the updated call graphs for each file
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)   
                tree, list_functions = create_file_graphs(filepath)
                tree_dict[filepath] = tree
                function_dict[filepath] = list_functions
    
def get_tree_of_function(function_name, function_dict, tree_dict):
    """ 
    Get the tree of the function from the function name
    """
    for key in function_dict.keys():
        if function_name in function_dict[key]:
            return tree_dict[key], key
    return None
                
def get_user_input_for_llm(function_dict, tree_dict, full_prompt_by_user=False):
    """ 
    Get user input for llm prompt
    if full_prompt_by_user is False, then get the function name and argument to be added from user to fit into the sample prompt else get the whole prompt from user
    """
    if not full_prompt_by_user:
        #to get from user
        #name of the function to be modified
        #argument of the function to be added
        #little info about the argument and how it should affect the function
        function_to_be_modified = input('Name of function to be modified: ')
        arg_to_be_added = input('Parameter to be added: ')
        arg_info = input('Info about the parameter and how it should affect the function: ')
        tree1, file_path1 = get_tree_of_function(function_to_be_modified, function_dict, tree_dict)
        function_code = tree1.get_function_from_name(function_to_be_modified)
        prompt = (f"Modify/Edit the given function definition to add a '{arg_to_be_added}' parameter to it and update the function accordingly. "
              f"The '{arg_to_be_added}' parameter should {arg_info}. Generate ONLY the code output for the function.\n"
              f"function-\n{function_code}")
        return prompt, function_to_be_modified
    else:
        function_to_be_modified = input('Name of function to be modified: ')
        return input('Enter the full prompt: '), function_to_be_modified
        
def get_approved_llm_response(prompt, function_dict, tree_dict):
    """ 
    Get approved llm response from user i.e the user gets option to keep prompting till they get a satisfactory response
    """
    #approve llm response from user
    while True:
        response = get_llm_response(prompt)
        print('-------------------------------------------')
        print("Response from LLM: \n", response)
        key = input("Is the response correct? (y/n): ")
        if key == 'y':
            return response
        else:
            key2 = input("Do you want to enter full prompt? (y/n):")
            if key2 == 'y':
                prompt = get_user_input_for_llm(function_dict, tree_dict, full_prompt_by_user=True)
            else:
                prompt = get_user_input_for_llm(function_dict, tree_dict,)

    
def update_callers_code(file_path, function_name, tree, prev_response, function_dict, tree_dict):
    """ 
    update the code of the caller functions of the given function by prompting llm
    """
    #get callers' names and codes
    callers_names = tree.get_callers(function_name)
    callers_codes = tree.get_callers_function_code(function_name)
    # function_def = prev_response
    function_def = tree.get_function_from_name(function_name)
    #prompt llm to edit code of each caller to fit the new function definition and update the arguments
    for i in range(len(callers_codes)):
        caller_code = callers_codes[i]
        caller_name = callers_names[i]
        prompt = (
            f"The function definition for {function_name} has changed to the following:\n{function_def}\n"
            f"Update the given caller code to reflect the changes in the function definition and to pass the argument properly to {function_name} function. Follow best coding practices and only return the updated code. Generate only the code output for the caller code.\nCaller code:\n{caller_code}"
        )   
        response = get_approved_llm_response(prompt, function_dict, tree_dict)
        #update the modified function/code provided by lmm to the actuall code file
        editor = CodeEditor(file_path)
        a = tree.get_st_and_end_points(caller_name)
        editor.replace_code(a[0],a[1], response)
        code = ''
        with open(file_path, 'r') as file:
            code = file.read()
        tree.update_tree(code)
            
    

                
if __name__ == "__main__":
    # code to clone repo and transform files
    github_api = GitHubAPI()
    repo_url = input("provide the url to the git repo: ")
    # repo_url = "https://github.com/t-gandhi-19/example"  
    cloned_path = github_api.clone_repo(repo_url)
    transform(cloned_path)
    

