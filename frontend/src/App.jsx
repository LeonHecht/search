/*
 * Copyright 2025 Leon Hecht
 * Licensed under the Apache License, Version 2.0 (see LICENSE file)
 */

import React, { useState } from 'react';

export default function App() {
  const [query, setQuery] = useState('');
  const [useTransformer, setUseTransformer] = useState(false);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [queryLogId, setQueryLogId] = useState(null);
  const [feedbackById, setFeedbackById] = useState({});
  const [toast, setToast] = useState({ docId: null, msg: "" });
  // Track whether the info panel is open
  const [infoOpen, setInfoOpen] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const resp = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 30, use_transformer: useTransformer }),
      });

      if (!resp.ok) {
        const err = await resp.json();
        console.error('FastAPI validation error:', err);
        alert(`Search failed: ${err.detail?.[0]?.msg || resp.statusText}`);
        return;
      }

      const data = await resp.json();
      console.log('Search response:', data);
      // data has shape { query_log_id, results }
      setResults(data.results);
      setQueryLogId(data.query_log_id); // Store query_log_id for feedback
    } catch (err) {
      console.error('Fetch failed:', err);
      const text = await err.response?.text().catch(()=>'');
      console.error('Response body:', text);
      alert(`Search failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Helper to highlight query terms in snippet
  const renderSnippet = (snippet) => {
    const terms = Array.from(
      new Set(
      query
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .split(/[^A-Za-z]+/)
        .filter(Boolean)
    )
  );
    const words = snippet.split(' ');
    return words.map((word, idx) => {
      // strip accents
      const ascii = word
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
      // then remove non-word chars and lower-case
      const clean = ascii.replace(/[^A-Za-z]/g, '').toLowerCase();
      if (terms.includes(clean)) {
        return <strong key={idx} className="font-bold">{word} </strong>;
      }
      return <span key={idx}>{word} </span>;
    });
  };

  async function sendFeedback(documentId, positive) {
    try {
      // You’ll need to know the query_log_id from when you logged the search.
      // For simplicity, assume you stored it in state when you first fetched results.
      const payload = {
        query_log_id: queryLogId,  
        document_id: documentId,
        positive,
      };

      const resp = await fetch("/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) throw new Error(await resp.text());
      console.log("Feedback sent:", await resp.json());
      
      // mark this doc as liked/disliked
      setFeedbackById(prev => ({ ...prev, [documentId]: positive }));

      setToast({
        docId: documentId,
        msg: positive ? "Gracias por su feedback!" : "Gracias, vamos a mejorar!"
      });

      setTimeout(() => setToast({ docId: null, msg: "" }), 2000); // clear after 2 seconds
    
    } catch (err) {
      console.error("Feedback error:", err);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="w-full max-w-xl mx-auto bg-gray-100 p-8 md:p-14 rounded-2xl shadow-lg">
          {/* Title + Info toggle */}
          <h1 className="text-2xl font-bold text-gray-800 text-center">
            Buscador de Jurisprudencia de la Sala Penal (5000 documentos)
          </h1>
          <button
            onClick={() => setInfoOpen((o) => !o)}
            className="mt-4 text-gray-500 hover:text-gray-700 transition"
            aria-expanded={infoOpen}
            aria-label="Toggle about panel"
          >
            <span>ℹ️ Guía rápida</span>
          </button>

          {/* Info accordion */}
          <div
            className={`my-4 overflow-hidden transition-max-h duration-300 ${
              infoOpen ? 'max-h-96' : 'max-h-0'
            }`}
          >
            <p className="text-gray-700 text-sm leading-relaxed">
              🔍 Esta interfaz te permite buscar <strong>5,000 sentencias</strong> de 2011 a 2023 de la Sala Penal de la Corte Suprema de Justicia de Paraguay. Los documentos tienen los siguientes criterios:
            </p>
              <ul className="list-disc list-inside text-gray-700 text-sm mt-2">
                <li>Materia: <strong>Penal, Penal Adolescente</strong></li>
                <li>Tipo de resolución judicial: <strong>Acuerdos y Sentencias</strong>.</li>
                <li>Sala: <strong>Sala Penal</strong>.</li>
              </ul>
              <p className="text-gray-700 text-sm leading-relaxed mt-2"><strong>Puedes</strong>:</p>
            <ul className="list-disc list-inside text-gray-700 text-sm mt-2">
              <li>Usar búsqueda <strong>Exacta</strong> (BM25) para búsquedas basadas en coincidencia de palabras clave.</li>
              <li>Usar búsqueda <strong>Semántica</strong> (embeddings de transformer) para encontrar casos con significado semántico similar a la consulta.</li>
              <li>Escribir cualquier término o frase jurídica (p. ej. <em>“hurto agravado en Villarica”</em>) en el cuadro de búsqueda.</li>
            </ul>
            <p className="text-gray-600 text-xs mt-3 italic">
              💡 Consejo: las tildes se ignoran y las búsquedas no distinguen entre mayúsculas y minúsculas.
            </p>
          </div>
          {/* Toggle between BM25 (Exacta) and Transformer (Semantica) */}
          <div className="flex justify-center mb-4">
            <button
              title="Exacta: Búsqueda basada en coincidencia literal de palabras clave (BM25).
              Las palabras se neutralizan por acentos y se comparan sin distinción de mayúsculas/minúsculas."
              onClick={() => setUseTransformer(false)}
              className={`px-4 py-2 rounded-l-2xl border hover:shadow transition-colors ${!useTransformer ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
            >
              Exacta
            </button>
            <button
              title="Semántica: Búsqueda con comprensión contextual mediante embeddings (transformer)."
              onClick={() => setUseTransformer(true)}
              className={`px-4 py-2 rounded-r-2xl border hover:shadow transition-colors ${useTransformer ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
            >
              Semántica
            </button>
          </div>
          {/* 3) Make input+button stack on mobile */}
          <div className="mt-10 flex flex-col sm:flex-row gap-4">
            <div className={`input-wrapper flex-grow relative ${query ? 'caret-hidden' : ''}`}>
              <input
                type="text"
                className="w-full py-3 px-4 border rounded-2xl
                            focus:outline-none focus:placeholder-transparent
                            hover:bg-gray-50 transition-colors"
                placeholder="Ingresa las palabras de tu búsqueda..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
              <button
                onClick={handleSearch}
                className="flex-shrink-0 px-6 py-2 text-gray-700 bg-gray-200 rounded-3xl hover:bg-gray-100 transition-colors hover:shadow hover:text-gray-800"
                disabled={loading}
              >
                {loading ? 'Buscando...' : 'Buscar'}
              </button>
          </div>
          <ul className="mt-6 space-y-4">
            {results.map((res) => {
              const fb = feedbackById[res.id];
              const isToast = toast.docId === res.id;

              return (
                <li key={res.id} className="p-4 border rounded-lg hover:shadow">
                  <div className="relative">
                    <h2 className="text-lg font-semibold">{res.title}</h2>
                    <div className="flex justify-between items-center mt-1">
                      <p className="font-mono text-xs text-gray-500">ID: {res.id}</p>
                      <span className="text-sm font-semibold">
                        Score: {res.score.toFixed(3)}
                      </span>
                    </div>

                    {/* snippet around match */}
                    <p className="mt-2 text-gray-700 text-sm">
                      {renderSnippet(res.snippet)}
                      {res.snippet.split(' ').length >= 50 ? '…' : ''}
                    </p>

                    {/* download button, if available */}
                    {res.download_url && (
                      <a
                        href={res.download_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-block mt-3 px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-100 transition-colors hover:shadow hover:text-gray-800"
                      >
                        Download Full Case
                      </a>
                    )}
                    {/* Feedback buttons */}
                    <div className="absolute bottom-2 right-2 flex space-x-2">
                      <button
                        onClick={() => sendFeedback(res.id, true)}
                        className={`
                          "p-1 rounded-full transition hover:bg-green-100" +
                          ${fb === true
                            ? "bg-green-200 text-green-800"
                            : "hover:bg-green-100 text-gray-600"
                          }
                        `}
                        title="Like: Este documento es un buen resultado para mi consulta."
                        disabled={fb != null}
                      >
                        👍
                      </button>
                      <button
                        onClick={() => sendFeedback(res.id, false)}
                        className={`
                          "p-1 rounded-full transition hover:bg-red-100"
                        ${fb === false
                          ? "bg-red-200 text-red-800"
                          : "hover:bg-red-100 text-gray-600"
                        }
                        `}
                        title="Dislike: Este documento es NO un buen resultado para mi consulta."
                        disabled={fb != null}
                      >
                        👎
                      </button>
                    </div>
                    {isToast && (
                      <div
                        className="
                          absolute 
                          bottom-10 right-2      /* position above the buttons */
                          bg-white border border-gray-300
                          text-gray-800
                          px-3 py-1
                          rounded-md shadow-lg
                          animate-fade-in-out z-10
                        "
                      >
                        {toast.msg}
                      </div>
                    )}
                  </div>
                </li>
              )
            })}
          </ul>
        </div>
      </div>
    </div>
  );
}
