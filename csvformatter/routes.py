
import os, datetime, uuid, io, csv

from flask import Flask, flash, request, redirect, url_for, render_template, make_response, send_file, current_app as app

from csvformatter import ALLOWED_EXTENSIONS, format_csv
from werkzeug.utils import secure_filename
from flask_weasyprint import HTML, render_pdf, CSS

import pandas as pd 
@app.route('/')
def hello_world():
    #return home.jinja2 template
    return render_template('home.html')

csv_storage = {}
VOLUME_PATH = '/app/files'


@app.route('/preview', defaults={'file_name': None}, methods=['GET', 'POST'])
@app.route('/preview/<file_name>', methods=['GET', 'POST'])
def upload_file(file_name):

    if file_name:
        #open file and read the content


        file_path = os.path.join(VOLUME_PATH, file_name)
        #open the file and read the content using panda
        data = pd.read_csv(file_path, sep=',', encoding='utf-8')
        # Convert the DataFrame to a list of dictionaries
        data = data.to_dict(orient='records')
        data = format_csv(data)

        
        return render_template('preview.html', data=data, filename=file_name, date=datetime.datetime.now(), temp_id=None)
       
    #if metho is post, check if file is in request.files
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            try:
                data = pd.read_csv(file, sep=';', encoding='utf-8')
                # Convert the DataFrame to a list of dictionaries
                data_list = data.to_dict(orient='records')
            except Exception as e:
                flash(f"Error processing file: {str(e)}")
                return redirect(request.url)
            
            data_list = format_csv(data_list)
            # Generate a unique ID for this CSV
            temp_id = str(uuid.uuid4())
            # Store the CSV content in the dictionary

            #TODO: cleanup memory buffer after some time
            csv_storage[temp_id] = data_list
            
            return render_template('preview.html', data=data_list, filename=filename, date=datetime.datetime.now(), temp_id=temp_id)
        
    return render_template('home.html')


@app.route('/download/<tempID>', methods=['POST'])
def download_pdf(tempID):
    # Retrieve the CSV data from the dictionary
    data = csv_storage.get(tempID)
    
    if data is None:
        flash("Invalid or expired link")
        return redirect(url_for('hello_world'))
    
    html = render_template('summary.html', data=data, date=datetime.datetime.now())
    css = CSS(string='@page { size: A4; margin: 1cm; }', media_type='print')
    pdf = HTML(string=html).write_pdf(stylesheets=[css])
    
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        attachment_filename= f"summary_{tempID}.pdf"
    )

@app.route('/save/<tempID>', methods=['POST'])
def save_csv(tempID):
    # Retrieve the CSV data from the dictionary
    data = csv_storage.get(tempID)
    
    if data is None:
        flash("Invalid or expired link")
        return redirect(url_for('hello_world'))
    
     # Generate a unique filename
    filename = f"summary_{tempID}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    file_path = os.path.join(VOLUME_PATH, filename)
    
    # Open the file for writing
    with open(file_path, 'w', newline='') as csvfile:
        # If data is not empty, extract headers from the first dictionary
        if data:
            headers = data[0].keys()
            csvwriter = csv.DictWriter(csvfile, fieldnames=headers)
            # Write the header
            csvwriter.writeheader()
            # Write the data rows
            for row in data:
                csvwriter.writerow(row)
        else:
            print("No data to save.")

   
    flash("File saved successfully")
    return redirect(url_for('hello_world'))

@app.route('/past')
def show_past_csv_files():
    
    # List all files in the directory
    all_files = os.listdir(VOLUME_PATH)
    
    # Filter for CSV files
    csv_files = [file for file in all_files if file.endswith('.csv')]
    
    
    # Generate and return an HTML page that lists the CSV files
    # Assuming you have a template called 'past.html' under your templates directory
    return render_template('past.html', csv_files=csv_files)
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS