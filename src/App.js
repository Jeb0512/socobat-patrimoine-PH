import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Thermometer, Zap, Calendar, Loader2, Info } from 'lucide-react';

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ groupe: '', ug: '' });

  // 1. Chargement du fichier Excel
  useEffect(() => {
    fetch('/base_ug.xlsx')
      .then(res => {
        if (!res.ok) throw new Error("Fichier Excel introuvable");
        return res.arrayBuffer();
      })
      .then(ab => {
        const wb = XLSX.read(ab);
        const ws = wb.Sheets[wb.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(ws);
        setData(jsonData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  // 2. Logique de recherche (insensible à la casse)
  const filteredResults = useMemo(() => {
    return data.filter(item => {
      const g = String(item.GROUPE || '').toLowerCase();
      const u = String(item['N°UG'] || '').toLowerCase();
      const searchG = filters.groupe.toLowerCase().trim();
      const searchU = filters.ug.toLowerCase().trim();
      return g.includes(searchG) && u.includes(searchU);
    });
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-[#F5F7FA] text-[#4A4A4A] font-sans pb-12">
      {/* Header Style Alan */}
      <header className="bg-white p-8 border-b border-gray-100 shadow-sm mb-8 text-center md:text-left">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-3xl font-bold text-[#3A7AFE] tracking-tight">Socobat Patrimoine PH</h1>
          <p className="text-gray-400 mt-2 font-medium">Recherche technique des Unités de Gestion</p>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4">
        {/* Formulaire de recherche */}
        <div className="bg-white p-6 rounded-[28px] shadow-sm mb-10 flex flex-col md:flex-row gap-4 items-end border border-gray-50">
          <div className="flex-1 w-full text-left">
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2 ml-1">Groupe (HP2)</label>
            <input 
              placeholder="Ex: HP2-045..." 
              className="w-full p-4 bg-[#F5F7FA] rounded-2xl outline-none focus:ring-2 focus:ring-[#3A7AFE] transition-all"
              onChange={e => setFilters({...filters, groupe: e.target.value})}
            />
          </div>
          <div className="flex-1 w-full text-left">
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2 ml-1">N° UG</label>
            <input 
              placeholder="Ex: 1204..." 
              className="w-full p-4 bg-[#F5F7FA] rounded-2xl outline-none focus:ring-2 focus:ring-[#3A7AFE] transition-all"
              onChange={e => setFilters({...filters, ug: e.target.value})}
            />
          </div>
        </div>

        {/* Affichage des résultats */}
        {loading ? (
          <div className="flex flex-col items-center py-20">
            <Loader2 className="animate-spin text-[#3A7AFE] mb-4" size={40} />
            <p className="text-gray-500 font-medium">Analyse du fichier Excel...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredResults.length > 0 ? (
              filteredResults.map((u, i) => (
                <div key={i} className="bg-white p-8 rounded-[24px] shadow-sm border border-transparent hover:border-blue-100 transition-all hover:shadow-md">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="font-bold text-xl text-gray-800">{u.GROUPE || 'Groupe inconnu'}</h3>
                      <p className="text-sm text-gray-400 font-medium">Réf: {u['N°UG'] || 'N/A'}</p>
                    </div>
                    <span className="bg-[#3A7AFE] text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-sm">
                      UG Actif
                    </span>
                  </div>

                  <div className="space-y-4 border-t border-gray-50 pt-6">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 rounded-lg text-[#3A7AFE]"><MapPin size={18}/></div>
                      <span className="text-sm font-medium">{u.ADRESSE || 'Adresse non renseignée'}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 rounded-lg text-[#3A7AFE]"><Zap size={18}/></div>
                      <span className="text-sm font-medium">{u.SCH ? `${u.SCH} m² chauffés` : 'Surface non renseignée'}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 rounded-lg text-[#3A7AFE]"><Thermometer size={18}/></div>
                      <span className="text-sm font-medium">{u.SYSTEME_CHAUFFAGE || 'Système inconnu'} ({u.ENERGIE || 'Energie N/C'})</span>
                    </div>
                    <div className="flex items-center gap-3 text-gray-400">
                      <div className="p-2 bg-gray-50 rounded-lg"><Info size={18}/></div>
                      <span className="text-sm font-medium italic">{u.MARQUE || 'Marque non précisée'} - {u.DATE_MES || 'Date N/C'}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full bg-white p-12 rounded-[24px] text-center text-gray-400 border border-dashed border-gray-200">
                Aucun résultat trouvé pour votre recherche.
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
