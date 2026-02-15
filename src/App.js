import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Zap, Loader2, Building2, Sun, ClipboardCheck } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

// Fonction pour forcer le format 6 caractères (ex: 15179 -> 015179)
const padUG = (val) => {
  const s = String(val).trim();
  if (!s || s === "0" || s === "N/A") return s;
  // Si c'est purement numérique et moins de 6 car., on ajoute des 0
  if (/^\d+$/.test(s) && s.length < 6) {
    return s.padStart(6, '0');
  }
  return s;
};

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Chargement...");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const loadData = async () => {
      let combined = [];
      for (const file of FICHIERS_EXCEL) {
        try {
          setStatus(`Analyse : ${file}`);
          const res = await fetch(`/${encodeURIComponent(file)}`);
          if (!res.ok) continue;
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          wb.SheetNames.forEach(sheet => {
            const json = XLSX.utils.sheet_to_json(wb.Sheets[sheet], { defval: "" });
            combined.push(...json.map(row => ({ ...row, _SOURCE: file })));
          });
        } catch (e) { console.error(e); }
      }
      setData(combined);
      setLoading(false);
    };
    loadData();
  }, []);

  const results = useMemo(() => {
    const sRaw = search.trim();
    if (sRaw.length < 2) return [];
    
    const sPadded = padUG(sRaw).toUpperCase();
    const sUpper = sRaw.toUpperCase();

    // 1. RECHERCHE RADAR avec tolérance sur le zéro de début
    const matches = data.filter(row => {
      return Object.values(row).some(v => {
        const valStr = String(v).toUpperCase().trim();
        const valPadded = padUG(valStr).toUpperCase();
        return valStr.includes(sUpper) || valPadded.includes(sPadded) || sPadded.includes(valPadded);
      });
    });

    const hp2Set = new Set();
    matches.forEach(m => {
      const keys = Object.keys(m);
      const hp2Key = keys.find(k => k.toUpperCase().includes("HP2") || k.toUpperCase().includes("GROUPE"));
      if (hp2Key && m[hp2Key]) hp2Set.add(String(m[hp2Key]).toUpperCase().trim());
    });

    return Array.from(hp2Set).map(code => {
      const related = data.filter(d => 
        Object.values(d).some(v => String(v).toUpperCase().trim() === code)
      );

      const specificUG = matches.find(m => {
        const rowStr = Object.values(m).join("|").toUpperCase();
        const hasUG = rowStr.includes(sUpper) || rowStr.includes(sPadded);
        const hasHP2 = rowStr.includes(code);
        return hasUG && hasHP2;
      });

      const findIn = (terms) => {
        for (const d of related) {
          for (const k of Object.keys(d)) {
            if (terms.some(t => k.toUpperCase().includes(t))) {
              const val = String(d[k]).trim();
              if (val && val !== "0" && val !== "N/A") return val;
            }
          }
        }
        return "N/C";
      };

      return {
        hp2: code,
        nom: findIn(["NOM", "GROUPE"]),
        adresse: findIn(["ADRESSE", "LOCALISATION", "RUE"]),
        surfTotal: findIn(["SURFACE CHAUFFEE", "SCH", "SURFACE UT"]),
        surfLogement: specificUG ? (
          specificUG["SURFACE HABITABLE (SHA)"] || 
          specificUG["SHA"] || 
          specificUG["SURFACE_REELLE"] || 
          specificUG["SURFACE"]
        ) : null,
        ugID: specificUG ? padUG(specificUG["N° UG"] || specificUG["UG"] || sRaw) : null,
        equip: findIn(["EQUIPEMENT", "SYSTEME", "CHAUFFAGE", "DESIGNATION"]),
        energie: findIn(["ENERGIE", "COMBUSTIBLE"]),
        isSolaire: related.some(d => d._SOURCE.includes("panneaux")),
        isIndividuel: related.some(d => d._SOURCE.includes("individuel"))
      };
    });
  }, [data, search]);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 font-sans pb-20">
      <header className="bg-[#3A7AFE] p-6 shadow-xl sticky top-0 z-50 flex justify-between items-center text-white">
        <div className="flex items-center gap-3">
          <Building2 size={24} />
          <h1 className="font-black text-xl uppercase italic">Socobat PH</h1>
        </div>
        <div className="text-[10px] font-bold bg-black/20 px-3 py-1 rounded-full uppercase italic">{data.length} Lignes</div>
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-10">
        <div className="bg-white p-8 rounded-[40px] shadow-2xl shadow-blue-900/10 mb-10">
          <input 
            placeholder="N° UG (6 chiffres) ou HP2..." 
            className="w-full p-6 bg-slate-50 rounded-3xl outline-none focus:ring-4 focus:ring-blue-500/10 transition-all text-xl font-bold border-none"
            onChange={e => setSearch(e.target.value)}
          />
          <p className="text-center text-slate-400 text-[10px] mt-4 font-black uppercase tracking-[0.2em]">Correcteur de format UG actif (0xxxx)</p>
        </div>

        {loading ? (
          <div className="flex flex-col items-center py-20"><Loader2 className="animate-spin text-blue-600" size={40} /></div>
        ) : (
          <div className="space-y-8">
            {results.map((r, i) => (
              <div key={i} className="bg-white rounded-[45px] shadow-sm border border-slate-200 overflow-hidden hover:shadow-2xl transition-all border-b-8 border-b-blue-600">
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
                      <div className="bg-blue-600 text-white p-8 rounded-[40px] shadow-xl shadow-blue-200">
                        <div className="flex items-center gap-2 mb-6 opacity-60 border-b border-white/20 pb-2 uppercase text-[9px] font-black"><ClipboardCheck size={16}/> Données DPE</div>
                        <div className="flex justify-between items-end mb-6">
                           <p className="text-xs font-bold uppercase tracking-tighter">Surface Logement <span className="block opacity-60 text-[8px]">UG: {r.ugID || "--"}</span></p>
                           <p className="text-3xl font-black">{r.surfLogement ? `${r.surfLogement} m²` : '--'}</p>
                        </div>
                        <div className="flex justify-between items-end">
                           <p className="text-xs font-bold uppercase tracking-tighter">Surface Groupe <span className="block opacity-60 text-[8px]">Ensemble HP2</span></p>
                           <p className="text-xl font-black">{r.surfTotal} m²</p>
                        </div>
                      </div>
                    </div>
                    <div className="bg-slate-50 p-8 rounded-[40px] border border-slate-100 h-fit">
                      <p className="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-4 flex items-center gap-2"><Zap size={16}/> Technique</p>
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
