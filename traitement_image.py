import cv2
import os
import time
import hashlib
from tkinter import Tk, Label, Button, Frame
from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fixed paths
input_folder = 'photos/photo'
output_blurry = 'photos/photos_floues'
output_sharp = 'photos/photos_nettes'
output_duplicates = 'photos/photos_duplicates'

def is_blurry(image_path, threshold=100.0):
    image = cv2.imread(image_path)
    if image is None:
        return True  # Si l'image ne peut pas être chargée, la considérer comme floue
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold

def hash_image(image_path):
    """Calcule le hachage SHA-256 d'une image."""
    hasher = hashlib.sha256()
    with open(image_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_image(image_path, output_blurry, output_sharp, duplicates_set, results_text):
    if not os.path.exists(image_path):
        results_text.append(f"{os.path.basename(image_path)} : Fichier non trouvé")
        return

    image_hash = hash_image(image_path)
    if image_hash in duplicates_set:
        results_text.append(f"{os.path.basename(image_path)} : Doublon")
        # Faire une copie au lieu de déplacer
        destination_path = os.path.join(output_duplicates, os.path.basename(image_path))
        os.system(f"cp '{image_path}' '{destination_path}'")
    else:
        duplicates_set.add(image_hash)
        if is_blurry(image_path):
            # Faire une copie au lieu de déplacer
            destination_path = os.path.join(output_blurry, os.path.basename(image_path))
            os.system(f"cp '{image_path}' '{destination_path}'")
            results_text.append(f"{os.path.basename(image_path)} : Floue")
        else:
            # Faire une copie au lieu de déplacer
            destination_path = os.path.join(output_sharp, os.path.basename(image_path))
            os.system(f"cp '{image_path}' '{destination_path}'")
            results_text.append(f"{os.path.basename(image_path)} : Nette")

def process_images_sequential(input_folder, output_blurry, output_sharp, output_duplicates, results_text):
    if not os.path.exists(output_blurry):
        os.makedirs(output_blurry)
    if not os.path.exists(output_sharp):
        os.makedirs(output_sharp)
    if not os.path.exists(output_duplicates):
        os.makedirs(output_duplicates)

    duplicates_set = set()
    for filename in os.listdir(input_folder):
        image_path = os.path.join(input_folder, filename)
        process_image(image_path, output_blurry, output_sharp, duplicates_set, results_text)

def process_images_parallel(input_folder, output_blurry, output_sharp, output_duplicates, results_text, num_threads):
    if not os.path.exists(output_blurry):
        os.makedirs(output_blurry)
    if not os.path.exists(output_sharp):
        os.makedirs(output_sharp)
    if not os.path.exists(output_duplicates):
        os.makedirs(output_duplicates)

    duplicates_set = set()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for filename in os.listdir(input_folder):
            image_path = os.path.join(input_folder, filename)
            futures.append(executor.submit(process_image, image_path, output_blurry, output_sharp, duplicates_set, results_text))
        for future in as_completed(futures):
            future.result()

def run_sequential():
    results_text = []
    start_time = time.time()
    process_images_sequential(input_folder, output_blurry, output_sharp, output_duplicates, results_text)
    end_time = time.time()

    elapsed_time = end_time - start_time
    results_text.append(f"Temps de traitement séquentiel : {elapsed_time:.2f} secondes")
    update_results(sequential_results, results_text)

def run_parallel():
    results_text = []
    num_threads = 4  # Ajustez ce nombre en fonction du nombre de cœurs logiques de votre CPU
    start_time = time.time()
    process_images_parallel(input_folder, output_blurry, output_sharp, output_duplicates, results_text, num_threads)
    end_time = time.time()

    elapsed_time = end_time - start_time
    results_text.append(f"Temps de traitement parallèle avec {num_threads} threads : {elapsed_time:.2f} secondes")
    update_results(parallel_results, results_text)

def update_results(results_frame, results_text):
    for widget in results_frame.winfo_children():
        widget.destroy()

    for line in results_text:
        label = Label(results_frame, text=line)
        label.pack()

# Setup GUI
root = Tk()
root.title("Traitement d'Images")

# Frames
main_frame = Frame(root)
main_frame.pack(fill="both", expand=True)

left_frame = Frame(main_frame, bg="lightblue", width=400)
left_frame.pack(side="left", fill="both", expand=True)

right_frame = Frame(main_frame, bg="lightblue", width=400)
right_frame.pack(side="right", fill="both", expand=True)

# Buttons
Button(left_frame, text="Exécution Séquentielle", command=run_sequential).pack(pady=20)
Button(right_frame, text="Exécution Parallèle", command=run_parallel).pack(pady=20)

# Results areas
sequential_results = Frame(left_frame, bg="lightblue")
sequential_results.pack(fill="both", expand=True)

parallel_results = Frame(right_frame, bg="lightblue")
parallel_results.pack(fill="both", expand=True)

root.mainloop()

