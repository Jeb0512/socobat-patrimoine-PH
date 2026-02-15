import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Building2, MapPin, Zap, Loader2, Sun, ClipboardCheck, Calculator } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

// Nettoyage et formatage strict (ex: " 15179 " -> "015179")
const normalize = (val) => {
  let s = String(val || "").trim().toUpperCase().replace(/\s/g, '');
  if (/^\d+$/.test(s) && s.length < 6) return s.padStart(6, '0');
  return s;
};

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState({ hp2: '', ug: '' });

  useEffect(() => {
    const load = async () => {
      let all = [];
      for (const f of FICHIERS_EXCEL) {
        try {
          const res = await fetch(`/${encodeURIComponent(f)}`);
          if (!res.ok) continue;
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          wb.SheetNames.forEach(sn => {
            // Lecture brute (header: 1) pour accéder aux colonnes par index numérique
            const rows = XLSX.utils.sheet_to_json(wb.Sheets[sn], { header: 1, defval: "" });
            // On transforme en objet mais on garde une trace de l'index des colonnes
            all.push(...rows.map(r => ({ _RAW_ARRAY: r, _F: f })));
          });
        } catch (e) { console.error(e); }
      }
      setData(all);
      setLoading(false);
    };
    load();
  }, []);

  const result = useMemo(() => {
    const sU = normalize(search.ug);
    const sH = search.hp2.trim().toUpperCase();
    if (!sU && !sH) return null;

    let targetHP2 = sH;
    let targetUGRow = null;

    // 1. RECHERCHE DE L'UG (Scan de toutes les colonnes de tous les fichiers)
    if (sU) {
      targetUGRow = data.find(r => 
        r._RAW_ARRAY.some(cell => normalize(cell) === sU)
      );
      if (targetUGRow) {
        // Si trouvé, on cherche le HP2 sur la même ligne (souvent Col B = index 1)
        targetHP2 = normalize(targetUGRow._RAW_ARRAY[1] || targetHP2);
      }
    }

    if (!targetHP2) return null;

    // 2. CALCUL DE LA SOMME (Fichier 4 uniquement)
    // On cible le fichier 4, on cherche targetHP2 en Col B (index 1) et on somme Col L (index 11)
    const rowsFile4 = data.filter(r => r._F.toLowerCase().includes("ug surfaces") || r._F.includes("4"));
    
    let sumSHA = 0;
    rowsFile4.forEach(r => {
      const rowHP2 = normalize(r._RAW_ARRAY[1]); // Colonne B
      if (rowHP2 === targetHP2) {
        const val = parseFloat(String(r._RAW_ARRAY[11]).replace(',', '.')); // Colonne L
        if (!isNaN(val)) sumSHA += val;
      }
    });

    // 3. INFOS TECHNIQUES (Scan large)
    const groupRows = data.filter(r => r._RAW_ARRAY.some(cell => normalize(cell) === targetHP2));
    
    const findInfo = (terms) => {
      for (const r of groupRows) {
        const lineStr = r._RAW_ARRAY.join(" ").toUpperCase();
        if (terms.some(t => lineStr.includes(t))) {
          // On cherche une cellule qui n'est pas le code HP2 lui-même
          return r._RAW_ARRAY.find(cell => 
            cell && cell !== targetHP2 && String(cell).length > 3
          ) || "N/C";
        }
      }
      return "N/C";
    };

    return {
      hp2: targetHP2,
      nom: findInfo(["ALSACE", "AUBERVILLIERS", "SOLIDARI", "NOM"]),
      adr: findInfo(["RUE", "AVENUE", "BOULEVARD", "ADRESSE"]),
      shaUG: targetUGRow ? (targetUGRow._RAW_ARRAY.find(cell => !isNaN(parseFloat(cell)) && cell > 5) || "N/A") : null,
      shaTotal: sumSHA.toFixed(2),
      equip: findInfo(["CHAUDIERE", "ECHANGEUR", "CPCU", "GAZ", "EQUIPEMENT"]),
      nrj: findInfo(["CPCU", "GAZ", "ELECTRICITE", "ENERGIE"])
    };
  }, [data, search]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20 font-sans">
      <header className="bg-blue-800 p-5 shadow-lg flex justify-between items-center text-white">
        <div className="flex items-center gap-2 font-black uppercase italic">
          <Building2 size={22} /> Socobat DPE
        </div>
        <div className="text-[10px] font-bold bg-white/10 px-3 py-1 rounded-full uppercase">Scanner Actif</div>
      </header>

      <main className="max-w-3xl mx-auto px-4 pt-8">
        <div className="bg-white p-6 rounded-[30px] shadow-xl mb-8 flex flex-col gap-4 border border-blue-50">
          <div>
            <label className="text-[10px] font-black text-blue-600 uppercase mb-1 block ml-2">Numéro d'UG (Recherche prioritaire)</label>
            <input 
              placeholder="Ex: 015179" 
              className="w-full p-4 bg-slate-100 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold text-lg"
              onChange={e => setSearch({...search, ug: e.target.value})}
            />
          </div>
          <div className="text-center text-slate-300 font-bold text-xs uppercase tracking-widest">OU</div>
          <div>
            <label className="text-[10px] font-black text-slate-400 uppercase mb-1 block ml-2">Code Groupe (HP2)</label>
            <input 
              placeholder="Ex: 119AL" 
              className="w-full p-4 bg-slate-100 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold"
              onChange={e => setSearch({...search, hp2: e.target.value})}
            />
          </div>
        </div>

        {!loading && result && (
          <div className="bg-white rounded-[40px] shadow-2xl overflow-hidden border border-slate-100">
            <div className="p-8">
              <div className="flex justify-between items-start mb-6">
                <span className="bg-slate-900 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase">HP2: {result.hp2}</span>
                <span className="text-blue-600 font-black text-[10px] uppercase tracking-widest">Résultat trouvé</span>
              </div>
              
              <h2 className="text-2xl font-black uppercase mb-2 leading-tight">{result.nom}</h2>
              <p className="flex items-center gap-2 text-slate-500 font-bold text-sm mb-8"><MapPin size={16} /> {result.adr}</p>

              <div className="grid gap-6">
                {/* BLOC SURFACES */}
                <div className="bg-blue-600 text-white p-8 rounded-[35px] shadow-lg shadow-blue-200">
                  <div className="flex items-center gap-2 mb-6 opacity-80 border-b border-white/20 pb-2 uppercase text-[10px] font-black">
                    <ClipboardCheck size={18}/> Données Surfaces HabitaBles (SHA)
                  </div>
                  <div className="flex justify-between items-center mb-6">
                    <p className="text-xs font-bold uppercase tracking-widest text-blue-100">Surface Logement (UG)</p>
                    <p className="text-3xl font-black">{result.shaUG} m²</p>
                  </div>
                  <div className="flex justify-between items-center pt-4 border-t border-white/10">
                    <div className="flex items-center gap-2">
                      <Calculator size={16} className="text-blue-200"/>
                      <p className="text-xs font-bold uppercase tracking-widest text-blue-100">Total Groupe (Somme Col L)</p>
                    </div>
                    <p className="text-xl font-black">{result.shaTotal} m²</p>
                  </div>
                </div>

                {/* BLOC TECHNIQUE */}
                <div className="bg-slate-50 p-6 rounded-[30px] border border-slate-100">
                  <p className="text-[10px] font-black uppercase text-blue-600 mb-3 flex items-center gap-2"><Zap size={14}/> Équipement Technique</p>
                  <p className="font-bold text-sm italic text-slate-700 leading-relaxed mb-4">{result.equip}</p>
                  <div className="flex justify-between font-black text-[10px] uppercase pt-4 border-t border-slate-200">
                    <span className="text-slate-400">Combustible</span>
                    <span className="text-blue-600">{result.nrj}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {loading && <div className="text-center py-20 animate-pulse font-black text-slate-300 uppercase tracking-widest">Chargement des 7085 données...</div>}
      </main>
    </div>
  );
}
