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

// Nettoyage des dates Excel (ex: 29646)
const formatExcelDate = (serial) => {
  if (!serial || isNaN(serial) || serial < 1000) return serial;
  const date = new Date(Math.round((serial - 25569) * 86400 * 1000));
  return date.toLocaleDateString('fr-FR');
};

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Démarrage...");
  const [filters, setFilters] = useState({ groupe: '', ug: '' });

  useEffect(() => {
    const loadAllData = async () => {
      let combined = [];
      for (const file of FICHIERS_EXCEL) {
        try {
          setStatus(`Lecture : ${file}`);
          const res = await fetch(`/${encodeURIComponent(file)}`);
          if (!res.ok) continue;
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          
          wb.SheetNames.forEach(sheet => {
            const json = XLSX.utils.sheet_to_json(wb.Sheets[sheet], { defval: "" });
            combined.push(...json.map(row => {
              const clean = {};
              Object.keys(row).forEach(k => {
                // On normalise les clés : MAJUSCULES, sans espaces, sans accents
                const key = k.trim().toUpperCase()
                  .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                  .replace(/ /g, '_')
                  .replace(/N°/g, 'N');
                clean[key] = String(row[k]).trim();
              });
              return { ...clean, _SOURCE: file };
            }));
          });
        } catch (e) { console.error(e); }
      }
      setData(combined);
      setLoading(false);
    };
    loadAllData();
  }, []);

  const results = useMemo(() => {
    const sG = filters.groupe.toUpperCase().trim();
    const sU = filters.ug.toUpperCase().trim();
    
    if (!sG && !sU) return [];

    // 1. Trouver les lignes qui correspondent aux filtres
    const matches = data.filter(item => {
      const itemHP2 = (item.GROUPE_HP2 || item.HP2 || item.CODE_HP2 || "").toUpperCase();
      const itemUG = (item.N_UG || item.UG || "").toUpperCase();
      
      const matchG = sG === "" || itemHP2.includes(sG);
      const matchU = sU === "" || itemUG === sU || itemUG.includes(sU);
      
      return matchG && matchU;
    });

    // 2. Extraire les codes HP2 uniques pour fusionner les infos techniques
    const uniqueHP2s = [...new Set(matches.map(m => (m.GROUPE_HP2 || m.HP2 || m.CODE_HP2 || "")))];

    return uniqueHP2s.map(hp2Code => {
      const code = hp2Code.toUpperCase();
      // On récupère toutes les infos de ce groupe dans toute la base
      const groupHistory = data.filter(d => (d.GROUPE_HP2 || d.HP2 || d.CODE_HP2 || "").toUpperCase() === code);
      // On récupère l'UG spécifique si on en a cherché une
      const ugSpecific = matches.find(m => (m.GROUPE_HP2 || m.HP2 || m.CODE_HP2 || "").toUpperCase() === code && (m.N_UG || m.UG));

      const find = (keys) => {
        for (const d of groupHistory) {
          for (const k of keys) { if (d[k] && d[k] !== "0" && d[k] !== "" && d[k] !== "N/A") return d[k]; }
        }
        return "N/C";
      };

      return {
        id: code,
        nom: find(['NOM_GROUPE', 'NOM']),
        adresse: find(['ADRESSE', 'LOCALISATION', 'ADRESSE_COMPLETE']),
        // Surface du Groupe (Patrimoine global)
        surfGroupe: find(['SURFACE_CHAUFFEE_SCH', 'SCH', 'SURFACE_UTILE_SUT', 'SURFACE_HABITABLE_SHAB']),
        // Surface de l'UG (Logement précis)
        surfUG: ugSpecific ? (ugSpecific.SURFACE_HABITABLE_SHA || ugSpecific.SHA || ugSpecific.SURFACE_REELLE_SRE || ugSpecific.SRE) : null,
        ugID: ugSpecific ? (ugSpecific.N_UG || ugSpecific.UG) : null,
        energie: find(['TYPE_COMBUSTIBLE', 'ENERGIE', 'TYPE_ENERGIE']),
        equipement: find(['EQUIPEMENT', 'SYSTEME_CHAUFFAGE', 'DESIGNATION', 'DESCRIPTIF_GENERATEURS']),
        marque: find(['MARQUE', 'CONSTRUCTEUR']),
        date: formatExcelDate(find(['DATE_DE_MISE_EN_SERVICE', 'DATE_MES', 'DATE_CONSTRUCTION'])),
        isSolaire: groupHistory.some(d => d._SOURCE.includes("panneaux")),
        isIndividuel: groupHistory.some(d => d._SOURCE.includes("individuel")),
        nbLogements: find(['NOMBRE_DE_LOGEMENTS', 'NB_LOGEMENTS'])
      };
    });
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-[#F1F5F9] text-slate-900 font-sans pb-20">
      <header className="bg-[#3A7AFE] p-6 shadow-xl sticky top-0 z-50 flex justify-between items-center text-white">
        <div className="flex items-center gap-3">
          <Building2 size={28} />
          <h1 className="font-black text-xl tracking-tighter uppercase italic">Socobat PH</h1>
        </div>
        {!loading && <div className="text-[10px] font-bold bg-white/20 px-3 py-1 rounded-full">{data.length} LIGNES</div>}
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-10">
        {/* DOUBLE RECHERCHE */}
        <div className="bg-white p-6 rounded-[32px] shadow-sm border border-slate-100 mb-8 flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label className="text-[10px] font-black text-slate-400 uppercase ml-2 mb-1 block">Groupe (HP2)</label>
            <input 
              placeholder="Ex: 119AL" 
              className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold"
              onChange={e => setFilters({...filters, groupe: e.target.value})}
            />
          </div>
          <div className="flex-1">
            <label className="text-[10px] font-black text-slate-400 uppercase ml-2 mb-1 block">N° UG (Logement)</label>
            <input 
              placeholder="Ex: 151799" 
              className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold text-blue-600"
              onChange={e => setFilters({...filters, ug: e.target.value})}
            />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center py-20 text-slate-400">
            <Loader2 className="animate-spin mb-4" size={40} />
            <p className="font-black uppercase tracking-widest text-xs">{status}</p>
          </div>
        ) : (
          <div className="space-y-6">
            {results.map((r, i) => (
              <div key={i} className="bg-white rounded-[40px] shadow-sm border border-slate-100 overflow-hidden hover:shadow-2xl transition-all border-b-8 border-b-blue-500">
                <div className="p-8">
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="bg-slate-900 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase tracking-wider">HP2: {r.id}</span>
                    {r.isSolaire && <span className="bg-orange-500 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase flex items-center gap-1"><Sun size={12}/> Solaire</span>}
                    <span className={`text-[10px] font-black px-3 py-1 rounded-lg uppercase ${r.isIndividuel ? 'bg-purple-100 text-purple-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {r.isIndividuel ? 'Chauffage Individuel' : 'Chauffage Collectif'}
                    </span>
                  </div>

                  <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tighter mb-8 leading-none">{r.nom || "Groupe sans nom"}</h2>

                  <div className="grid md:grid-cols-2 gap-8 pt-6 border-t border-slate-50">
                    <div className="space-y-6">
                      <div className="flex gap-4">
                        <MapPin size={24} className="text-blue-500 shrink-0" />
                        <div>
                          <p className="text-[9px] font-black text-slate-300 uppercase tracking-widest">Adresse complète</p>
                          <p className="font-bold text-slate-600 leading-snug">{r.adresse}</p>
                        </div>
                      </div>

                      {/* BLOC SURFACE DPE */}
                      <div className="bg-blue-600 text-white p-6 rounded-[32px] shadow-lg shadow-blue-200">
                        <div className="flex items-center gap-2 mb-4 opacity-70 border-b border-white/20 pb-2">
                           <ClipboardCheck size={16} />
                           <p className="text-[9px] font-bold uppercase tracking-widest">Données pour DPE</p>
                        </div>
                        <div className="flex justify-between items-end mb-4">
                           <p className="text-xs font-bold">Surface UG <span className="block opacity-60 font-medium">Logement ({r.ugID || "N/A"})</span></p>
                           <p className="text-2xl font-black">{r.surfUG ? `${r.surfUG} m²` : '--'}</p>
                        </div>
                        <div className="flex justify-between items-end">
                           <p className="text-xs font-bold">Surface HP2 <span className="block opacity-60 font-medium">Ensemble immobilier</span></p>
                           <p className="text-xl font-black">{r.surfGroupe} m²</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-50 p-6 rounded-[32px] border border-slate-100 h-fit">
                      <div className="flex items-center gap-3 mb-4 text-blue-600">
                        <Zap size={20}/>
                        <p className="text-[10px] font-black uppercase tracking-widest">Fiche Technique</p>
                      </div>
                      <p className="font-bold text-slate-700 text-sm leading-relaxed mb-6 italic">{r.equipement}</p>
                      
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
            {filters.groupe || filters.ug ? results.length === 0 && (
              <div className="text-center py-20 bg-white rounded-[40px] border-4 border-dashed border-slate-100">
                <p className="text-slate-300 font-black uppercase tracking-widest text-sm italic">Aucun patrimoine trouvé</p>
              </div>
            ) : null}
          </div>
        )}
      </main>
    </div>
  );
}
