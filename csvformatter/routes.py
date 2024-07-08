
import os
import csv
from flask import Flask, flash, request, redirect, url_for, render_template, current_app as app
from csvformatter import ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename

import pandas as pd 
@app.route('/')
def hello_world():
    #return home.jinja2 template
    return render_template('home.html')


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
            
            print(data_list)
            return render_template('preview.html', data=data_list, filename=filename)
        
    return render_template('home.html')


def format_csv(data):
    #Parse the csv data in a more readeble way
    return data
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS