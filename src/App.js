import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Thermometer, Zap, Loader2, Building2, AlertTriangle, Home, Layers, Sun, ClipboardCheck } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

const formatExcelDate = (serial) => {
  if (!serial || isNaN(serial) || serial < 1000) return serial;
  const date = new Date(Math.round((serial - 25569) * 86400 * 1000));
  return date.toLocaleDateString('fr-FR');
};

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Vérification des fichiers...");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const loadAllData = async () => {
      let combined = [];
      for (const file of FICHIERS_EXCEL) {
        try {
          setStatus(`Chargement : ${file}`);
          const res = await fetch(`/${encodeURIComponent(file)}`);
          if (!res.ok) continue;
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          
          wb.SheetNames.forEach(sheet => {
            const json = XLSX.utils.sheet_to_json(wb.Sheets[sheet], { defval: "" });
            combined.push(...json.map(row => {
              const clean = {};
              Object.keys(row).forEach(k => {
                const key = k.trim().toUpperCase().replace(/ /g, '_').replace(/N°/g, 'N');
                clean[key] = String(row[k]).trim();
              });
              return { ...clean, _ORIGIN: file };
            }));
          });
        } catch (e) { console.error(e); }
      }
      setData(combined);
      setLoading(false);
    };
    loadAllData();
  }, []);

  const finalResults = useMemo(() => {
    const s = search.toLowerCase().trim();
    if (!s) return [];

    // 1. On cherche si la saisie correspond à un N° UG ou un Code HP2
    const targetUGs = data.filter(d => (d.N_UG || d.UG || "").toLowerCase() === s);
    const targetHP2s = data.filter(d => (d.GROUPE_HP2 || d.HP2 || d.CODE_HP2 || "").toLowerCase() === s);

    // On détermine la liste des codes HP2 à analyser
    const hp2Codes = new Set();
    targetHP2s.forEach(d => hp2Codes.add((d.GROUPE_HP2 || d.HP2 || d.CODE_HP2).toUpperCase()));
    targetUGs.forEach(d => hp2Codes.add((d.GROUPE_HP2 || d.HP2 || d.CODE_HP2).toUpperCase()));

    return Array.from(hp2Codes).map(code => {
      const groupData = data.filter(d => (d.GROUPE_HP2 || d.HP2 || d.CODE_HP2 || "").toUpperCase() === code);
      
      const find = (keys) => {
        for (const d of groupData) {
          for (const k of keys) { if (d[k] && d[k] !== "0" && d[k] !== "NON" && d[k] !== "N/A") return d[k]; }
        }
        return "N/C";
      };

      // Info spécifique de l'UG si recherchée
      const ugInfo = targetUGs.find(d => (d.GROUPE_HP2 || d.HP2 || d.CODE_HP2 || "").toUpperCase() === code);

      return {
        hp2: code,
        nom: find(['NOM_GROUPE', 'NOM']),
        adresse: find(['ADRESSE', 'LOCALISATION', 'ADRESSE_COMPLETE']),
        // Surface du Groupe (Totale)
        surfGroupe: find(['SURFACE_CHAUFFEE_SCH', 'SCH', 'SURFACE_UTILE_SUT']),
        // Surface de l'UG spécifique
        surfUG: ugInfo ? (ugInfo.SURFACE_HABITABLE_SHA || ugInfo.SHA || ugInfo.SURFACE_CHAUFFEE_SCH || ugInfo.SCH) : null,
        ugCode: ugInfo ? (ugInfo.N_UG || ugInfo.UG) : null,
        energie: find(['TYPE_COMBUSTIBLE', 'ENERGIE', 'TYPE_ENERGIE']),
        equipement: find(['EQUIPEMENT', 'SYSTEME_CHAUFFAGE', 'DESIGNATION', 'DESCRIPTIF_GENERATEURS', 'MARQUE_DE_TYPE_VITOSOL']),
        marque: find(['MARQUE', 'CONSTRUCTEUR']),
        date: formatExcelDate(find(['DATE_DE_MISE_EN_SERVICE', 'DATE_MES', 'DATE_CONSTRUCTION'])),
        isSolaire: groupData.some(d => d._ORIGIN.includes("panneaux")),
        isIndividuel: groupData.some(d => d._ORIGIN.includes("individuel")),
        nbLogements: find(['NOMBRE_DE_LOGEMENTS', 'NB_LOGEMENTS'])
      };
    });
  }, [data, search]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans pb-20">
      <header className="bg-white border-b border-slate-200 p-5 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-xl text-white shadow-lg"><Building2 size={24}/></div>
            <h1 className="font-black text-xl tracking-tighter">SOCOBAT <span className="text-blue-600 font-medium">PH</span></h1>
          </div>
          {!loading && <div className="text-[10px] font-bold bg-slate-100 text-slate-500 px-3 py-1 rounded-full uppercase tracking-widest">{data.length} DONNÉES</div>}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-10">
        <div className="mb-10 text-center">
          <h2 className="text-3xl font-black text-slate-900 mb-2">Consultation DPE</h2>
          <p className="text-slate-400 font-medium">Saisissez un N° d'UG pour obtenir les surfaces et données techniques.</p>
        </div>

        <div className="relative mb-12">
          <input 
            placeholder="Ex: 151799 (UG) ou 119AL (Groupe)..." 
            className="w-full p-6 bg-white rounded-[32px] shadow-2xl shadow-blue-900/10 outline-none focus:ring-4 focus:ring-blue-500/10 transition-all text-lg font-bold border border-slate-100"
            onChange={e => setSearch(e.target.value)}
          />
          <Search className="absolute right-6 top-6 text-blue-600" size={28}/>
        </div>

        {loading ? (
          <div className="flex flex-col items-center py-20 text-slate-400">
            <Loader2 className="animate-spin mb-4" size={40} />
            <p className="font-bold uppercase tracking-widest text-[10px]">{status}</p>
          </div>
        ) : (
          <div className="space-y-8">
            {finalResults.map((r, i) => (
              <div key={i} className="bg-white rounded-[40px] shadow-sm border border-slate-100 overflow-hidden hover:shadow-xl transition-all">
                <div className="p-8">
                  {/* BADGES */}
                  <div className="flex flex-wrap gap-2 mb-6">
                    <span className="bg-slate-900 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase">GROUPE {r.hp2}</span>
                    {r.isSolaire && <span className="bg-orange-500 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase flex items-center gap-1"><Sun size={12}/> Solaire</span>}
                    <span className={`text-[10px] font-black px-3 py-1 rounded-lg uppercase ${r.isIndividuel ? 'bg-purple-100 text-purple-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {r.isIndividuel ? 'Individuel' : 'Collectif'}
                    </span>
                  </div>

                  <h3 className="text-2xl font-black text-slate-900 uppercase tracking-tighter mb-8">{r.nom}</h3>

                  <div className="grid md:grid-cols-2 gap-8 border-t border-slate-50 pt-8">
                    {/* COLONNE GAUCHE : SURFACES DPE */}
                    <div className="space-y-6">
                      <div className="flex gap-4">
                        <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl h-fit"><MapPin size={24}/></div>
                        <div>
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Adresse</p>
                          <p className="font-bold text-slate-700 leading-tight">{r.adresse}</p>
                        </div>
                      </div>

                      <div className="bg-blue-600 text-white p-6 rounded-[32px] shadow-lg shadow-blue-200">
                        <div className="flex items-center gap-2 mb-4 opacity-80 border-b border-white/20 pb-2">
                           <ClipboardCheck size={18} />
                           <p className="text-[10px] font-bold uppercase tracking-widest">Données Surface DPE</p>
                        </div>
                        <div className="flex justify-between items-center mb-4">
                           <p className="text-sm font-medium">Surface de l'UG <span className="block text-[9px] opacity-70 italic">(Logement)</span></p>
                           <p className="text-2xl font-black">{r.surfUG ? `${r.surfUG} m²` : 'Tapez N° UG'}</p>
                        </div>
                        <div className="flex justify-between items-center">
                           <p className="text-sm font-medium">Surface du Groupe <span className="block text-[9px] opacity-70 italic">(Ensemble)</span></p>
                           <p className="text-xl font-black">{r.surfGroupe} m²</p>
                        </div>
                      </div>
                    </div>

                    {/* COLONNE DROITE : TECHNIQUE */}
                    <div className="bg-slate-50 p-6 rounded-[32px] border border-slate-100 h-fit">
                      <div className="flex items-center gap-3 mb-4 text-slate-400">
                        <Zap size={20}/>
                        <p className="text-[10px] font-black uppercase tracking-widest">Technique & Énergie</p>
                      </div>
                      <p className="font-bold text-slate-700 text-sm leading-relaxed mb-6">{r.equipement}</p>
                      
                      <div className="grid grid-cols-2 gap-4 border-t border-slate-200 pt-4">
                         <div>
                            <span className="text-[8px] font-bold text-slate-400 uppercase block mb-1">Combustible</span>
                            <span className="text-xs font-black text-blue-600 uppercase">{r.energie}</span>
                         </div>
                         <div className="text-right">
                            <span className="text-[8px] font-bold text-slate-400 uppercase block mb-1">Mise en service</span>
                            <span className="text-xs font-black text-slate-600">{r.date}</span>
                         </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {search && finalResults.length === 0 && (
              <div className="text-center py-20 bg-white rounded-[40px] border-4 border-dashed border-slate-100">
                <p className="text-slate-300 font-black uppercase tracking-widest text-sm">Aucun résultat trouvé</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
