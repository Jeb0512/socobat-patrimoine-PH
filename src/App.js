import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Thermometer, Zap, Loader2, Building2, AlertTriangle, Sun, Home } from 'lucide-react';

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
  const [status, setStatus] = useState("Connexion...");
  const [filters, setFilters] = useState({ groupe: '', ug: '' });

  useEffect(() => {
    const chargerToutesLesDonnees = async () => {
      let cumulDonnees = [];
      for (const nomFichier of FICHIERS_EXCEL) {
        try {
          setStatus(`Chargement : ${nomFichier}`);
          const res = await fetch(`/${encodeURIComponent(nomFichier)}`);
          if (!res.ok) continue;
          
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          
          wb.SheetNames.forEach(sheetName => {
            const ws = wb.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(ws, { defval: "" });
            
            const cleanedData = jsonData.map(item => {
              // FONCTION MAGIQUE : Cherche une valeur dans plusieurs noms de colonnes possibles
              const find = (keywords) => {
                const key = Object.keys(item).find(k => 
                  keywords.some(kw => k.toUpperCase().includes(kw.toUpperCase()))
                );
                return key ? String(item[key]).trim() : "";
              };

              return {
                // On cherche les colonnes les plus probables
                GROUPE_FINAL: find(['GROUPE', 'HP2', 'GRPE', 'GRP']),
                UG_FINAL: find(['N°UG', 'N° UG', 'UG', 'CODE UG', 'UNIT']),
                ADRESSE_VAL: find(['ADRESSE', 'LOCALISATION', 'RUE', 'COMMUNE']),
                SURFACE_VAL: find(['SCH', 'SURFACE', 'SURF', 'M2', 'S.CH']),
                EQUIP_VAL: find(['SYSTEME', 'CHAUFFAGE', 'EQUIPEMENT', 'DESIGNATION', 'TYPE', 'CHAUDIERE']),
                ENERGIE_VAL: find(['ENERGIE', 'COMBUSTIBLE', 'TYPE ENERGIE']),
                PUISSANCE: find(['PUISSANCE', 'KW', 'P_NOMINALE']),
                DATE_MES: find(['DATE', 'ANNEE', 'MISE EN SERVICE', 'MES']),
                MARQUE: find(['MARQUE', 'MODELE', 'CONSTRUCTEUR']),
                sourceFile: nomFichier,
                onglet: sheetName
              };
            });
            cumulDonnees = [...cumulDonnees, ...cleanedData];
          });
        } catch (err) { console.error(err); }
      }
      setData(cumulDonnees);
      setLoading(false);
    };
    chargerToutesLesDonnees();
  }, []);

  const filteredResults = useMemo(() => {
    const sG = filters.groupe.toLowerCase().trim();
    const sU = filters.ug.toLowerCase().trim();
    if (!sG && !sU) return [];

    return data.filter(item => {
      // On filtre pour ne garder que les lignes qui ont au moins un Groupe ou une UG
      if (!item.GROUPE_FINAL && !item.UG_FINAL) return false;
      
      const matchG = sG === '' || item.GROUPE_FINAL.toLowerCase().includes(sG);
      const matchU = sU === '' || item.UG_FINAL.toLowerCase().includes(sU);
      return matchG && matchU;
    });
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-[#F5F7FA] text-[#4A4A4A] font-sans pb-12">
      <header className="bg-white p-6 border-b border-gray-100 shadow-sm sticky top-0 z-10 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-[#3A7AFE] p-2 rounded-xl text-white shadow-lg shadow-blue-100"><Building2 size={24} /></div>
          <div>
            <h1 className="text-lg font-black text-gray-900 tracking-tight leading-none uppercase">Socobat PH</h1>
            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">Patrimoine Technique</p>
          </div>
        </div>
        {!loading && <div className="text-right px-4 py-1 bg-gray-50 rounded-full border border-gray-100 font-bold text-[10px] text-gray-500 uppercase">{data.length} LIGNES ANALYSÉES</div>}
      </header>

      <main className="max-w-5xl mx-auto p-4 md:p-8">
        <div className="bg-white p-6 rounded-[32px] shadow-sm mb-8 flex flex-col md:flex-row gap-6 border border-gray-50">
          <div className="flex-1">
            <label className="text-[11px] font-black text-gray-400 uppercase ml-2 block mb-2">Groupe (HP2)</label>
            <input placeholder="Ex: HP2-045" className="w-full p-4 bg-[#F5F7FA] rounded-2xl outline-none focus:ring-2 focus:ring-[#3A7AFE] transition-all font-bold text-gray-700" onChange={e => setFilters({...filters, groupe: e.target.value})} />
          </div>
          <div className="flex-1">
            <label className="text-[11px] font-black text-gray-400 uppercase ml-2 block mb-2">N° UG / Code</label>
            <input placeholder="Ex: 119AL" className="w-full p-4 bg-[#F5F7FA] rounded-2xl outline-none focus:ring-2 focus:ring-[#3A7AFE] transition-all font-bold text-gray-700" onChange={e => setFilters({...filters, ug: e.target.value})} />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 bg-white rounded-[40px] shadow-sm border border-gray-50">
            <Loader2 className="animate-spin text-[#3A7AFE] mb-6" size={48} />
            <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">{status}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredResults.length > 0 ? (
              filteredResults.map((u, i) => (
                <div key={i} className="bg-white p-8 rounded-[35px] shadow-sm border border-transparent hover:border-blue-200 transition-all hover:shadow-xl group relative overflow-hidden">
                  <div className="flex justify-between items-start mb-6">
                    <div className="max-w-[70%]">
                      <span className="text-[9px] font-black text-[#3A7AFE] bg-blue-50 px-2.5 py-1 rounded-lg uppercase mb-2 block w-fit leading-none">
                        {u.sourceFile.split(' ')[0]}
                      </span>
                      <h3 className="font-black text-xl text-gray-900 uppercase tracking-tighter leading-none break-words">
                        {u.GROUPE_FINAL || 'GROUPE N/C'}
                      </h3>
                    </div>
                    <div className="text-right flex flex-col items-end">
                      <div className="bg-gray-900 text-white p-2 rounded-2xl shadow-md min-w-[60px] text-center">
                        <p className="text-[8px] font-bold uppercase opacity-60 leading-none mb-1">Code UG</p>
                        <p className="text-sm font-black leading-none">{u.UG_FINAL || 'N/A'}</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4 border-t border-gray-50 pt-6">
                    <div className="flex items-start gap-4">
                      <div className="p-3 bg-blue-50 rounded-2xl text-[#3A7AFE] shrink-0 shadow-sm"><MapPin size={18}/></div>
                      <div className="pt-1">
                        <p className="text-[9px] font-bold text-gray-300 uppercase leading-none mb-1">Localisation</p>
                        <p className="text-sm font-bold text-gray-600 leading-tight">{u.ADRESSE_VAL || 'Non renseignée'}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                        <div className="flex items-center gap-3">
                          <div className="p-3 bg-gray-50 rounded-2xl text-gray-400 shrink-0"><Zap size={18}/></div>
                          <div>
                            <p className="text-[9px] font-bold text-gray-300 uppercase leading-none mb-1">Surface</p>
                            <p className="text-sm font-black text-gray-700">{u.SURFACE_VAL || 'N/C'} <span className="text-[10px] font-bold text-gray-400">m²</span></p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="p-3 bg-gray-50 rounded-2xl text-gray-400 shrink-0"><Thermometer size={18}/></div>
                          <div>
                            <p className="text-[9px] font-bold text-gray-300 uppercase leading-none mb-1">Énergie</p>
                            <p className="text-sm font-black text-gray-700 truncate max-w-[100px]">{u.ENERGIE_VAL || 'N/C'}</p>
                          </div>
                        </div>
                    </div>

                    <div className="bg-[#F5F7FA] p-5 rounded-[24px] border border-gray-100 mt-4 group-hover:bg-white group-hover:border-blue-100 transition-colors">
                        <div className="flex items-center gap-2 mb-2 text-[#3A7AFE]">
                           <Home size={14} />
                           <p className="text-[10px] font-black uppercase tracking-wider">Équipement Technique</p>
                        </div>
                        <p className="text-sm font-bold text-gray-700 leading-snug mb-2">{u.EQUIP_VAL || 'Information non disponible'}</p>
                        <div className="flex justify-between items-end border-t border-gray-200/50 pt-3 mt-3">
                           <div>
                              <p className="text-[8px] font-bold text-gray-400 uppercase leading-none">Marque / Modèle</p>
                              <p className="text-[10px] font-black text-gray-500 uppercase">{u.MARQUE || 'N/C'}</p>
                           </div>
                           <div className="text-right">
                              <p className="text-[8px] font-bold text-gray-400 uppercase leading-none">Mise en service</p>
                              <p className="text-[10px] font-black text-gray-500">{u.DATE_MES || 'Inconnue'}</p>
                           </div>
                        </div>
                    </div>
                  </div>
                  
                  <div className="mt-6 pt-4 border-t border-gray-50 flex items-center justify-between opacity-40 group-hover:opacity-100 transition-opacity">
                     <span className="text-[9px] font-black text-gray-300 uppercase tracking-widest">Feuille : {u.onglet}</span>
                     <div className="flex items-center gap-1 text-blue-400">
                        <AlertTriangle size={12} />
                        <span className="text-[9px] font-black uppercase">Source : Excel</span>
                     </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full bg-white py-32 px-10 rounded-[50px] text-center border-4 border-dashed border-gray-50 flex flex-col items-center">
                <div className="p-6 bg-blue-50 rounded-full mb-6 text-[#3A7AFE] shadow-inner"><Search size={40} /></div>
                <h2 className="text-xl font-black text-gray-800 uppercase tracking-tighter italic">Recherche Patrimoine</h2>
                <p className="text-gray-400 text-sm mt-4 max-w-sm font-medium leading-relaxed">
                  Saisissez un **Groupe** ou un **Code UG** (ex: 119AL) pour voir apparaître les fiches techniques.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
