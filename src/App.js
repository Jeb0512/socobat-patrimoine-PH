import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Zap, Loader2, Building2, Sun, ClipboardCheck, Info } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

const clean = (v) => String(v || "").trim().toUpperCase();

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Synchro...");
  const [filters, setFilters] = useState({ hp2: '', ug: '' });

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

  const results = useMemo(() => {
    const sH = clean(filters.hp2);
    const sU = clean(filters.ug);
    if (!sH && !sU) return [];

    // 1. Trouver les lignes qui matchent
    const matches = data.filter(r => {
      const rowStr = Object.values(r).join(" ").toUpperCase();
      const matchH = sH === "" || rowStr.includes(sH);
      const matchU = sU === "" || rowStr.includes(sU);
      return matchH && matchU;
    });

    // 2. Grouper par HP2
    const groups = {};
    matches.forEach(r => {
      const id = clean(r['GROUPE (HP2)'] || r['HP2'] || r['CODE_HP2'] || r['GROUPE'] || r['CODE_SITE']);
      if (!id || id === "N/C") return;
      if (!groups[id]) groups[id] = [];
      groups[id].push(r);
    });

    return Object.keys(groups).map(id => {
      const rows = data.filter(r => clean(r['GROUPE (HP2)'] || r['HP2'] || r['CODE_HP2'] || r['GROUPE']) === id);
      
      const get = (keys) => {
        for (const r of rows) {
          for (const k of Object.keys(r)) {
            if (keys.some(tk => k.toUpperCase().includes(tk))) {
              const v = String(r[k]).trim();
              if (v && v !== "0" && v !== "0.0" && v !== "N/A") return v;
            }
          }
        }
        return "N/C";
      };

      // Spécifique pour l'UG cherchée
      const ugRow = rows.find(r => sU !== "" && Object.values(r).some(v => clean(v).includes(sU)));

      return {
        id,
        nom: get(["NOM", "LIBELLE"]),
        adr: get(["ADRESSE", "LOCALISATION", "RUE"]),
        sch: get(["SURFACE CHAUFFEE", "SCH", "SUT", "SURFACE_UTILE"]),
        sha: ugRow ? (ugRow['SURFACE HABITABLE (SHA)'] || ugRow['SHA'] || ugRow['SURFACE'] || "N/C") : null,
        ug: ugRow ? (ugRow['N° UG'] || ugRow['UG'] || sU) : null,
        equip: get(["EQUIPEMENT", "SYSTEME", "CHAUFFAGE", "CHAUDIERE", "DESIGNATION"]),
        nrj: get(["ENERGIE", "COMBUSTIBLE", "TYPE"]),
        sol: rows.some(r => r._F.includes("panneaux")),
        ind: rows.some(r => r._F.includes("individuel"))
      };
    });
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans pb-20">
      <header className="bg-[#1E40AF] p-5 shadow-xl sticky top-0 z-50 flex justify-between items-center text-white">
        <div className="flex items-center gap-2">
          <Building2 size={24} />
          <h1 className="font-black text-lg uppercase tracking-tighter">Socobat <span className="text-blue-200">Patrimoine</span></h1>
        </div>
        <div className="text-[10px] font-bold bg-white/20 px-3 py-1 rounded-full uppercase">{data.length} Lignes</div>
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-8">
        <div className="bg-white p-6 rounded-[32px] shadow-sm mb-8 flex flex-col md:flex-row gap-4 border border-slate-100">
          <div className="flex-1">
            <input placeholder="Groupe (ex: 119AL)" className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold" onChange={e => setFilters({...filters, hp2: e.target.value})} />
          </div>
          <div className="flex-1">
            <input placeholder="N° UG (ex: 151799)" className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold text-blue-600" onChange={e => setFilters({...filters, ug: e.target.value})} />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center py-20 text-slate-400 font-bold uppercase text-xs tracking-widest"><Loader2 className="animate-spin mb-2" /> {status}</div>
        ) : (
          <div className="space-y-6">
            {results.map((r, i) => (
              <div key={i} className="bg-white rounded-[40px] shadow-sm border border-slate-100 overflow-hidden border-b-8 border-b-blue-600 hover:shadow-2xl transition-all">
                <div className="p-8">
                  <div className="flex gap-2 mb-4">
                    <span className="bg-slate-900 text-white text-[9px] font-black px-2 py-1 rounded">ID: {r.id}</span>
                    {r.sol && <span className="bg-orange-500 text-white text-[9px] font-black px-2 py-1 rounded uppercase flex items-center gap-1"><Sun size={10}/> Solaire</span>}
                    <span className={`text-[9px] font-black px-2 py-1 rounded uppercase ${r.ind ? 'bg-purple-100 text-purple-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {r.ind ? 'Individuel' : 'Collectif'}
                    </span>
                  </div>

                  <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tighter mb-8">{r.nom}</h2>

                  <div className="grid md:grid-cols-2 gap-8 pt-6 border-t border-slate-50">
                    <div className="space-y-6">
                      <div className="flex gap-4">
                        <MapPin size={20} className="text-blue-500 shrink-0" />
                        <p className="font-bold text-slate-600 text-sm leading-tight">{r.adr}</p>
                      </div>

                      <div className="bg-[#2563EB] text-white p-6 rounded-[32px] shadow-lg shadow-blue-100">
                        <div className="flex items-center gap-2 mb-4 opacity-70 border-b border-white/20 pb-2 uppercase text-[9px] font-black"><ClipboardCheck size={14}/> Données Surfaces</div>
                        <div className="flex justify-between items-end mb-4">
                           <p className="text-xs font-bold uppercase">UG (Logement) <span className="block opacity-60 text-[8px]">{r.ug || "--"}</span></p>
                           <p className="text-2xl font-black tracking-tighter">{r.sha ? `${r.sha} m²` : '--'}</p>
                        </div>
                        <div className="flex justify-between items-end">
                           <p className="text-xs font-bold uppercase">Groupe (Total)</p>
                           <p className="text-xl font-black tracking-tighter">{r.sch} m²</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-50 p-6 rounded-[32px] border border-slate-100">
                      <p className="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-4 flex items-center gap-2"><Zap size={14}/> Technique</p>
                      <p className="font-bold text-slate-800 text-xs leading-relaxed mb-6 italic">{r.equip}</p>
                      <div className="border-t border-slate-200 pt-4 flex justify-between font-black text-[10px] uppercase">
                         <span className="text-slate-400">Énergie :</span>
                         <span className="text-blue-600">{r.nrj}</span>
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
