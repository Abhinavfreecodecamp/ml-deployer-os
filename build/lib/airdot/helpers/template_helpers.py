from typing import List

from airdot.collection.collections import python_function_prop, source_file_props
from airdot.helpers.general_helpers import add_space


def make_soruce_file(
    dir: str, pyProps: python_function_prop, source_file_name: str = "source"
):

    sourceParts: List[str] = [
        "import sys",
        "from flask import escape, jsonify, Flask, request",
        "import pickle",
        "app = Flask('ml-deployer')"
    ]
    if pyProps.namespaceFroms:
        for iAs, iModule in pyProps.namespaceFroms.items():
            sourceParts.append(f"from {iModule} import {iAs}")
    if pyProps.namespaceImports:
        for iAs, iModule in pyProps.namespaceImports.items():
            if iModule == iAs:
                sourceParts.append(f"import {iModule}")
            else:
                sourceParts.append(f"import {iModule} as {iAs}")
    add_space(sourceParts)
    # sourceParts.append("storage_client = storage.Client()")
    # sourceParts.append("bucket = storage_client.bucket('model-ml-deployer')")
    if pyProps.namespaceVars and pyProps.namespaceVarsDesc:
        for nName, _ in pyProps.namespaceVars.items():
            sourceParts.append(f"blob = bucket.blob('{dir}/{nName}.pkl')")
            sourceParts.append(f"{nName} =  pickle.loads(blob.download_as_string())")
    if pyProps.customInitCode:
        sourceParts.append("\n" + "\n\n".join(pyProps.customInitCode))
    add_space(sourceParts)
    if pyProps.namespaceFunctions:
        for _, fSource in pyProps.namespaceFunctions.items():
            sourceParts.append(fSource)
            add_space(sourceParts)
    add_space(sourceParts)

    if pyProps.source:
        sourceParts.append("# main function")
        sourceParts.append(pyProps.source)

    # add calling method
    add_space(sourceParts)
    sourceParts.append("@app.route('/', methods=['POST'])")
    sourceParts.append(f"def main_{pyProps.name}():")
    sourceParts.append("\tdata = request.get_json()")
    sourceParts.append("\tif data is None:")
    sourceParts.append(f"\t\treturn jsonify({pyProps.name}())")
    sourceParts.append("\telse:")
    sourceParts.append(f"\t\treturn jsonify({pyProps.name}(**data))")
    return source_file_props(f"{source_file_name}.py", "\n".join(sourceParts))


def get_docker_template(req_string):
    dockerBuildParts: List[str] = [
            "FROM python:3.8-slim",
            "ENV APP_HOME /app",
            "WORKDIR $APP_HOME",
            "COPY . ./",
            f"RUN pip install {req_string}",
            "CMD exec gunicorn --bind :8080 --workers 1 --threads 8 app:app"
    ]
    return dockerBuildParts