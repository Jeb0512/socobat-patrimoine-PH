import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Thermometer, Zap, Calendar, Loader2, Building2, AlertTriangle, Sun } from 'lucide-react';

// --- CONFIGURATION : NOMS EXACTS DES FICHIERS SUR GITHUB ---
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
  const [status, setStatus] = useState("Connexion au serveur...");
  const [filters, setFilters] = useState({ groupe: '', ug: '' });

  useEffect(() => {
    const chargerToutesLesDonnees = async () => {
      let cumulDonnees = [];
      
      for (const nomFichier of FICHIERS_EXCEL) {
        try {
          setStatus(`Lecture de : ${nomFichier}...`);
          
          // Le chemin commence par / car ils sont dans le dossier public
          const res = await fetch(`/${encodeURIComponent(nomFichier)}`);
          
          if (!res.ok) {
            console.error(`Erreur 404 : Le fichier ${nomFichier} est introuvable.`);
            continue;
          }
          
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          
          wb.SheetNames.forEach(sheetName => {
            const ws = wb.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(ws, { defval: "" });
            
            const cleanedData = jsonData.map(item => ({
              ...item,
              // Mapping flexible pour gérer toutes les variantes de noms de colonnes
              GROUPE_FINAL: String(item.GROUPE || item['GROUPE (HP2)'] || item['Groupe'] || item['GROUPE '] || "").trim(),
              UG_FINAL: String(item['N°UG'] || item['UG'] || item['N° UG'] || item['Code UG'] || "").trim(),
              ADRESSE_VAL: item.ADRESSE || item['ADRESSE COMPLETE'] || item['Localisation'] || item['COMMUNE'] || "",
              SURFACE_VAL: item.SCH || item['SURFACE'] || item['SURFACE DES UG'] || item['SURFACE BATIMENT'] || item['Surface'] || "",
              EQUIP_VAL: item.SYSTEME_CHAUFFAGE || item['EQUIPEMENT'] || item['Désignation'] || item['Type'] || "",
              ENERGIE_VAL: item.ENERGIE || item['TYPE ENERGIE'] || item['Energie'] || "",
              sourceFile: nomFichier,
              onglet: sheetName
            }));
            
            cumulDonnees = [...cumulDonnees, ...cleanedData];
          });
        } catch (err) {
          console.error(`Erreur technique sur ${nomFichier}:`, err);
        }
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
      const matchG = sG === '' || item.GROUPE_FINAL.toLowerCase().includes(sG);
      const matchU = sU === '' || item.UG_FINAL.toLowerCase().includes(sU);
      return matchG && matchU;
    });
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-[#F5F7FA] text-[#4A4A4A] font-sans pb-12">
      {/* Header Alan Style */}
      <header className="bg-white p-6 border-b border-gray-100 shadow-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
             <div className="bg-[#3A7AFE] p-2 rounded-lg text-white">
                <Building2 size={24} />
             </div>
             <div>
                <h1 className="text-xl font-bold text-gray-900 leading-none">Socobat Patrimoine PH</h1>
                <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">Consultation Technique</p>
             </div>
          </div>
          {!loading && (
            <div className="hidden md:block text-right">
              <p className="text-[10px] font-bold text-gray-400 uppercase leading-none">Base synchronisée</p>
              <p className="text-sm font-bold text-[#3A7AFE]">{data.length} entrées</p>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-5xl mx-auto p-4 md:p-8">
        {/* Barre de Recherche */}
        <div className="bg-white p-6 rounded-[28px] shadow-[0_4px_24px_rgba(0,0,0,0.04)] mb-8 flex flex-col md:flex-row gap-6 border border-gray-50">
          <div className="flex-1">
            <label className="text-[11px] font-bold text-gray-400 uppercase ml-1 block mb-2">Groupe (HP2)</label>
            <div className="relative group">
              <input 
                placeholder="Ex: HP2-045" 
                className="w-full p-4 bg-[#F5F7FA] rounded-2xl outline-none focus:ring-2 focus:ring-[#3A7AFE] transition-all text-sm font-semibold text-gray-700"
                onChange={e => setFilters({...filters, groupe: e.target.value})}
              />
              <Search className="absolute right-4 top-4 text-gray-300 group-focus-within:text-[#3A7AFE] transition-colors" size={18} />
            </div>
          </div>
          <div className="flex-1">
            <label className="text-[11px] font-bold text-gray-400 uppercase ml-1 block mb-2">N° UG</label>
            <div className="relative group">
              <input 
                placeholder="Ex: 1204" 
                className="w-full p-4 bg-[#F5F7FA] rounded-2xl outline-none focus:ring-2 focus:ring-[#3A7AFE] transition-all text-sm font-semibold text-gray-700"
                onChange={e => setFilters({...filters, ug: e.target.value})}
              />
              <Search className="absolute right-4 top-4 text-gray-300 group-focus-within:text-[#3A7AFE] transition-colors" size={18} />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-[32px] border border-gray-100 shadow-sm">
            <Loader2 className="animate-spin text-[#3A7AFE] mb-6" size={48} />
            <p className="text-gray-500 font-bold text-lg animate-pulse">{status}</p>
            <p className="text-gray-300 text-sm mt-2">Veuillez patienter pendant la lecture des fichiers...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredResults.length > 0 ? (
              filteredResults.map((u, i) => (
                <div key={i} className="bg-white p-8 rounded-[30px] shadow-sm border border-transparent hover:border-blue-100 transition-all hover:shadow-xl group relative overflow-hidden">
                  {u.sourceFile.includes("panneaux") && (
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20">
                      <Sun size={60} className="text-orange-400" />
                    </div>
                  )}
                  
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <span className="text-[9px] font-black text-[#3A7AFE] bg-blue-50 px-2.5 py-1 rounded-md uppercase mb-2 block w-fit">
                        {u.sourceFile.split(' ')[0]}
                      </span>
                      <h3 className="font-bold text-xl text-gray-900 uppercase tracking-tight leading-tight">
                        {u.GROUPE_FINAL || 'Groupe N/C'}
                      </h3>
                    </div>
                    <div className="text-right">
                      <p className="text-[9px] font-bold text-gray-300 uppercase mb-1">Unité de Gestion</p>
                      <p className="text-xl font-black text-gray-900 leading-none">
                        {u.UG_FINAL || 'N/A'}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-4 border-t border-gray-50 pt-6">
                    <div className="flex items-start gap-4">
                      <div className="p-2.5 bg-blue-50 rounded-xl text-[#3A7AFE] shrink-0"><MapPin size={18}/></div>
                      <span className="text-sm font-semibold text-gray-600 leading-snug">{u.ADRESSE_VAL || 'Adresse non renseignée'}</span>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="p-2.5 bg-blue-50 rounded-xl text-[#3A7AFE] shrink-0"><Zap size={18}/></div>
                      <span className="text-sm font-bold text-gray-700">
                        {u.SURFACE_VAL ? `${u.SURFACE_VAL} m²` : 'Surface non renseignée'}
                      </span>
                    </div>

                    <div className="flex items-start gap-4">
                      <div className="p-2.5 bg-blue-50 rounded-xl text-[#3A7AFE] shrink-0"><Thermometer size={18}/></div>
                      <div className="text-sm font-bold text-gray-700 leading-tight pt-1">
                        {u.EQUIP_VAL || 'Équipement non renseigné'}
                        <div className="text-[10px] text-gray-400 uppercase tracking-wide mt-1.5 font-bold">
                          Énergie : {u.ENERGIE_VAL || 'N/C'}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-8 pt-4 border-t border-gray-50 flex items-center justify-between">
                     <span className="text-[10px] font-bold text-gray-300 uppercase tracking-wider">Feuille : {u.onglet}</span>
                     <div className="flex items-center gap-1.5 text-blue-300 group-hover:text-[#3A7AFE] transition-colors">
                        <AlertTriangle size={12} />
                        <span className="text-[9px] font-bold uppercase">Multi-source</span>
                     </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full bg-white py-24 px-6 rounded-[40px] text-center border-2 border-dashed border-gray-100 flex flex-col items-center">
                {filters.groupe || filters.ug ? (
                  <>
                    <div className="p-4 bg-gray-50 rounded-full mb-4"><AlertTriangle size={32} className="text-gray-300"/></div>
                    <p className="text-gray-500 font-bold text-lg">Aucune donnée trouvée.</p>
                    <p className="text-gray-300 text-sm mt-1">Vérifiez vos critères ou tentez une recherche plus large.</p>
                  </>
                ) : (
                  <>
                    <div className="p-4 bg-blue-50 rounded-full mb-4 text-[#3A7AFE]"><Search size={32} /></div>
                    <p className="text-gray-500 font-bold text-lg leading-none">Prêt pour la recherche</p>
                    <p className="text-gray-300 text-sm mt-3 max-w-xs mx-auto font-medium leading-relaxed">
                      Saisissez un **Groupe (HP2)** ou un **N° UG** pour extraire les données techniques consolidées.
                    </p>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
