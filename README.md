BetonX

✅ Ce que tu obtiens :
API pour recuperer la data beton

Chargement des données depuis SQLite

Nettoyage automatique des valeurs (virgules → points)

Résumé statistique affiché

Interface de correction interactive pour les valeurs manquantes (par numeroNSB)

Écriture directe dans la base avec rechargement instantané

On conserve la numeroNSB modifiée et les colonnes mises à jour.

Après le st.rerun(), on recharge la table.

On applique un style conditionnel avec DataFrame.style.applymap().

Afficher les moyennes des résistances par âge et par formule de béton :

✅ 1. 📊 Graphique comparatif par âge et par formule
✅ 2. 🎯 Moyenne des résistances sur les 30 derniers jours
✅ Une visualisation graphique des anomalies (ex: scatter ou heatmap) ?

✅ Une exportation Excel ou CSV des résultats filtrés ?

✅ Je peux aussi t’aider à sauvegarder les anomalies détectées dans une table dédiée de ta base SQLite.

Ton df contient les colonnes de résistances aux différents âges sous forme de colonnes distinctes (jour_1, jour_3, etc.). Pour détecter anomalie par valeur, il faut :

Transformer ces colonnes en format long (une ligne par numeroNSB + jour + valeur résistance),

Appliquer Isolation Forest sur ces valeurs individuelles (avec éventuellement d’autres features),

Ajouter une colonne "anomalie" par valeur.

Merci pour la précision, c’est important ! La colonne formule (type de béton) et l’âge (jour_1, jour_3, etc.) sont des facteurs clés qui influencent la résistance, donc ils doivent absolument être pris en compte dans la détection d’anomalies.

Proposition améliorée avec segmentation par formule et prise en compte de l’âge (age_jour)
Points clés :
On conserve la transformation en format long (chaque mesure est une ligne).

On inclut la formule comme feature catégorielle encodée (par exemple, via un LabelEncoder ou pd.get_dummies).

L'âge (extrait de age_jour) est converti en nombre entier.

On conserve slump et temperature comme variables explicatives.

Le modèle Isolation Forest est entraîné sur ces features.

Le résultat anomalie est ajouté par mesure.
L’âge est un facteur majeur, car la résistance évolue dans le temps.

La formule influence la résistance attendue.

Le modèle peut détecter des résistances anormales par rapport à la formule et à l’âge, ajusté par les conditions slump et temperature.

L’âge est un facteur majeur, car la résistance évolue dans le temps.

La formule influence la résistance attendue.

Le modèle peut détecter des résistances anormales par rapport à la formule et à l’âge, ajusté par les conditions slump et temperature.

Ok, tu veux donc visualiser les anomalies détectées par Isolation Forest, mais en les comparant aux valeurs acceptables (seuils), sans remplacer la détection par des règles fixes.

Voici comment tu peux faire ça, en intégrant les deux aspects :

Détection IA (Isolation Forest)

Visualisation des mesures et des anomalies sur fond des seuils acceptables (seuil métier)

Comment intégrer ?
Remplace ta fonction de détection dans evalAnomalies.py par ce code.

Appelle cette fonction dans un onglet Streamlit dédié.

Ajoute ou adapte la table seuils_acceptables selon tes règles métiers.

Le graphique affiche :

Les mesures normales en bleu

Les anomalies détectées en rouge

Les lignes de seuil métier en trait pointillé par formule

Oui, c’est toujours de l’IA (machine learning non supervisé). Voici pourquoi :

Le modèle Isolation Forest est un algorithme d’apprentissage automatique non supervisé qui apprend à détecter des anomalies sans règles fixes préalables.

Il analyse la distribution des données dans un espace multi-dimensionnel (avec résistance, âge, formule encodée, slump, température) et identifie ce qui est « inhabituel » ou « rare ».

Le fait d’utiliser des seuils métier en plus (par exemple pour la visualisation ou validation) ne transforme pas la nature IA de la détection automatique. Ces seuils sont simplement une référence métier pour comparer les résultats IA.

Le cœur de la détection est toujours un modèle statistique adaptatif, pas un simple filtre fixe ou une règle prédéfinie.

En résumé :

La détection avec Isolation Forest = IA.

L’ajout des seuils métier pour visualiser ou comprendre les anomalies = support métier.

Tu combines donc un modèle IA + des règles métier pour l’interprétation, ce qui est très courant en pratique.