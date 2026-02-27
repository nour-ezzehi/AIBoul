# 🥖 RAG – Assistant Intelligent pour Fiches Techniques en Boulangerie

## 📌 Contexte

Dans le cadre d’un projet d’assistance à la formulation en boulangerie et pâtisserie, nous disposons d’un ensemble de fiches techniques (enzymes, améliorants, agents oxydants, etc.).

Ces fiches ont déjà été :

- Converties en texte  
- Découpées en fragments (chunks)  
- Transformées en embeddings  
- Stockées dans une base PostgreSQL (pgvector)  

L’objectif est de développer un module de **recherche sémantique (RAG – Retrieval Augmented Generation)** permettant d’interroger cette base vectorielle à partir d’une question en langage naturel.

---

# 🏗 Architecture du Système

## 🔎 Pipeline RAG

```text
Question utilisateur
        ↓
Embedding (all-MiniLM-L6-v2)
        ↓
Recherche vectorielle (PostgreSQL + pgvector)
        ↓
Top 3 fragments les plus similaires
        ↓
(Optionnel) LLM → Génération d’une réponse synthétique
---

## 🧠 Composants

### 1️⃣ Génération d’embedding

- Modèle : all-MiniLM-L6-v2  
- Bibliothèque : sentence-transformers  
- Dimension : 384  

L’embedding de la question est généré avec le même modèle que celui utilisé pour indexer les documents, garantissant la compatibilité dans l’espace vectoriel.

---

### 2️⃣ Base de données vectorielle

Base : PostgreSQL  
Extension : pgvector  

Table : embeddings

| Colonne         | Type          |
|----------------|--------------|
| id             | Primary Key  |
| id_document    | int          |
| texte_fragment | text         |
| vecteur        | VECTOR(384)  |

Les embeddings des fragments sont déjà stockés dans cette table.

---

### 3️⃣ Recherche par similarité

La similarité entre la question et les fragments est calculée via la similarité cosinus :

cos(θ) = (A · B) / (||A|| ||B||)

Les fragments sont :

- Classés par ordre décroissant de pertinence
- Limités aux 3 plus proches

---

### 4️⃣ (Optionnel) Génération avec LLM

Les fragments récupérés peuvent être injectés dans un modèle de langage afin de :

- Générer une réponse synthétique
- Fournir une explication contextualisée
- Améliorer l’expérience utilisateur

---

# ⚙️ Fonctionnalités du Prototype

✔ Question libre en langage naturel  
✔ Génération dynamique d’embedding  
✔ Interrogation PostgreSQL avec recherche vectorielle  
✔ Retour des 3 fragments les plus pertinents  
✔ Affichage des scores de similarité  
✔ Option d’activation du LLM  

---

# 🎯 Explication Technique (Pitch Court)

Le système implémente une architecture RAG industrielle.

Lorsqu’un utilisateur pose une question :

1. La question est encodée en un vecteur 384 dimensions via le modèle all-MiniLM-L6-v2.
2. Ce vecteur est comparé aux embeddings des fragments stockés dans PostgreSQL via l’extension pgvector.
3. La similarité cosinus est utilisée pour mesurer la proximité sémantique.
4. Les trois fragments les plus pertinents sont retournés.
5. Optionnellement, ces fragments sont transmis à un LLM pour générer une réponse synthétique contextualisée.

Cette approche permet une recherche basée sur la compréhension du sens, et non sur une simple correspondance lexicale.

---

# 🚀 Valeur Ajoutée

- Recherche sémantique avancée  
- Exploitation d’une base vectorielle industrielle  
- Architecture évolutive  
- Compatible avec des bases documentaires volumineuses  
- Extensible vers index ANN (HNSW / IVFFlat)  

---

# 🏁 Conclusion

Ce prototype démontre la mise en œuvre complète d’un module de Retrieval dans une architecture RAG, permettant une recherche intelligente et contextualisée au sein de fiches techniques en boulangerie et pâtisserie.
