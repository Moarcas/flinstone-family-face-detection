#!/bin/bash

# Definirea vectorului de directoare de șters
directories_to_delete=("../date/antrenare/faces/" "../date/antrenare/nonFaces/" "../date/antrenare/descriptors/" "../date/antrenare/models/")

# Iterarea prin vector și ștergerea fiecărui director
for directory in "${directories_to_delete[@]}"; do
    # Verificăm dacă directorul există
    if [ -d "$directory" ]; then
        # Ștergem directorul
        rm -r "$directory"
        echo "Directorul \"$directory\" a fost șters."
    else
        echo "Directorul \"$directory\" nu există."
    fi
done

