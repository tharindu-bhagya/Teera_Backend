import shutil
import os

print("Re-zipping the Keras model directory into a valid .keras file...")
shutil.make_archive('cinnamon_model', 'zip', 'cinnamon_disease_model.keras')

if os.path.exists('cinnamon_model.keras'):
    os.remove('cinnamon_model.keras')

os.rename('cinnamon_model.zip', 'cinnamon_model.keras')
print("Created cinnamon_model.keras successfully!")
