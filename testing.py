from flask import Flask, request, render_template,redirect, url_for
import os
import pandas as pd
import requests
from jinja2 import Template
from datetime import datetime
import json
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return render_template('index.html', error='No selected file')

        # Save the uploaded file to a temporary location
        file_path = '/Users/utkarshshukla/Documents/codebases/Testing/uploads' + file.filename
        file.save(file_path)

        # Read API details from the uploaded spreadsheet
        api_details = read_api_details_from_spreadsheet(file_path)

        # Run API tests
        test_results = run_api_tests(api_details)

        # Generate HTML report
        generate_html_report(test_results)

        # Remove the temporary file
        os.remove(file_path)

        return render_template('index.html', success='File uploaded and API tests executed successfully!')

    return render_template('index.html')


def read_api_details_from_spreadsheet(file_path):
    df = pd.read_csv(file_path)
    print(df)
    return df

def run_api_tests(api_details):
    results = []
    response_time_threshold = 1.0
    for index, row in api_details.iterrows():
        endpoint = row['Endpoint']
        method = row['Method']
        headers = json.loads(row['Headers']) if pd.notna(row['Headers']) else {}
        payload = json.loads(row['Payload']) if pd.notna(row['Payload']) else {}
        expected_status_code = int(row['ExpectedStatusCode'])
        response_validation = json.loads(row['ResponseValidation']) if pd.notna(row['ResponseValidation']) else None


        response, response_time, url = make_api_request(endpoint, method, headers, payload)

        result = {
            "Endpoint": url,
            "ResponseTime": validate_response_time(response_time,response_time_threshold),
            "Status": validate_status(response, expected_status_code),
            "ResponseValidation": validate_response(response, response_validation),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        results.append(result)

    return results

def make_api_request(endpoint, method, headers, payload):
    url = f"https://jsonplaceholder.typicode.com/{endpoint}"  # Update the base URL
    start_time = time.time()
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=payload)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=payload)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response_time = time.time() - start_time
    return response, response_time, url

def validate_response_time(response_time,response_time_threshold):
    if response_time <= response_time_threshold:
        return f"{response_time} sec"
    else:
        return f"Failed - too slow {response_time} greater than {response_time_threshold}"

def validate_status(response, expected_status_code):
    actual_status_code = response.status_code
    if actual_status_code == expected_status_code:
        print("running and passing")
        return "Passed"
    else:
        print("failed running")
        return f"Failed - Expected: {expected_status_code}, Actual: {actual_status_code}"


def validate_response(response, response_validation):
    if response_validation is None:
        return "No validation specified"

    # Validate content
    if 'content' in response_validation:
        expected_content = response_validation['content']
        actual_content = response.json()
        print(type(expected_content))
        print(type(actual_content))
        if isinstance(expected_content, str):
            # If expected_content is a string, parse it as JSON
            try:
                expected_content = json.loads(expected_content)
            except json.JSONDecodeError:
                return "Invalid JSON structure in ResponseValidation"

        if isinstance(expected_content, dict) and isinstance(actual_content, dict):
            # Compare nested dictionaries
            if expected_content == actual_content:
                content_validation_result = "Content validation passed"
            else:
                content_validation_result = f"Content validation failed - Expected: {expected_content}, Actual: {actual_content}"
        else:
            content_validation_result = "Invalid content structure in ResponseValidation"

    else:
        content_validation_result = "No content validation specified"

    # Validate other conditions as needed

    return content_validation_result

def generate_html_report(results):
    print("generating html")
    with open("report_template.html", "r") as template_file:
        template_content = template_file.read()
        template = Template(template_content)

        html_output = template.render(results=results)

    with open("api_test_report.html", "w") as output_file:
        output_file.write(html_output)


if __name__ == "__main__":
    app.run(debug=True)

