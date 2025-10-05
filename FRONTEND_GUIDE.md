# 🎨 Frontend Development Guide - SpaceBio AI Platform

> Guide complet pour les développeurs frontend travaillant sur l'interface utilisateur de SpaceBio AI

**Dernière mise à jour** : Janvier 2025
**Version Backend** : Django 5.0
**Tech Stack Actuel** : TailwindCSS + Alpine.js + HTMX

---

## 📋 Table des Matières

1. [Vue d'ensemble du Projet](#vue-densemble-du-projet)
2. [Architecture Backend](#architecture-backend)
3. [Endpoints API Disponibles](#endpoints-api-disponibles)
4. [Fonctionnalités Principales](#fonctionnalités-principales)
5. [Contraintes et Règles Métier](#contraintes-et-règles-métier)
6. [Guidelines de Design](#guidelines-de-design)
7. [Exemples de Requêtes/Réponses](#exemples-de-requêtesréponses)
8. [Variables d'Environnement](#variables-denvironnement)
9. [Recommandations Techniques](#recommandations-techniques)

---

## 🌟 Vue d'ensemble du Projet

**SpaceBio AI Platform** est une plateforme d'intelligence scientifique spécialisée en biologie spatiale et recherche sur la microgravité.

### Objectif Principal
Permettre aux chercheurs de :
- Rechercher dans 572 articles scientifiques NASA/PMC
- Interagir avec un assistant AI spécialisé en biologie spatiale
- Synthétiser des rapports basés sur de vraies données de recherche
- Générer des revues de littérature

### Points Clés
- ✅ **Base de données** : 572 articles scientifiques indexés
- ✅ **Domaine** : Biologie spatiale, microgravité, santé des astronautes
- ✅ **Philosophie** : Synthèse de données réelles, PAS de génération fictive
- ✅ **IA** : OpenRouter (GPT-4) + Groq (Llama 3.3) avec fallback

---

## 🏗️ Architecture Backend

### Structure Django

```
spacebio/
├── core/                          # Application principale
│   ├── models.py                  # Models (Article, ChatSession, etc.)
│   ├── views.py                   # Views (home, search, chat, etc.)
│   ├── urls.py                    # URL routing
│   ├── services/
│   │   ├── ai_providers.py        # Interface OpenRouter/Groq
│   │   ├── embeddings.py          # Service de recherche sémantique
│   │   └── context_guard.py       # Validation de contexte
│   ├── management/commands/
│   │   ├── load_articles.py       # Import des articles CSV
│   │   └── generate_embeddings.py # Génération des embeddings
│   └── templates/core/            # Templates HTML actuels
├── Data/
│   └── SB_publication_PMC.csv     # Dataset de 608 articles NASA
├── db.sqlite3                     # Base de données SQLite
└── manage.py
```

### Models Principaux

```python
# Article scientifique
class Article:
    - title: str
    - authors: str
    - journal: str
    - publication_year: int
    - abstract: text
    - pmid: str (PubMed ID)
    - views_count: int

# Session de chat
class ChatSession:
    - session_id: UUID
    - messages: JSON (liste de messages)
    - created_at: datetime
    - is_active: bool

# Article généré/synthétisé
class GeneratedArticle:
    - title: str
    - content: text
    - topic: str
    - article_type: str (review/research/protocol)
    - length: str (short/medium/long)
    - style: str (academic/executive/technical)
    - generation_time_seconds: float

# Recherche sémantique
class ArticleEmbedding:
    - article: ForeignKey(Article)
    - embedding: JSON (vecteur 1536 dimensions)
    - created_at: datetime
```

---

## 🔌 Endpoints API Disponibles

### Base URL
```
http://localhost:8000
```

### 1️⃣ **Recherche d'Articles**

#### GET `/search/`
Recherche simple par mots-clés dans les titres et abstracts.

**Paramètres Query** :
- `q` : Terme de recherche (optionnel)
- `year` : Année de publication (optionnel)
- `search_type` : `simple` ou `semantic` (défaut: `simple`)

**Réponse** :
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Effects of Microgravity on Bone Density",
      "authors": "Smith, J., Doe, A.",
      "journal": "Journal of Space Biology",
      "publication_year": 2023,
      "abstract": "Abstract text...",
      "pmid": "12345678",
      "views_count": 15
    }
  ],
  "count": 1,
  "search_term": "microgravity bone"
}
```

---

### 2️⃣ **Chat AI Assistant**

#### GET `/chat/`
Affiche l'interface de chat (page HTML).

#### POST `/api/chat/message/`
Envoie un message au chat AI.

**Headers** :
```
Content-Type: application/json
```

**Body** :
```json
{
  "message": "What are the effects of microgravity on astronauts?",
  "session_id": "uuid-here"
}
```

**Réponse** :
```json
{
  "success": true,
  "response": "Microgravity has several significant effects on astronauts...",
  "session_id": "uuid-here",
  "sources_used": 3,
  "off_topic": false  // true si question hors-sujet
}
```

**⚠️ Comportement Important** :
- Si la question est hors-sujet (ex: "comment gagner de l'argent"), `off_topic: true`
- L'IA redirige poliment vers des sujets liés à la biologie spatiale
- Automatiquement cherche 3 articles pertinents pour enrichir la réponse

---

### 3️⃣ **Research Synthesis (anciennement Generate)**

#### GET `/generate/`
Affiche l'interface de synthèse de recherche.

#### POST `/api/generate/`
Synthétise un rapport basé sur les articles de la base de données.

**Headers** :
```
Content-Type: application/json
```

**Body** :
```json
{
  "topic": "Bone loss in microgravity",
  "type": "review",           // review, research, protocol
  "length": "medium",          // short (500w), medium (1000w), long (2000w)
  "style": "academic"          // academic, executive, technical
}
```

**Réponse (Success)** :
```json
{
  "success": true,
  "article": {
    "id": 42,
    "title": "Comprehensive Analysis of Bone Loss in Microgravity Environments",
    "content": "## Abstract\n\nBased on analysis of 5 research articles...\n\n## Introduction\n...",
    "synthesis_time": 28.5,
    "source_articles": 5,
    "note": "This synthesis is based on 5 research articles from our database."
  }
}
```

**Réponse (Erreur - Pas d'articles trouvés)** :
```json
{
  "success": false,
  "error": "No relevant research articles found for 'random topic'. This synthesis tool requires existing research articles from our database. Try a different topic or broader search terms related to space biology."
}
```

**Réponse (Erreur - Hors-sujet)** :
```json
{
  "success": false,
  "error": "Topic must be related to space biology research. I specialize in space biology and microgravity research. Could you ask about topics like astronaut health, microgravity effects, or space experiments?"
}
```

**⚠️ Contraintes CRITIQUES** :
- ✅ Minimum 1 article pertinent requis (sinon erreur 404)
- ✅ Topic doit être lié à la biologie spatiale (sinon erreur 400)
- ✅ Le contenu généré est une SYNTHÈSE, pas une invention
- ✅ Afficher clairement le nombre d'articles sources utilisés

---

### 4️⃣ **Détails d'un Article**

#### GET `/article/<int:article_id>/`
Affiche les détails d'un article.

**Réponse** : Page HTML

#### GET `/api/article/<int:article_id>/`
Retourne les données JSON d'un article.

**Réponse** :
```json
{
  "id": 1,
  "title": "Effects of Microgravity on Bone Density",
  "authors": "Smith, J., Doe, A.",
  "journal": "Journal of Space Biology",
  "publication_year": 2023,
  "abstract": "Full abstract text here...",
  "pmid": "12345678",
  "doi": "10.1234/jsb.2023.001",
  "views_count": 16
}
```

---

### 5️⃣ **Résumé AI d'un Article**

#### POST `/api/article/<int:article_id>/summarize/`
Génère un résumé AI d'un article.

**Body** :
```json
{
  "type": "concise"  // "concise" (100 mots) ou "detailed" (300 mots)
}
```

**Réponse** :
```json
{
  "success": true,
  "summary": "This study examines the effects of prolonged microgravity exposure on bone mineral density in astronauts...",
  "summary_type": "concise"
}
```

---

### 6️⃣ **Literature Review**

#### GET `/literature-review/`
Interface pour générer une revue de littérature.

#### POST `/api/literature-review/`
Génère une revue de littérature structurée.

**Body** :
```json
{
  "topic": "Cardiovascular adaptation to spaceflight",
  "min_year": 2015,
  "max_year": 2024,
  "max_articles": 10
}
```

**Réponse** :
```json
{
  "success": true,
  "review": {
    "id": 1,
    "title": "Literature Review: Cardiovascular adaptation to spaceflight",
    "content": "# Introduction\n\nThis review synthesizes findings from 8 research articles...",
    "article_count": 8,
    "generation_time": 45.2
  }
}
```

---

### 7️⃣ **Analytics**

#### GET `/analytics/`
Affiche le dashboard analytics.

**Données disponibles** :
- Total articles dans la base
- Total sessions de chat
- Total recherches effectuées
- Total synthèses générées
- Embeddings générés (pour recherche sémantique)

---

## ⚙️ Fonctionnalités Principales

### 1. **Recherche d'Articles** 🔍

**Deux modes** :
1. **Simple Search** : Recherche par mots-clés (gratuit, rapide)
2. **Semantic Search** : Recherche par similarité sémantique (nécessite embeddings)

**Filtres disponibles** :
- Terme de recherche
- Année de publication
- Type de recherche

**Affichage** :
- Liste des articles
- Tri par pertinence
- Compteur de vues
- Preview de l'abstract

---

### 2. **AI Assistant (Chat)** 💬

**Fonctionnalités** :
- ✅ Conversation contextuelle (garde 10 derniers messages)
- ✅ Validation automatique du contexte (filtre questions hors-sujet)
- ✅ Recherche automatique de 3 articles pertinents par question
- ✅ Réponses basées sur des articles réels
- ✅ Indicateur de sources utilisées

**Contraintes UX importantes** :
- Afficher clairement quand la question est hors-sujet
- Montrer le nombre de sources utilisées
- Conserver l'historique de la session
- Bouton "New Chat" pour recommencer

**Messages système** :
- ✅ "I specialize in space biology..." (redirection polie)
- ✅ "Based on 3 research articles..." (transparence sources)

---

### 3. **Research Synthesis** 🔬

**IMPORTANT** : Ce n'est PAS un générateur d'articles fictifs !

**Workflow** :
1. Utilisateur entre un topic
2. Système recherche minimum 5 articles pertinents
3. Si aucun article → Erreur claire
4. Synthèse basée UNIQUEMENT sur les articles trouvés
5. Affichage du nombre de sources

**Paramètres** :
- **Type** : Review, Research, Protocol
- **Length** : Short (500w), Medium (1000w), Long (2000w)
- **Style** : Academic, Executive, Technical

**UX Critique** :
```
❌ "Generate Article"
✅ "Synthesize Research"

❌ "AI is generating content..."
✅ "Analyzing 5 research articles..."

❌ "Article generated in 30s"
✅ "Synthesis based on 5 research articles | Completed in 30s"
```

---

### 4. **Literature Review** 📚

Génère une revue de littérature structurée sur un sujet donné.

**Paramètres** :
- Topic
- Plage d'années (min_year - max_year)
- Nombre max d'articles à inclure

**Structure du résultat** :
- Introduction
- Méthodologie
- Findings (par thème)
- Gaps identifiés
- Conclusions
- Références

---

## 🚨 Contraintes et Règles Métier

### Règle #1 : Domaine Strictement Spatial 🛸

**Topics acceptés** :
- Microgravité et biologie
- Santé des astronautes
- Expériences ISS
- Radiations cosmiques
- Adaptations physiologiques en espace
- Biologie végétale/animale spatiale
- Countermeasures pour vols spatiaux

**Topics REFUSÉS** :
- Finance, business (sauf si spatial)
- Cuisine, sport, divertissement
- Santé générale (non liée à l'espace)
- Technologie générale (sauf si spatiale)

**Implémentation frontend** :
- Afficher un message clair quand topic refusé
- Proposer des exemples de topics valides
- Ne pas laisser l'utilisateur attendre 30s pour une erreur

---

### Règle #2 : Pas d'Hallucination 🚫

**Synthèse de recherche** :
- ✅ TOUJOURS afficher le nombre d'articles sources
- ✅ Si 0 articles trouvés → Bloquer, ne pas générer
- ✅ Texte clair : "Based on X real research articles"
- ❌ Ne jamais dire "AI generated"
- ✅ Dire "Synthesized from database"

**Chat AI** :
- ✅ Afficher nombre de sources utilisées
- ✅ Encourager à demander les sources
- ✅ Admettre quand info manquante

---

### Règle #3 : Transparence des Sources 📊

**Chaque résultat doit montrer** :
- Nombre d'articles utilisés
- Temps de synthèse/recherche
- Type d'opération (synthesis, search, chat)

**Exemples UI** :
```
✅ Synthesis based on 5 research articles | 28.5s
✅ Response informed by 3 database articles
✅ Found 42 articles matching your query
```

---

## 🎨 Guidelines de Design

### Couleurs et Branding

**Palette actuelle** :
- Primary : Indigo (`#4F46E5`) - Boutons principaux
- Secondary : Purple (`#7C3AED`) - Gradients
- Success : Green (`#10B981`) - Validations
- Warning : Yellow (`#F59E0B`) - Avertissements
- Error : Red (`#EF4444`) - Erreurs

**Gradients** :
```css
background: linear-gradient(to right, #4F46E5, #7C3AED);
```

---

### Iconographie

**Recommandations** :
- 🚀 SpaceBio / Platform
- 🔍 Search
- 💬 Chat / AI Assistant
- 🔬 Research Synthesis
- 📚 Literature Review
- 📊 Analytics
- 🧪 Experiments / Research
- 🌌 Space / Microgravity
- 👨‍🚀 Astronaut Health

---

### Composants Principaux

#### Cards
```html
<div class="bg-white rounded-lg shadow-lg p-6">
  <!-- Content -->
</div>
```

#### Buttons
```html
<!-- Primary -->
<button class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold">
  Action
</button>

<!-- Secondary -->
<button class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg">
  Cancel
</button>
```

#### Loading States
```html
<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
```

---

### Responsive Design

**Breakpoints** (TailwindCSS) :
- `sm:` 640px
- `md:` 768px
- `lg:` 1024px
- `xl:` 1280px
- `2xl:` 1536px

**Mobile-First** :
- Priorité au mobile
- Stack cards verticalement sur petit écran
- Navigation hamburger < 768px

---

### UX Patterns Critiques

#### 1. Loading States (IMPORTANT)
```html
<!-- Pendant recherche d'articles -->
<div>
  <div class="spinner"></div>
  <p>Searching 572 research articles...</p>
</div>

<!-- Pendant synthèse -->
<div>
  <div class="spinner"></div>
  <p>Analyzing 5 research articles...</p>
  <p class="text-sm">Cross-referencing findings...</p>
</div>
```

#### 2. Success States
```html
<div class="bg-green-50 border border-green-200 rounded-lg p-4">
  <p class="text-green-800">
    ✅ Synthesis based on <strong>5</strong> research articles | 28.5s
  </p>
</div>
```

#### 3. Error States
```html
<!-- Pas d'articles trouvés -->
<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
  <p class="text-yellow-800">
    ⚠️ No relevant research found for this topic.
    Try broader terms related to space biology.
  </p>
</div>

<!-- Hors sujet -->
<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
  <p class="text-blue-800">
    💡 I specialize in space biology research.
    Ask about: astronaut health, microgravity effects, ISS experiments.
  </p>
</div>
```

---

## 📝 Exemples de Requêtes/Réponses

### Exemple 1 : Chat AI - Question Valide

**Requête** :
```bash
POST /api/chat/message/
{
  "message": "What happens to astronaut bones in space?",
  "session_id": "abc-123"
}
```

**Réponse** :
```json
{
  "success": true,
  "response": "Based on research from the ISS, astronauts experience significant bone density loss in microgravity, averaging 1-2% per month in weight-bearing bones like the spine and hips. This occurs because the lack of gravitational load reduces mechanical stress on bones, leading to decreased bone formation and increased bone resorption...",
  "session_id": "abc-123",
  "sources_used": 3,
  "off_topic": false
}
```

---

### Exemple 2 : Chat AI - Question Hors-Sujet

**Requête** :
```bash
POST /api/chat/message/
{
  "message": "How do I make money online?",
  "session_id": "abc-123"
}
```

**Réponse** :
```json
{
  "success": true,
  "response": "I specialize in space biology and microgravity research. Your question seems outside this domain. I focus on topics like: astronaut health, microgravity effects on organisms, ISS experiments, radiation biology, and countermeasures for spaceflight. Could you rephrase your question to relate to space biology research?",
  "session_id": "abc-123",
  "sources_used": 0,
  "off_topic": true
}
```

**UI Recommendation** :
```html
<div class="bg-blue-50 border-l-4 border-blue-400 p-4">
  <p class="text-blue-700">{{ response }}</p>
  <div class="mt-2">
    <p class="text-sm text-blue-600">Suggested topics:</p>
    <ul class="list-disc ml-5 text-sm text-blue-600">
      <li>Bone loss in microgravity</li>
      <li>Muscle atrophy in space</li>
      <li>Radiation effects on DNA</li>
    </ul>
  </div>
</div>
```

---

### Exemple 3 : Synthesis - Success

**Requête** :
```bash
POST /api/generate/
{
  "topic": "Cardiovascular deconditioning in spaceflight",
  "type": "review",
  "length": "medium",
  "style": "academic"
}
```

**Réponse** :
```json
{
  "success": true,
  "article": {
    "id": 15,
    "title": "Cardiovascular Deconditioning in Spaceflight: A Comprehensive Analysis",
    "content": "# Abstract\n\nBased on analysis of 5 peer-reviewed studies from our database...\n\n# Introduction\n\nCardiovascular deconditioning remains one of the primary health concerns...",
    "synthesis_time": 32.4,
    "source_articles": 5,
    "note": "This synthesis is based on 5 research articles from our database."
  }
}
```

---

### Exemple 4 : Synthesis - Pas d'Articles

**Requête** :
```bash
POST /api/generate/
{
  "topic": "Cooking pasta in zero gravity",
  "type": "review",
  "length": "medium",
  "style": "academic"
}
```

**Réponse** :
```json
{
  "success": false,
  "error": "No relevant research articles found for \"Cooking pasta in zero gravity\". This synthesis tool requires existing research articles from our database. Try a different topic or broader search terms related to space biology."
}
```

**UI Recommendation** :
```html
<div class="bg-yellow-50 border border-yellow-300 rounded-lg p-6">
  <div class="flex items-start">
    <span class="text-3xl mr-3">⚠️</span>
    <div>
      <h3 class="font-bold text-yellow-900 mb-2">No Research Articles Found</h3>
      <p class="text-yellow-800">{{ error }}</p>
      <div class="mt-4">
        <p class="font-semibold text-yellow-900">Try topics like:</p>
        <ul class="list-disc ml-5 text-yellow-800">
          <li>Microgravity effects on bone density</li>
          <li>Astronaut cardiovascular health</li>
          <li>Radiation exposure in space missions</li>
        </ul>
      </div>
    </div>
  </div>
</div>
```

---

## 🔐 Variables d'Environnement

**Fichier `.env`** (ne PAS commiter) :

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite par défaut, PostgreSQL pour production)
DATABASE_URL=sqlite:///db.sqlite3

# OpenRouter API (Primary)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Groq API (Fallback)
GROQ_API_KEY=gsk_xxxxx
GROQ_BASE_URL=https://api.groq.com/openai/v1

# AI Models
PRIMARY_AI_MODEL=gpt-4-turbo
FALLBACK_AI_MODEL=llama-3.3-70b-versatile

# OpenAI (pour embeddings seulement)
OPENAI_API_KEY=your-openai-api-key-here  # Optionnel
```

---

## 💡 Recommandations Techniques

### Framework Recommandés

**Option 1 : React + Next.js** ⭐ Recommandé
```bash
npx create-next-app@latest spacebio-frontend
```

**Avantages** :
- SSR pour SEO
- Routing file-based
- API routes intégrées
- Optimisation images
- TypeScript natif

**Libraries** :
- `axios` ou `fetch` : Requêtes API
- `react-query` : Cache et state management API
- `tailwindcss` : Styling
- `framer-motion` : Animations
- `react-markdown` : Affichage markdown
- `chart.js` ou `recharts` : Graphiques analytics

---

**Option 2 : Vue 3 + Nuxt**
```bash
npx nuxi@latest init spacebio-frontend
```

**Avantages** :
- Plus simple que React
- Performance excellente
- SSR natif avec Nuxt

---

**Option 3 : Svelte + SvelteKit**
```bash
npm create svelte@latest spacebio-frontend
```

**Avantages** :
- Bundle ultra-léger
- Syntaxe la plus simple
- Performance native

---

### Structure Projet Recommandée (Next.js)

```
spacebio-frontend/
├── app/
│   ├── page.tsx                 # Homepage
│   ├── search/page.tsx          # Search
│   ├── chat/page.tsx            # AI Chat
│   ├── synthesis/page.tsx       # Research Synthesis
│   └── analytics/page.tsx       # Analytics
├── components/
│   ├── ArticleCard.tsx          # Card article
│   ├── ChatMessage.tsx          # Message chat
│   ├── SearchBar.tsx            # Barre de recherche
│   ├── LoadingSpinner.tsx       # Loading states
│   └── ErrorBoundary.tsx        # Error handling
├── lib/
│   ├── api.ts                   # API client
│   ├── types.ts                 # TypeScript types
│   └── utils.ts                 # Utilities
├── public/
│   └── images/
└── styles/
    └── globals.css              # TailwindCSS
```

---

### TypeScript Types Recommandés

```typescript
// types.ts

export interface Article {
  id: number;
  title: string;
  authors: string;
  journal: string;
  publication_year: number;
  abstract: string;
  pmid: string;
  doi?: string;
  views_count: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  session_id: string;
  sources_used: number;
  off_topic: boolean;
}

export interface SynthesisRequest {
  topic: string;
  type: 'review' | 'research' | 'protocol';
  length: 'short' | 'medium' | 'long';
  style: 'academic' | 'executive' | 'technical';
}

export interface SynthesisResponse {
  success: boolean;
  article?: {
    id: number;
    title: string;
    content: string;
    synthesis_time: number;
    source_articles: number;
    note: string;
  };
  error?: string;
}

export interface SearchParams {
  q?: string;
  year?: number;
  search_type?: 'simple' | 'semantic';
}
```

---

### API Client Example

```typescript
// lib/api.ts
import axios from 'axios';
import type { Article, ChatResponse, SynthesisResponse } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Search
  searchArticles: async (params: SearchParams) => {
    const { data } = await apiClient.get('/search/', { params });
    return data;
  },

  // Chat
  sendChatMessage: async (message: string, sessionId: string) => {
    const { data } = await apiClient.post<ChatResponse>('/api/chat/message/', {
      message,
      session_id: sessionId,
    });
    return data;
  },

  // Synthesis
  synthesizeResearch: async (params: SynthesisRequest) => {
    const { data } = await apiClient.post<SynthesisResponse>('/api/generate/', params);
    return data;
  },

  // Article details
  getArticle: async (id: number) => {
    const { data } = await apiClient.get<Article>(`/api/article/${id}/`);
    return data;
  },

  // Summarize article
  summarizeArticle: async (id: number, type: 'concise' | 'detailed') => {
    const { data } = await apiClient.post(`/api/article/${id}/summarize/`, { type });
    return data;
  },
};
```

---

### State Management (React Query)

```typescript
// hooks/useChat.ts
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export const useChat = (sessionId: string) => {
  const { mutate: sendMessage, isLoading } = useMutation({
    mutationFn: (message: string) => api.sendChatMessage(message, sessionId),
    onSuccess: (data) => {
      if (data.off_topic) {
        // Handle off-topic warning
        console.warn('Question hors-sujet');
      }
    },
  });

  return { sendMessage, isLoading };
};

// hooks/useSearch.ts
export const useSearch = (params: SearchParams) => {
  return useQuery({
    queryKey: ['articles', params],
    queryFn: () => api.searchArticles(params),
    enabled: !!params.q, // Only run if search query exists
  });
};

// hooks/useSynthesis.ts
export const useSynthesis = () => {
  return useMutation({
    mutationFn: (params: SynthesisRequest) => api.synthesizeResearch(params),
    onError: (error: any) => {
      // Handle specific errors
      if (error.response?.status === 404) {
        console.error('No articles found');
      } else if (error.response?.status === 400) {
        console.error('Topic off-topic');
      }
    },
  });
};
```

---

## 🚀 Démarrage Rapide

### 1. Backend Setup
```bash
# Cloner le repo
git clone <repo-url>
cd 007

# Activer l'environnement virtuel
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Lancer le serveur Django
python manage.py runserver
```

Backend disponible sur : `http://localhost:8000`

---

### 2. Frontend Setup (Next.js)

```bash
# Créer le projet
npx create-next-app@latest spacebio-frontend --typescript --tailwind --app

cd spacebio-frontend

# Installer les dépendances
npm install axios @tanstack/react-query framer-motion react-markdown

# Créer .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Lancer le dev server
npm run dev
```

Frontend disponible sur : `http://localhost:3000`

---

## 🎯 Checklist de Développement

### Phase 1 : Setup
- [ ] Choisir le framework (React/Vue/Svelte)
- [ ] Setup projet avec TypeScript
- [ ] Configurer TailwindCSS
- [ ] Créer API client
- [ ] Définir les types TypeScript
- [ ] Tester connexion API backend

### Phase 2 : Pages Principales
- [ ] Homepage avec stats
- [ ] Search avec filtres
- [ ] Article detail view
- [ ] Chat interface
- [ ] Research Synthesis
- [ ] Analytics dashboard

### Phase 3 : Composants
- [ ] ArticleCard
- [ ] SearchBar
- [ ] ChatMessage
- [ ] LoadingSpinner
- [ ] ErrorBoundary
- [ ] Toast notifications

### Phase 4 : UX Avancée
- [ ] Loading states pour toutes les actions
- [ ] Error handling avec messages clairs
- [ ] Off-topic warnings dans chat
- [ ] Source count display partout
- [ ] Mobile responsive
- [ ] Animations (Framer Motion)

### Phase 5 : Optimisations
- [ ] Code splitting
- [ ] Image optimization
- [ ] Caching avec React Query
- [ ] SEO (meta tags)
- [ ] Analytics tracking
- [ ] Performance monitoring

---

## 📚 Ressources

### Documentation Backend
- Django Docs : https://docs.djangoproject.com/
- Django REST Framework : https://www.django-rest-framework.org/

### Documentation Frontend
- **Next.js** : https://nextjs.org/docs
- **React Query** : https://tanstack.com/query/latest
- **TailwindCSS** : https://tailwindcss.com/docs
- **Framer Motion** : https://www.framer.com/motion/

### Design Resources
- **Icons** : https://heroicons.com/ (TailwindCSS native)
- **Colors** : https://tailwindcolor.com/
- **Gradients** : https://uigradients.com/

---

## 🐛 Debugging

### Common Issues

**1. CORS Errors**
```python
# Backend: settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js default port
]
```

**2. API 404 Not Found**
Vérifier que le backend tourne sur port 8000 :
```bash
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Mac/Linux
```

**3. Type Errors TypeScript**
Toujours définir les interfaces dans `lib/types.ts`

---

## 📞 Support

**Questions Backend** :
- Vérifier `core/views.py` pour la logique métier
- Vérifier `core/urls.py` pour les routes
- Logs Django : Console du serveur

**Questions API** :
- Tester avec Postman ou Thunder Client
- Vérifier les headers (`Content-Type: application/json`)
- Vérifier le body JSON

**Questions Frontend** :
- Console browser (F12)
- Network tab pour voir les requêtes
- React DevTools

---

## ✅ Best Practices

1. **Toujours afficher le nombre de sources** dans les résultats AI
2. **Messages d'erreur clairs** avec suggestions d'actions
3. **Loading states informatifs** : "Analyzing 5 articles..." pas juste "Loading..."
4. **Mobile-first design**
5. **Accessibility** : ARIA labels, keyboard navigation
6. **Performance** : Lazy loading, code splitting
7. **SEO** : Meta tags, semantic HTML
8. **Testing** : Unit tests pour API calls

---

## 🎉 Conclusion

Ce guide devrait vous donner toutes les informations nécessaires pour développer une interface frontend moderne et professionnelle pour SpaceBio AI.

**Points clés à retenir** :
- ✅ Transparence des sources (toujours afficher le count)
- ✅ Validation du contexte (bloquer hors-sujet poliment)
- ✅ Pas d'hallucination (synthèse uniquement)
- ✅ UX claire et informative
- ✅ Mobile-responsive
- ✅ Performance optimale

**Bonne chance ! 🚀**

---

**Auteur** : SpaceBio Team
**Date** : Janvier 2025
**Version** : 1.0
**Contact** : [Votre contact]
