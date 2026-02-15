import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Zap, Loader2, Building2, Layers, Sun, ClipboardCheck } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

// Nettoyeur universel de codes (HP2 ou UG)
const cleanCode = (val) => {
  if (!val) return "";
  let s = String(val).trim().toUpperCase().replace(/\s/g, '');
  // Si c'est un code UG numérique, on le force sur 6 caractères
  if (/^\d+$/.test(s) && s.length <= 6) return s.padStart(6, '0');
  return s;
};

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Chargement...");
  const [filters, setFilters] = useState({ hp2: '', ug: '' });

  useEffect(() => {
    const loadAll = async () => {
      let all = [];
      for (const file of FICHIERS_EXCEL) {
        try {
          setStatus(`Lecture : ${file}`);
          const res = await fetch(`/${encodeURIComponent(file)}`);
          if (!res.ok) continue;
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          wb.SheetNames.forEach(sheet => {
            const json = XLSX.utils.sheet_to_json(wb.Sheets[sheet], { defval: "" });
            all.push(...json.map(row => {
              const cleanedRow = {};
              // On indexe chaque ligne avec des clés simplifiées
              Object.keys(row).forEach(k => {
                cleanedRow[k.trim().toUpperCase()] = String(row[k]).trim();
              });
              return { ...cleanedRow, _RAW: row, _FILE: file };
            }));
          });
        } catch (e) { console.error(e); }
      }
      setData(all);
      setLoading(false);
    };
    loadAll();
  }, []);

  const consolidatedResults = useMemo(() => {
    const sHP2 = cleanCode(filters.hp2);
    const sUG = cleanCode(filters.ug);

    if (!sHP2 && !sUG) return [];

    // 1. Trouver le code HP2 de référence
    let activeHP2 = sHP2;
    let activeUGData = null;

    if (sUG) {
      // Si on cherche une UG, on scanne tous les fichiers pour trouver le HP2 associé
      const ugRow = data.find(row => {
        return Object.keys(row).some(k => 
          (k.includes("UG") || k.includes("UNIT")) && cleanCode(row[k]) === sUG
        );
      });
      if (ugRow) {
        activeUGData = ugRow;
        // On cherche le HP2 dans cette même ligne
        const hp2Key = Object.keys(ugRow).find(k => k.includes("HP2") || k.includes("GROUPE"));
        if (hp2Key) activeHP2 = cleanCode(ugRow[hp2Key]);
      }
    }

    if (!activeHP2) return [];

    // 2. Récupérer TOUTES les lignes de TOUS les fichiers pour ce HP2
    const groupRows = data.filter(row => {
      return Object.keys(row).some(k => 
        (k.includes("HP2") || k.includes("GROUPE")) && cleanCode(row[k]) === activeHP2
      );
    });

    // 3. Extraire les meilleures données (Fusion)
    const findBest = (terms) => {
      for (const row of groupRows) {
        for (const k of Object.keys(row)) {
          if (terms.some(t => k.includes(t))) {
            const v = row[k];
            if (v && v !== "0" && v !== "N/A" && v !== "0.0") return v;
          }
        }
      }
      return "N/C";
    };

    return [{
      hp2: activeHP2,
      nom: findBest(["NOM", "LIBELLE"]),
      adresse: findBest(["ADRESSE", "LOCALISATION", "RUE"]),
      // Surface globale (Fichier 3 ou 1)
      surfTotal: findBest(["SURFACE CHAUFFEE", "SCH", "SUT", "SURFACE_UTILE"]),
      // Surface spécifique de l'UG si recherchée
      surfUG: activeUGData ? (activeUGData["SURFACE HABITABLE (SHA)"] || activeUGData["SHA"] || activeUGData["SURFACE"]) : null,
      ugID: sUG || null,
      equip: findBest(["EQUIPEMENT", "SYSTEME", "CHAUFFAGE", "DESIGNATION", "DESCRIPTIF"]),
      energie: findBest(["ENERGIE", "COMBUSTIBLE", "TYPE"]),
      isSolaire: groupRows.some(r => r._FILE.includes("panneaux")),
      isIndividuel: groupRows.some(r => r._FILE.includes("individuel"))
    }];
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 pb-20 font-sans">
      <header className="bg-blue-600 p-6 shadow-xl sticky top-0 z-50 flex justify-between items-center text-white">
        <div className="flex items-center gap-3">
          <Building2 size={24} />
          <h1 className="font-black text-xl uppercase italic">Socobat PH</h1>
        </div>
        <div className="text-[10px] font-bold bg-black/20 px-3 py-1 rounded-full uppercase">{data.length} Lignes</div>
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-10">
        {/* BLOC RECHERCHE */}
        <div className="bg-white p-8 rounded-[40px] shadow-2xl shadow-blue-900/10 mb-10 flex flex-col md:flex-row gap-6">
          <div className="flex-1">
            <label className="text-[10px] font-black text-slate-400 uppercase mb-2 block ml-2">Code Groupe (HP2)</label>
            <input 
              placeholder="Ex: 119AL" 
              className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-4 focus:ring-blue-500/10 font-bold"
              onChange={e => setFilters({...filters, hp2: e.target.value})}
            />
          </div>
          <div className="flex-1">
            <label className="text-[10px] font-black text-blue-400 uppercase mb-2 block ml-2">N° UG (Logement)</label>
            <input 
              placeholder="Ex: 015179" 
              className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-4 focus:ring-blue-500/10 font-bold text-blue-600"
              onChange={e => setFilters({...filters, ug: e.target.value})}
            />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center py-20"><Loader2 className="animate-spin text-blue-600" size={40} /></div>
        ) : (
          <div className="space-y-8">
            {consolidatedResults.map((r, i) => (
              <div key={i} className="bg-white rounded-[45px] shadow-sm border border-slate-200 overflow-hidden border-b-8 border-b-blue-600">
                <div className="p-10">
                  <div className="flex gap-2 mb-4">
                    <span className="bg-slate-900 text-white text-[10px] font-black px-3 py-1 rounded-lg">ID: {r.hp2}</span>
                    {r.isSolaire && <span className="bg-orange-500 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase flex items-center gap-1"><Sun size={12}/> Solaire</span>}
                  </div>
                  <h3 className="text-3xl font-black text-slate-900 uppercase tracking-tighter mb-10 leading-none">{r.nom}</h3>
                  <div className="grid md:grid-cols-2 gap-10">
                    <div className="space-y-8">
                      <div className="flex gap-4">
                        <MapPin size={24} className="text-blue-600 shrink-0" />
                        <p className="font-bold text-slate-700 text-lg leading-tight">{r.adresse}</p>
                      </div>
                      <div className="bg-blue-600 text-white p-8 rounded-[40px] shadow-xl">
                        <div className="flex items-center gap-2 mb-6 opacity-60 border-b border-white/20 pb-2 uppercase text-[9px] font-black"><ClipboardCheck size={16}/> Synthèse DPE</div>
                        <div className="flex justify-between items-end mb-6">
                           <p className="text-xs font-bold uppercase tracking-tighter">Surface Logement <span className="block opacity-60 text-[8px]">UG: {r.ugID || "N/C"}</span></p>
                           <p className="text-3xl font-black">{r.surfUG ? `${r.surfUG} m²` : '--'}</p>
                        </div>
                        <div className="flex justify-between items-end">
                           <p className="text-xs font-bold uppercase tracking-tighter">Surface Groupe <span className="block opacity-60 text-[8px]">Ensemble HP2</span></p>
                           <p className="text-xl font-black">{r.surfTotal} m²</p>
                        </div>
                      </div>
                    </div>
                    <div className="bg-slate-50 p-8 rounded-[40px] border border-slate-100 h-fit">
                      <p className="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-4 flex items-center gap-2"><Zap size={16}/> Chaufferie</p>
                      <p className="font-bold text-slate-800 text-sm leading-relaxed mb-6 italic">{r.equip}</p>
                      <div className="border-t border-slate-200 pt-4 flex justify-between font-black text-[10px] uppercase">
                         <span className="text-slate-400">Énergie :</span>
                         <span className="text-blue-600">{r.energie}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
