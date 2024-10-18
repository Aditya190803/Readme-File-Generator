import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import ast
from readme_template import get_readme_template

def read_code_file(file):
    return file.read().decode("utf-8")

def analyze_code(code):
    try:
        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        imports += [f"{node.module}.{alias.name}" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for alias in node.names]
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports
        }
    except SyntaxError:
        return {"error": "Unable to parse the code. Please ensure it's valid Python code."}

def generate_readme(project_name, code_info, code_analysis):
    template = get_readme_template()

    prompt_template = PromptTemplate(
        input_variables=["project_name", "functions", "classes", "imports", "code"],
        template=template
    )

    chatgroq = ChatGroq(api_key=st.secrets["GROQ_API_KEY"])
    llm_chain = LLMChain(llm=chatgroq, prompt=prompt_template)

    readme_content = llm_chain.run(
        project_name=project_name,
        functions=", ".join(code_analysis["functions"]),
        classes=", ".join(code_analysis["classes"]),
        imports=", ".join(code_analysis["imports"]),
        code=code_info
    )

    return readme_content

def main():
    st.set_page_config(page_title="README Generator for Python Projects")
    st.title("README Generator for Python Projects")
    
    project_name = st.text_input("Enter Project Name")
    code_file = st.file_uploader("Upload your Python code file", type=["py"])

    if st.button("Generate README"):
        if project_name and code_file:
            with st.spinner("Generating README..."):
                code_info = read_code_file(code_file)
                code_analysis = analyze_code(code_info)
                
                if "error" in code_analysis:
                    st.error(code_analysis["error"])
                else:
                    readme_content = generate_readme(project_name, code_info, code_analysis)
                
                    st.subheader("Generated README")
                    st.text_area("README.md", value=readme_content, height=400)

                    st.download_button(
                        label="Download README.md",
                        data=readme_content,
                        file_name="README.md",
                        mime="text/markdown"
                    )
        else:
            st.error("Please enter a project name and upload a Python code file.")

if __name__ == "__main__":
    main()