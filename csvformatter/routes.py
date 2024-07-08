
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

@app.route('/preview', methods=['GET', 'POST'])
def upload_file():
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
            
            # Format the data
            data_list = format_csv(data_list)
            # Generate a unique ID for this CSV
            temp_id = str(uuid.uuid4())
            # Store the CSV content in the dictionary
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
    
    # Specify the Docker volume path
    volume_path = '/app/files'
    # Generate a unique filename
    filename = f"summary_{tempID}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    file_path = os.path.join(volume_path, filename)
    
    # Save the CSV data to a file in the Docker volume
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in data:
            csvwriter.writerow(row)
    
    flash("File saved successfully")
    return redirect(url_for('hello_world'))


    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS