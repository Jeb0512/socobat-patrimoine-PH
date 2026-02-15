import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Zap, Loader2, Building2, Sun, ClipboardCheck, Calculator } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

const clean = (v) => String(v || "").trim().toUpperCase().replace(/\s/g, '');

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Chargement...");
  const [search, setSearch] = useState({ hp2: '', ug: '' });

  useEffect(() => {
    const load = async () => {
      let all = [];
      for (const f of FICHIERS_EXCEL) {
        try {
          setStatus(`Lecture : ${f}`);
          const res = await fetch(`/${encodeURIComponent(f)}`);
          if (!res.ok) continue;
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          wb.SheetNames.forEach(sn => {
            const json = XLSX.utils.sheet_to_json(wb.Sheets[sn], { defval: 0 });
            all.push(...json.map(r => ({ ...r, _F: f })));
          });
        } catch (e) { console.error(e); }
      }
      setData(all);
      setLoading(false);
    };
    load();
  }, []);

  const results = useMemo(() => {
    const sH = clean(search.hp2);
    const sU = clean(search.ug);
    if (!sH && !sU) return [];

    // 1. Trouver le HP2 cible
    let targetHP2 = sH;
    let targetUGRow = null;

    if (sU) {
      // On cherche l'UG spécifiquement dans le fichier 4 (Surfaces UG)
      targetUGRow = data.find(r => clean(r['N° UG'] || r['UG']) === sU && r._F.includes("4"));
      if (targetUGRow) {
        // Le code HP2 est en colonne B (souvent 'GROUPE (HP2)')
        targetHP2 = clean(targetUGRow['GROUPE (HP2)'] || targetHP2);
      }
    }

    if (!targetHP2) return [];

    // 2. Filtrer toutes les lignes liées à ce groupe
    const allGroupRows = data.filter(r => clean(r['GROUPE (HP2)'] || r['HP2'] || r['CODE_HP2'] || r['GROUPE']) === targetHP2);

    // 3. CALCUL DE LA SOMME DES SURFACES HABITABLES (Fichier 4 - Colonne L)
    // On filtre le fichier 4 pour ce groupe et on additionne la colonne SHA
    const totalSHA = data
      .filter(r => r._F.includes("4") && clean(r['GROUPE (HP2)'] || r['GROUPE']) === targetHP2)
      .reduce((sum, r) => {
        const val = parseFloat(r['SURFACE HABITABLE (SHA)'] || r['SHA'] || 0);
        return sum + (isNaN(val) ? 0 : val);
      }, 0);

    const getBest = (keywords) => {
      for (const r of allGroupRows) {
        for (const k of Object.keys(r)) {
          if (keywords.some(tk => k.toUpperCase().includes(tk))) {
            const val = String(r[k]).trim();
            if (val && val !== "0" && val !== "N/A" && val !== "0.0") return val;
          }
        }
      }
      return "N/C";
    };

    return [{
      id: targetHP2,
      nom: getBest(["NOM", "LIBELLE"]),
      adr: getBest(["ADRESSE", "LOCALISATION", "RUE"]),
      shaTotal: totalSHA.toFixed(2),
      shaUG: targetUGRow ? (targetUGRow['SURFACE HABITABLE (SHA)'] || targetUGRow['SHA'] || "N/C") : null,
      ugID: sU || null,
      equip: getBest(["EQUIPEMENT", "SYSTEME", "CHAUFFAGE", "CHAUDIERE"]),
      energie: getBest(["ENERGIE", "COMBUSTIBLE", "TYPE"]),
      sol: allGroupRows.some(r => r._F.includes("panneaux")),
      ind: allGroupRows.some(r => r._F.includes("individuel"))
    }];
  }, [data, search]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans pb-20">
      <header className="bg-[#1E40AF] p-5 shadow-xl sticky top-0 z-50 flex justify-between items-center text-white">
        <div className="flex items-center gap-2">
          <Building2 size={24} />
          <h1 className="font-black text-lg uppercase tracking-tighter italic">Socobat PH <span className="text-blue-300 not-italic font-medium">| DPE</span></h1>
        </div>
        <div className="text-[10px] font-bold bg-white/20 px-3 py-1 rounded-full uppercase tracking-widest">{data.length} LIGNES</div>
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-8">
        <div className="bg-white p-6 rounded-[32px] shadow-sm mb-8 flex flex-col md:flex-row gap-4 border border-slate-100">
          <div className="flex-1">
            <label className="text-[10px] font-black text-slate-400 uppercase ml-2 mb-1 block">Groupe HP2</label>
            <input placeholder="ex: 119AL" className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold" onChange={e => setSearch({...search, hp2: e.target.value})} />
          </div>
          <div className="flex-1">
            <label className="text-[10px] font-black text-blue-500 uppercase ml-2 mb-1 block">N° UG (6 chiffres)</label>
            <input placeholder="ex: 151799" className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold text-blue-600" onChange={e => setSearch({...search, ug: e.target.value})} />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center py-20 text-slate-400 font-bold uppercase text-xs tracking-widest animate-pulse"><Loader2 className="animate-spin mb-2" /> Calcul en cours...</div>
        ) : (
          <div className="space-y-6">
            {results.map((r, i) => (
              <div key={i} className="bg-white rounded-[40px] shadow-sm border border-slate-100 overflow-hidden border-b-8 border-b-blue-600">
                <div className="p-8">
                  <div className="flex gap-2 mb-4">
                    <span className="bg-slate-900 text-white text-[9px] font-black px-3 py-1 rounded">ID: {r.id}</span>
                    {r.sol && <span className="bg-orange-500 text-white text-[9px] font-black px-2 py-1 rounded uppercase flex items-center gap-1"><Sun size={10}/> Solaire</span>}
                  </div>

                  <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tighter mb-8 leading-none">{r.nom}</h2>

                  <div className="grid md:grid-cols-2 gap-8 pt-6 border-t border-slate-100">
                    <div className="space-y-6">
                      <div className="flex gap-4">
                        <MapPin size={20} className="text-blue-500 shrink-0" />
                        <p className="font-bold text-slate-600 text-sm leading-tight">{r.adr}</p>
                      </div>

                      <div className="bg-[#2563EB] text-white p-7 rounded-[35px] shadow-xl">
                        <div className="flex items-center gap-2 mb-5 opacity-70 border-b border-white/20 pb-2 uppercase text-[9px] font-black">
                           <ClipboardCheck size={14}/> Surfaces HabitaBles (SHA)
                        </div>
                        
                        <div className="flex justify-between items-center mb-6 bg-white/10 p-4 rounded-2xl border border-white/10">
                           <div>
                              <p className="text-[10px] font-black uppercase tracking-wider">Surface Logement</p>
                              <p className="text-[9px] opacity-70 italic">UG {r.ug || "--"}</p>
                           </div>
                           <p className="text-3xl font-black tracking-tighter">{r.shaUG ? `${r.shaUG} m²` : '--'}</p>
                        </div>

                        <div className="flex justify-between items-center px-4">
                           <div className="flex items-center gap-2">
                              <Calculator size={14} className="opacity-60" />
                              <div>
                                 <p className="text-[10px] font-black uppercase tracking-wider">Total Groupe</p>
                                 <p className="text-[9px] opacity-70 italic">Somme de toutes les UG</p>
                              </div>
                           </div>
                           <p className="text-xl font-black tracking-tighter">{r.shaTotal} m²</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-50 p-6 rounded-[32px] border border-slate-100 h-fit">
                      <p className="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-4 flex items-center gap-2"><Zap size={14}/> Technique</p>
                      <p className="font-bold text-slate-800 text-xs leading-relaxed mb-6 italic">{r.equip}</p>
                      <div className="border-t border-slate-200 pt-4 flex justify-between font-black text-[10px] uppercase">
                         <span className="text-slate-400">Énergie :</span>
                         <span className="text-blue-600 font-black">{r.energie}</span>
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
