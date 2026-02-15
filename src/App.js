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

// Force le format 6 caractères (ex: 8856 -> 008856)
const formatUG = (val) => {
  let s = String(val || "").trim().replace(/\s/g, '');
  if (/^\d+$/.test(s) && s.length < 6) return s.padStart(6, '0');
  return s.toUpperCase();
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
            const json = XLSX.utils.sheet_to_json(wb.Sheets[sn], { defval: "" });
            all.push(...json.map(r => ({ ...r, _F: f })));
          });
        } catch (e) { console.error(e); }
      }
      setData(all);
      setLoading(false);
    };
    load();
  }, []);

  const result = useMemo(() => {
    const sU = formatUG(search.ug);
    const sH = search.hp2.trim().toUpperCase();
    if (!sU && !sH) return null;

    // 1. Trouver l'UG et son groupe associé (Fichier 4)
    let ugData = null;
    let currentHP2 = sH;

    if (sU) {
      ugData = data.find(r => formatUG(r['N° UG'] || r['UG']) === sU);
      if (ugData) {
        // On récupère le HP2 en colonne B (souvent 'GROUPE (HP2)')
        currentHP2 = String(ugData['GROUPE (HP2)'] || ugData['CODE_SITE'] || "").trim().toUpperCase();
      }
    }

    if (!currentHP2) return null;

    // 2. Calculer la somme SHA du groupe (Fichier 4 - Colonne L)
    const totalSHA = data
      .filter(r => r._F.includes("4") && String(r['GROUPE (HP2)'] || r['GROUPE'] || "").trim().toUpperCase() === currentHP2)
      .reduce((acc, r) => {
        const val = parseFloat(String(r['SURFACE HABITABLE (SHA)'] || r['SHA'] || 0).replace(',', '.'));
        return acc + (isNaN(val) ? 0 : val);
      }, 0);

    // 3. Récupérer les infos techniques
    const groupRows = data.filter(r => String(r['GROUPE (HP2)'] || r['HP2'] || "").trim().toUpperCase() === currentHP2);
    
    const findInfo = (keys) => {
      for (const r of groupRows) {
        for (const k of Object.keys(r)) {
          if (keys.some(tk => k.toUpperCase().includes(tk))) {
            const v = String(r[k]).trim();
            if (v && v !== "0" && v !== "N/A") return v;
          }
        }
      }
      return "N/C";
    };

    return {
      hp2: currentHP2,
      nom: findInfo(["NOM", "LIBELLE"]),
      adr: findInfo(["ADRESSE", "RUE"]),
      shaUG: ugData ? (ugData['SURFACE HABITABLE (SHA)'] || ugData['SHA'] || "N/A") : null,
      shaTotal: totalSHA.toFixed(2),
      equip: findInfo(["EQUIPEMENT", "CHAUFFAGE"]),
      nrj: findInfo(["ENERGIE", "COMBUSTIBLE"]),
      solaire: groupRows.some(r => r._F.includes("panneaux"))
    };
  }, [data, search]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20">
      <header className="bg-blue-700 p-5 shadow-lg flex justify-between items-center text-white">
        <div className="flex items-center gap-2 font-black uppercase tracking-tighter italic">
          <Building2 size={22} /> Socobat Patrimoine
        </div>
        <div className="text-[10px] font-bold bg-white/20 px-3 py-1 rounded-full uppercase">{data.length} LIGNES</div>
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-8">
        <div className="bg-white p-6 rounded-[32px] shadow-sm mb-8 flex flex-col md:flex-row gap-4">
          <input 
            placeholder="Numéro UG (ex: 015179)" 
            className="flex-1 p-4 bg-slate-100 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold text-blue-600"
            onChange={e => setSearch({...search, ug: e.target.value})}
          />
          <input 
            placeholder="Ou Code HP2 (ex: 119AL)" 
            className="flex-1 p-4 bg-slate-100 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold"
            onChange={e => setSearch({...search, hp2: e.target.value})}
          />
        </div>

        {loading ? <div className="text-center py-20 animate-pulse text-slate-400 font-bold uppercase text-xs">Analyse des fichiers...</div> : result && (
          <div className="bg-white rounded-[40px] shadow-xl overflow-hidden border-b-8 border-b-blue-700">
            <div className="p-8">
              <div className="flex gap-2 mb-4">
                <span className="bg-slate-900 text-white text-[9px] font-black px-2 py-1 rounded">GROUPE: {result.hp2}</span>
                {result.solaire && <span className="bg-orange-500 text-white text-[9px] font-black px-2 py-1 rounded uppercase flex items-center gap-1"><Sun size={10}/> Solaire</span>}
              </div>
              <h2 className="text-2xl font-black uppercase mb-8">{result.nom}</h2>

              <div className="grid md:grid-cols-2 gap-8 pt-6 border-t">
                <div className="space-y-6">
                  <div className="flex gap-3 text-slate-600 font-bold text-sm"><MapPin size={18} className="text-blue-600"/> {result.adr}</div>
                  <div className="bg-blue-600 text-white p-6 rounded-[30px] shadow-lg">
                    <p className="text-[9px] font-black uppercase opacity-60 border-b border-white/20 pb-2 mb-4 flex items-center gap-2"><ClipboardCheck size={14}/> Synthèse Surfaces (SHA)</p>
                    <div className="flex justify-between items-center mb-4 bg-white/10 p-3 rounded-xl">
                      <p className="text-[10px] font-bold uppercase">Logement {search.ug}</p>
                      <p className="text-2xl font-black">{result.shaUG} m²</p>
                    </div>
                    <div className="flex justify-between items-center px-2">
                      <div className="flex items-center gap-2">
                        <Calculator size={14} className="opacity-50"/>
                        <p className="text-[10px] font-bold uppercase tracking-widest">Total HP2 (Somme Col L)</p>
                      </div>
                      <p className="text-xl font-black">{result.shaTotal} m²</p>
                    </div>
                  </div>
                </div>
                <div className="bg-slate-50 p-6 rounded-[30px] border border-slate-100">
                  <p className="text-[10px] font-black uppercase text-blue-600 mb-4 flex items-center gap-2"><Zap size={14}/> Technique</p>
                  <p className="font-bold text-xs italic mb-4 text-slate-700">{result.equip}</p>
                  <div className="pt-4 border-t flex justify-between font-black text-[10px] uppercase">
                    <span className="text-slate-400">Énergie:</span> <span className="text-blue-600">{result.nrj}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
