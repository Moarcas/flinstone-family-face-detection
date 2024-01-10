#!/bin/bash

# Hardcodeaza numele primului fisier de sters
file_to_delete_1="../date/antrenare/descriptors/negative*"
prefix="negative"
folder="../date/antrenare/descriptors"  # specifică calea folderului, dacă este necesar

files_to_delete=($folder/$prefix*)

# Verifica dacă există fișiere care se potrivesc cu modelul
if [ -e "${files_to_delete[0]}" ]; then
  # Șterge fiecare fișier găsit
  rm "${files_to_delete[@]}"
  echo "Fișierele cu prefixul '$prefix' au fost șterse cu succes."
else
  echo "Nu există fișiere cu prefixul '$prefix' în folderul '$folder'."
fi

folder="../date/antrenare/models"  # Specifică calea folderului pe care dorești să-l ștergi

# Verifică dacă folderul există
if [ -d "$folder" ]; then
  # Șterge folderul și conținutul său recursiv
  rm -r "$folder"
  echo "Folderul '$folder' a fost șters cu succes."
else
  echo "Folderul '$folder' nu există."
fi
