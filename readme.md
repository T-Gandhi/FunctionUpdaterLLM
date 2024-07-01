**Code Transformation Module using Large Language Models**         
Module to transform files in code repository using large language models.

Set Up:
1. **Cloning the Repository**:
    ```bash
    git clone <repository-url>
    ```

2. **Installing Requirements**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Uploading the `.env` File**:
    - Upload the `.env` file to the project directory. The file should contain [Github API token](https://github.com/settings/tokens) 'GH_TOKEN' and [Groq API key](https://console.groq.com/keys) 'GROQ_API_KEY'.

4. **Running the Main Script**:
    ```bash
    python main.py
    ```


**Description:**       
First user prompted to provide url for the repository that has to be transformed.  
The repository is then cloned and call graphs of each of the files are displayed. In the call graph on the node the function name and parameter is displayed and on the edges the arguments used to call the callee function are displayed in red.  
Then user prompted to provide the name of the function to be modified, parameter to be added and info about the paramete and how it should affect the function.    
Prompt for the llm to update function definition -    
*Modify/Edit the given function definition to add a loglevel parameter to it and update the function accordingly.  
The loglevel parameter should be printed out as well. Generate ONLY the code output for the function.   
function-  
def log(self, message):  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print(f"LOG: {message}")*    
The response from the llm is displayed and should be approved by the user before adding to the code file.   
Then all the callers updated as well using llm using a simple prompt.           
Prompt to update callers -        
*The function definition for log has changed to the following:       
def log(self, message, loglevel):               
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print(f"{loglevel}: {message}")           
Update the given caller code to reflect the changes in the function definition and to pass the argument properly to log function. Follow best coding practices and only return the updated code. Generate only the code output for the caller code.    
Caller code:      
...*               
The updated call graphs for each of the files are also displayed.                           
        

          


**Assumption** -            
For now problem only to add a paramete/argument to function so use the llm to -            
- modify function's working to add the parameter/argument             
- modify wherever the function called to pass the argument properly (not just change the signature)            
This can be generalized as well if the user provides the whole prompt to the llm about how to modify the function definition and then this updated function definition will be used to update all callers as well                   


**LLM Details**
- The current implementation uses Llama 3 with Groq AI due to GPU constraints. A more powerful LLM can be used for better results.            
