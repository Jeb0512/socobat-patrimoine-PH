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

const formatExcelDate = (serial) => {
  if (!serial || isNaN(serial) || serial < 1000) return serial;
  const date = new Date(Math.round((serial - 25569) * 86400 * 1000));
  return date.toLocaleDateString('fr-FR');
};

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Chargement...");
  const [filters, setFilters] = useState({ search: '' });

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
              // On garde les noms de colonnes originaux pour le "Radar"
              Object.keys(row).forEach(k => {
                clean[k.trim().toUpperCase()] = String(row[k]).trim();
              });
              return { ...clean, _RAW: row, _SOURCE: file };
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
    const s = filters.search.toUpperCase().trim();
    if (s.length < 2) return [];

    // FONCTION RADAR : Cherche le texte dans TOUTE la ligne
    const matches = data.filter(item => {
      return Object.values(item).some(val => String(val).toUpperCase().includes(s));
    });

    // Extraire les codes HP2 uniques trouvés
    const hp2Found = new Set();
    matches.forEach(m => {
      const code = m['GROUPE (HP2)'] || m['HP2'] || m['CODE_HP2'] || m['GROUPE_HP2'] || m['GROUPE'];
      if (code) hp2Found.add(code.toUpperCase());
    });

    return Array.from(hp2Found).map(code => {
      const history = data.filter(d => 
        (d['GROUPE (HP2)'] || d['HP2'] || d['CODE_HP2'] || d['GROUPE_HP2'] || d['GROUPE'] || "").toUpperCase() === code
      );

      // On cherche l'UG spécifique dans les résultats du radar pour ce groupe
      const specificUG = matches.find(m => 
        (m['N° UG'] || m['UG'] || m['N_UG'] || m['CODE UG'] || "").includes(s) &&
        (m['GROUPE (HP2)'] || m['HP2'] || m['CODE_HP2'] || m['GROUPE_HP2'] || m['GROUPE'] || "").toUpperCase() === code
      );

      const find = (keys) => {
        for (const d of history) {
          for (const k of keys) {
            const val = d[k.toUpperCase()];
            if (val && val !== "0" && val !== "N/A" && val !== "") return val;
          }
        }
        return "N/C";
      };

      return {
        hp2: code,
        nom: find(['NOM_GROUPE', 'NOM DU GROUPE', 'NOM']),
        adresse: find(['ADRESSE', 'LOCALISATION', 'ADRESSE COMPLETE']),
        surfGroupe: find(['SURFACE CHAUFFEE (SCH)', 'SCH', 'SURFACE_UTILE_SUT', 'SURFACE']),
        // Surface précise du logement (Sha)
        surfUG: specificUG ? (specificUG['SURFACE HABITABLE (SHA)'] || specificUG['SHA'] || specificUG['SURFACE_CHAUFFEE_(SCH)']) : null,
        ugID: specificUG ? (specificUG['N° UG'] || specificUG['UG'] || specificUG['N_UG']) : null,
        equipement: find(['SYSTEME_CHAUFFAGE', 'EQUIPEMENT', 'DESIGNATION', 'DESCRIPTIF_GENERATEURS']),
        energie: find(['ENERGIE', 'TYPE_COMBUSTIBLE', 'TYPE_ENERGIE']),
        date: formatExcelDate(find(['DATE_DE_MISE_EN_SERVICE', 'DATE_MES', 'DATE_CONSTRUCTION'])),
        isSolaire: history.some(d => d._SOURCE.includes("panneaux")),
        isIndividuel: history.some(d => d._SOURCE.includes("individuel"))
      };
    });
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans pb-20">
      <header className="bg-blue-600 p-6 shadow-lg sticky top-0 z-50 flex justify-between items-center text-white">
        <div className="flex items-center gap-3">
          <Building2 size={24} />
          <h1 className="font-black text-xl tracking-tighter uppercase italic">Socobat PH</h1>
        </div>
        {!loading && <div className="text-[10px] font-bold bg-white/20 px-3 py-1 rounded-full">{data.length} LIGNES</div>}
      </header>

      <main className="max-w-4xl mx-auto px-4 pt-10">
        <div className="bg-white p-8 rounded-[40px] shadow-2xl shadow-blue-900/5 border border-slate-100 mb-10 text-center">
          <h2 className="text-2xl font-black mb-2">Recherche DPE Patrimoine</h2>
          <p className="text-slate-400 text-sm mb-8 font-medium italic">Saisissez n'importe quelle donnée (N° UG, Adresse, Code HP2...)</p>
          
          <div className="relative group">
            <input 
              placeholder="Exemple: 151799 ou HP2-045..." 
              className="w-full p-6 bg-slate-50 rounded-3xl outline-none focus:ring-4 focus:ring-blue-500/10 transition-all text-xl font-bold border-none"
              onChange={e => setFilters({search: e.target.value})}
            />
            <Search className="absolute right-6 top-6 text-blue-600" size={28}/>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center py-20"><Loader2 className="animate-spin text-blue-600" size={40} /></div>
        ) : (
          <div className="space-y-8">
            {results.map((r, i) => (
              <div key={i} className="bg-white rounded-[45px] shadow-sm border border-slate-100 overflow-hidden hover:shadow-2xl transition-all border-b-8 border-b-blue-600">
                <div className="p-10">
                  <div className="flex flex-wrap gap-2 mb-6">
                    <span className="bg-slate-900 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase tracking-wider">GROUPE {r.hp2}</span>
                    {r.isSolaire && <span className="bg-orange-500 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase flex items-center gap-1"><Sun size={12}/> Solaire</span>}
                    <span className={`text-[10px] font-black px-3 py-1 rounded-lg uppercase ${r.isIndividuel ? 'bg-purple-100 text-purple-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {r.isIndividuel ? 'Chauffage Individuel' : 'Chauffage Collectif'}
                    </span>
                  </div>

                  <h3 className="text-3xl font-black text-slate-900 uppercase tracking-tighter mb-10 leading-none">{r.nom}</h3>

                  <div className="grid md:grid-cols-2 gap-10">
                    <div className="space-y-8">
                      <div className="flex gap-4">
                        <MapPin size={24} className="text-blue-600 shrink-0" />
                        <div>
                          <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1">Localisation</p>
                          <p className="font-bold text-slate-700 text-lg leading-tight">{r.adresse}</p>
                        </div>
                      </div>

                      <div className="bg-blue-600 text-white p-8 rounded-[40px] shadow-xl shadow-blue-200">
                        <div className="flex items-center gap-2 mb-6 opacity-80 border-b border-white/20 pb-3">
                           <ClipboardCheck size={20} />
                           <p className="text-[10px] font-black uppercase tracking-widest">Données de Surface (DPE)</p>
                        </div>
                        <div className="flex justify-between items-end mb-6">
                           <p className="text-sm font-bold uppercase tracking-tighter">Surface Logement <span className="block opacity-60 text-[10px]">(UG {r.ugID || "N/C"})</span></p>
                           <p className="text-3xl font-black">{r.surfUG ? `${r.surfUG} m²` : '--'}</p>
                        </div>
                        <div className="flex justify-between items-end">
                           <p className="text-sm font-bold uppercase tracking-tighter">Surface Totale <span className="block opacity-60 text-[10px]">(Ensemble HP2)</span></p>
                           <p className="text-xl font-black">{r.surfGroupe} m²</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-50 p-8 rounded-[40px] border border-slate-100 h-fit">
                      <div className="flex items-center gap-3 mb-6 text-blue-600">
                        <Zap size={22}/>
                        <p className="text-[10px] font-black uppercase tracking-widest">Technique & Énergie</p>
                      </div>
                      <p className="font-bold text-slate-700 text-sm leading-relaxed mb-8 italic">{r.equipement}</p>
                      
                      <div className="grid grid-cols-2 gap-4 border-t border-slate-200 pt-6">
                         <div>
                            <span className="text-[9px] font-black text-slate-400 uppercase block mb-1">Combustible</span>
                            <span className="text-xs font-black text-blue-600 uppercase">{r.energie}</span>
                         </div>
                         <div className="text-right">
                            <span className="text-[9px] font-black text-slate-400 uppercase block mb-1">Dernière MES</span>
                            <span className="text-xs font-black text-slate-600">{r.date}</span>
                         </div>
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
