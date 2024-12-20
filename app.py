from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

# Configuración de la carpeta de files usando una variable de entorno
FILES_FOLDER = os.environ.get('', os.path.join(app.root_path, 'files'))
app.config['FILES_FOLDER'] = FILES_FOLDER

def list_directory(folder):
    try:
        items = os.listdir(folder)
        files = []
        subfolders = []
        for item in items:
            item_path = os.path.join(folder, item)
            relative_path = os.path.relpath(item_path, app.config['FILES_FOLDER'])
            if os.path.isfile(item_path):
                files.append((item, relative_path))
            else:
                subfolders.append((item, relative_path))

        # Ordenar las subcarpetas por número de mes, si es posible
        try:
            subfolders.sort(key=lambda x: int(x[0].split('-')[0]))
        except (ValueError, IndexError):
            # Si no se puede extraer el número de mes, ordenar alfabéticamente
            subfolders.sort(key=lambda x: x[0].lower())

        # Ordenar los archivos alfabéticamente
        files.sort(key=lambda x: x[0].lower())

        return files, subfolders
    except OSError:
        abort(404)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    full_path = os.path.join(app.config['FILES_FOLDER'], path)

    if not os.path.exists(full_path):
        abort(404)

    if os.path.isfile(full_path):
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path), as_attachment=True)

    files, subfolders = list_directory(full_path)
    return render_template('index.html', files=files, subfolders=subfolders, current_path=path)

@app.route('/download/<path:path>')
def download_file(path):
    return send_from_directory(app.config['FILES_FOLDER'], path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)