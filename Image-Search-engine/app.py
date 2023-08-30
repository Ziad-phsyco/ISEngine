from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
import os
import shutil

from imagesearchengine import ImageSearchEngine

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])



@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    global image_uploaded  # Declare as global to modify the global variable
    if 'image' not in request.files:
        return redirect(request.url)
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        image_uploaded = True  # Set the flag to True
        return redirect(url_for('show_image', filename=file.filename))

@app.route('/show-image/<filename>')
def show_image(filename):
    image_path = url_for('uploaded_file', filename=filename)
    return render_template('upload.html', image_path=image_path, image_uploaded=image_uploaded)

@app.route('/search', methods=['POST'])
def search_similar():
    global similar_images_found
    query_filename = request.form.get('query_filename')
    print("FILE NAME RECIEVED ::: {}".format(query_filename))
    # Simulate creating an instance of ImageSearchEngine and searching for similar images
    search_engine = ImageSearchEngine(5)
    similar_images = search_engine.get_similar_images(query_filename)
    # send images from directory
    img_paths = []
    similar_images_found = True
    for img in similar_images:
        # Replace backslashes with forward slashes
        img = img.replace('\\', '/')
        # copy image to static/uploads folder
        img_name = img.split('/')[-1]
        # create path to image in the upload folder
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        # copy image to upload folder
        shutil.copy(img, img_path)

        print("IMAGE PATH ::: {}".format(img))
        # Add image path to list
        img_paths.append(url_for('uploaded_file', filename=img_name))
    # return similar images
    print("SIMILAR IMAGES ::: {}".format(img_paths))
    return render_template('upload.html', similar_images_found=similar_images_found, img_paths=img_paths)



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)