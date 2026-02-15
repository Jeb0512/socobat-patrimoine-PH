import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Thermometer, Zap, Loader2, Building2, AlertTriangle, Sun, Home, Layers } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Initialisation...");
  const [filters, setFilters] = useState({ search: '' });

  useEffect(() => {
    const loadData = async () => {
      let rawData = [];
      for (const file of FICHIERS_EXCEL) {
        try {
          setStatus(`Lecture : ${file}`);
          const res = await fetch(`/${encodeURIComponent(file)}`);
          if (!res.ok) continue;
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          
          wb.SheetNames.forEach(sheet => {
            const json = XLSX.utils.sheet_to_json(wb.Sheets[sheet], { defval: "" });
            rawData.push(...json.map(row => {
              // Standardisation de toutes les clés en MAJUSCULES et SANS ESPACES
              const cleanRow = {};
              Object.keys(row).forEach(k => {
                const cleanKey = k.trim().toUpperCase()
                  .replace(/ /g, '_')
                  .replace(/\(/g, '')
                  .replace(/\)/g, '')
                  .replace(/N°/g, 'N');
                cleanRow[cleanKey] = String(row[k]).trim();
              });
              return { ...cleanRow, _SOURCE: file };
            }));
          });
        } catch (e) { console.error(e); }
      }
      setData(rawData);
      setLoading(false);
    };
    loadData();
  }, []);

  const results = useMemo(() => {
    const s = filters.search.toLowerCase().trim();
    if (!s) return [];

    // 1. Trouver tous les Groupes ou UG correspondant à la recherche
    const matches = data.filter(item => {
      const hp2 = (item.GROUPE_HP2 || item.HP2 || item.CODE_HP2 || "").toLowerCase();
      const ug = (item.N_UG || item.UG || "").toLowerCase();
      return hp2.includes(s) || ug.includes(s);
    });

    // 2. Grouper les informations par Code HP2 pour fusionner les fichiers
    const grouped = {};
    matches.forEach(item => {
      const id = item.GROUPE_HP2 || item.HP2 || item.CODE_HP2 || "INCONNU";
      if (!grouped[id]) grouped[id] = { hp2: id, docs: [] };
      grouped[id].docs.push(item);
    });

    return Object.values(grouped).map(group => {
      const findVal = (keys) => {
        for (const doc of group.docs) {
          for (const k of keys) { if (doc[k]) return doc[k]; }
        }
        return "";
      };

      return {
        hp2: group.hp2,
        nom: findVal(['NOM_GROUPE', 'NOM']),
        adresse: findVal(['ADRESSE', 'LOCALISATION', 'ADRESSE_COMPLETE']),
        surface: findVal(['SURFACE_CHAUFFEE_SCH', 'SCH', 'SURFACE']),
        equipement: findVal(['EQUIPEMENT', 'SYSTEME_CHAUFFAGE', 'DESIGNATION', 'MARQUE', 'MARQUE_DE_TYPE_VITOSOL']),
        energie: findVal(['TYPE_COMBUSTIBLE', 'ENERGIE', 'TYPE_ENERGIE']),
        isSolaire: group.docs.some(d => d._SOURCE.includes("panneaux")),
        isIndividuel: group.docs.some(d => d._SOURCE.includes("individuel")),
        ug: group.docs.find(d => d.N_UG)?.N_UG || ""
      };
    });
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 font-sans pb-20">
      <header className="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-100 p-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2.5 rounded-2xl text-white shadow-lg shadow-blue-200"><Building2 size={24}/></div>
            <h1 className="font-black text-xl tracking-tighter uppercase">Socobat <span className="text-blue-600">PH</span></h1>
          </div>
          <div className="text-[10px] font-bold bg-slate-100 px-3 py-1.5 rounded-full text-slate-500 uppercase tracking-widest">
            {loading ? "Chargement..." : `${data.length} Entrées`}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-8">
        <div className="relative mb-12">
          <input 
            placeholder="Rechercher une UG ou un Groupe (ex: 119AL, HP2-045...)" 
            className="w-full p-6 bg-white rounded-[32px] shadow-2xl shadow-blue-900/5 outline-none focus:ring-4 focus:ring-blue-100 transition-all text-lg font-medium pr-16 border border-slate-50"
            onChange={e => setFilters({search: e.target.value})}
          />
          <div className="absolute right-6 top-6 text-blue-600"><Search size={28}/></div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <Loader2 className="animate-spin mb-4" size={48} />
            <p className="font-bold uppercase tracking-widest text-xs">{status}</p>
          </div>
        ) : (
          <div className="space-y-6">
            {results.map((r, i) => (
              <div key={i} className="bg-white rounded-[40px] p-8 border border-slate-50 shadow-sm hover:shadow-xl transition-all group">
                <div className="flex justify-between items-start mb-8">
                  <div>
                    <div className="flex gap-2 mb-3">
                      <span className="bg-blue-50 text-blue-600 text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-tighter">Groupe {r.hp2}</span>
                      {r.isSolaire && <span className="bg-orange-50 text-orange-600 text-[10px] font-black px-3 py-1 rounded-full uppercase flex items-center gap-1"><Sun size={12}/> Solaire</span>}
                      {r.isIndividuel ? 
                        <span className="bg-purple-50 text-purple-600 text-[10px] font-black px-3 py-1 rounded-full uppercase">Individuel</span> :
                        <span className="bg-emerald-50 text-emerald-600 text-[10px] font-black px-3 py-1 rounded-full uppercase">Collectif</span>
                      }
                    </div>
                    <h2 className="text-2xl font-black text-slate-900 uppercase leading-none tracking-tighter">{r.nom || "Groupe sans nom"}</h2>
                  </div>
                  {r.ug && <div className="text-right bg-slate-900 text-white p-4 rounded-3xl shadow-lg">
                    <p className="text-[10px] font-bold opacity-50 uppercase mb-1">Code UG</p>
                    <p className="text-lg font-black leading-none">{r.ug}</p>
                  </div>}
                </div>

                <div className="grid md:grid-cols-2 gap-8 border-t border-slate-50 pt-8">
                  <div className="space-y-5">
                    <div className="flex gap-4 items-start">
                      <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl"><MapPin size={20}/></div>
                      <div>
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Localisation</p>
                        <p className="font-bold text-slate-700 leading-snug">{r.adresse || "Adresse non listée"}</p>
                      </div>
                    </div>
                    <div className="flex gap-4 items-center">
                      <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl"><Layers size={20}/></div>
                      <div>
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Surface Chauffée</p>
                        <p className="font-bold text-slate-700">{r.surface || "N/C"} m²</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-50 rounded-[32px] p-6 relative overflow-hidden">
                    <div className="flex items-center gap-3 mb-4">
                      <Zap className="text-blue-600" size={20}/>
                      <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Centrale Thermique</p>
                    </div>
                    <p className="font-bold text-slate-700 text-sm leading-relaxed mb-4">{r.equipement || "Détails techniques en cours de saisie..."}</p>
                    <div className="flex justify-between items-center border-t border-slate-200/50 pt-4 mt-2">
                       <span className="text-[10px] font-black text-blue-600 uppercase tracking-tighter">{r.energie || "Énergie N/C"}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {filters.search && results.length === 0 && (
              <div className="text-center py-20 bg-white rounded-[40px] border-2 border-dashed border-slate-100">
                <p className="text-slate-400 font-bold uppercase tracking-widest text-sm">Aucun patrimoine trouvé</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
