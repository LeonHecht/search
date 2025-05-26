import React, { useState } from 'react';

export default function App() {
  const [query, setQuery] = useState('');
  const [useTransformer, setUseTransformer] = useState(false);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

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
      setResults(data);
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


  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-100">
      <div className="w-full max-w-xl bg-gray-100 p-14 rounded-2xl shadow-lg">
        <h1 className="text-2xl font-bold mb-4 text-center mb-7">Legal Document Search</h1>
        {/* Toggle between BM25 (Exacta) and Transformer (Semantica) */}
        <div className="flex justify-center mb-4">
          <button
            onClick={() => setUseTransformer(false)}
            className={`px-4 py-2 rounded-l-2xl border ${!useTransformer ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            Exacta
          </button>
          <button
            onClick={() => setUseTransformer(true)}
            className={`px-4 py-2 rounded-r-2xl border ${useTransformer ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            Semántica
          </button>
        </div>
        <div className="flex gap-2">
          <div className={`input-wrapper flex-grow relative ${query ? 'caret-hidden' : ''}`}>
            <input
              type="text"
              className="w-full py-3 px-4 border rounded-2xl focus:outline-none focus:placeholder-transparent hover:bg-gray-50 transition-colors"
              placeholder="Enter your search query..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
            <button
              onClick={handleSearch}
              className="py-1 px-5 bg-slate-600 rounded-3xl hover:bg-slate-500 disabled:opacity-50 transition-colors hover:shadow text-white"
              disabled={loading}
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
        </div>
        <ul className="mt-6 space-y-4">
          {results.map((res) => (
            <li key={res.id} className="p-4 border rounded-lg hover:shadow">
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
                  className="inline-block mt-3 px-4 py-2 bg-slate-600 text-white rounded hover:bg-slate-500 text-sm"
                >
                  Download Full Case
                </a>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
