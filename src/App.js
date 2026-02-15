import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Thermometer, Zap, Calendar, Loader2, Info, Building2 } from 'lucide-react';

// --- CONFIGURATION : LISTE EXACTE DE TES FICHIERS ---
const FICHIERS_EXCEL = [
  "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx",
  "2-EQUIPEMENTS CHAUFFAGE INDIVIDUEL_NOVEMBRE 2024.xlsx",
  "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx",
  "4 - UG SURFACES - NOVEMBRE 2024.xlsx",
  "5 - PANNEAUX SOLAIRES_NOVEMBRE 2024.xlsx"
];

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ groupe: '', ug: '' });

  useEffect(() => {
    const chargerToutesLesDonnees = async () => {
      try {
        let cumulDonnees = [];

        for (const nomFichier of FICHIERS_EXCEL) {
          const res = await fetch(`/${encodeURIComponent(nomFichier)}`);
          if (!res.ok) {
            console.warn(`Le fichier ${nomFichier} n'a pas pu être chargé.`);
            continue;
          }
          
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab);
          
          // On parcourt tous les onglets de chaque fichier
          wb.SheetNames.forEach(sheetName => {
            const ws = wb.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(ws);
            
            // On nettoie les données pour s'assurer que GROUPE et N°UG existent
            const cleanedData = jsonData.map(item => ({
              ...item,
              // On essaie de mapper les colonnes si les noms varient légèrement
              GROUPE: item.GROUPE || item['GROUPE (HP2)'] || item['Groupe'] || '',
              'N°UG': item['N°UG'] || item['UG'] || item['N° UG'] || '',
              sourceFile: nomFichier,
              onglet: sheetName
            }));
            
            cumulDonnees = [...cumulDonnees, ...cleanedData];
          });
        }

        setData(cumulDonnees);
        setLoading(false);
      } catch (err) {
        console.error("Erreur globale de chargement:", err);
        setLoading(false);
      }
    };

    chargerToutesLesDonnees();
  }, []);

  const filteredResults = useMemo(() => {
    // On ne garde que les lignes qui ont au moins un Groupe ou un N°UG
    return data.filter(item => {
      if (!item.GROUPE && !item['N°UG']) return false;

      const g = String(item.GROUPE).toLowerCase();
      const u = String(item['N°UG']).toLowerCase();
      const searchG = filters.groupe.toLowerCase().trim();
      const searchU = filters.ug.toLowerCase().trim();
      
      return g.includes(searchG) && u.includes(searchU);
    });
  }, [data, filters]);

  return (
    <div className="min-h-screen bg-[#F5F7FA] text-[#4A4A4A] font-sans pb-12">
      <header className="bg-white p-8 border-b border-gray-100 shadow-sm mb-8">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-[#3A7AFE] tracking-tight">Socobat Patrimoine PH</h1>
            <p className="text-gray-400 text-sm mt-1 font-medium italic">Base de données consolidée (Novembre 2024)</p>
          </div>
          <Building2 className="text-gray-200 hidden md:block" size={40} />
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4">
        {/* Barre de Recherche */}
        <div className="bg-white p-6 rounded-[28px] shadow-sm mb-10 flex flex-col md:flex-row gap-4 items-end border border-gray-50">
          <div className="flex-1 w-full text-left">
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2 ml-1">Groupe (HP2)</label>
            <input 
              placeholder="Ex: HP2-045..." 
              className="w-full p-4 bg-[#F5F7FA] rounded-2xl outline-none focus:ring-2 focus:ring-[#3A7AFE] transition-all"
              onChange={e => setFilters({...filters, groupe: e.target.value})}
            />
          </div>
          <div className="flex-1 w-full text-left">
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2 ml-1">N° UG</label>
            <input 
              placeholder="Ex: 1204..." 
              className="w-full p-4 bg-[#F5F7FA] rounded-2xl outline-none focus:ring-2 focus:ring-[#3A7AFE] transition-all"
              onChange={e => setFilters({...filters, ug: e.target.value})}
            />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center py-20">
            <Loader2 className="animate-spin text-[#3A7AFE] mb-4" size={40} />
            <p className="text-gray-500 font-medium text-center">
              Analyse des {FICHIERS_EXCEL.length} fichiers techniques...<br/>
              <span className="text-xs text-gray-400">(Cela peut prendre quelques secondes selon la taille)</span>
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredResults.length > 0 ? (
              filteredResults.map((u, i) => (
                <div key={i} className="bg-white p-8 rounded-[24px] shadow-sm border border-transparent hover:border-blue-100 transition-all hover:shadow-md group">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="font-bold text-xl text-gray-800 group-hover:text-[#3A7AFE] transition-colors uppercase">
                        {u.GROUPE || 'GROUPE INCONNU'}
                      </h3>
                      <p className="text-sm text-gray-400 font-medium italic">Fichier: {u.sourceFile} ({u.onglet})</p>
                    </div>
                    <span className="bg-blue-50 text-[#3A7AFE] px-4 py-1.5 rounded-full text-xs font-bold uppercase">
                      UG {u['N°UG'] || 'N/A'}
                    </span>
                  </div>

                  <div className="space-y-4 border-t border-gray-50 pt-6">
                    <div className="flex items-start gap-3">
                      <div className="p-2 bg-blue-50 rounded-lg text-[#3A7AFE] shrink-0"><MapPin size={18}/></div>
                      <span className="text-sm font-medium leading-relaxed">{u.ADRESSE || u['ADRESSE COMPLETE'] || 'Adresse non renseignée'}</span>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 rounded-lg text-[#3A7AFE] shrink-0"><Zap size={18}/></div>
                      <span className="text-sm font-medium">
                        {u.SCH || u['SURFACE'] || u['SURFACE CHAUFFEE'] || 'Surface non renseignée'} {u.SCH ? 'm²' : ''}
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 rounded-lg text-[#3A7AFE] shrink-0"><Thermometer size={18}/></div>
                      <div className="text-sm font-medium">
                        {u.SYSTEME_CHAUFFAGE || u['EQUIPEMENT'] || 'N/C'}
                        <span className="text-gray-400 font-normal"> — {u.ENERGIE || u['TYPE ENERGIE'] || 'Énergie N/C'}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 text-gray-400 border-t border-gray-50 pt-4 mt-2">
                      <div className="p-2 bg-gray-50 rounded-lg shrink-0"><Info size={16}/></div>
                      <span className="text-xs font-medium uppercase tracking-wider">
                        {u.MARQUE || 'Marque N/C'} • {u.PUISSANCE || u['P_NOMINALE'] || 'Puis. N/C'} • {u.DATE_MES || u['ANNÉE'] || 'Date N/C'}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full bg-white p-16 rounded-[32px] text-center border-2 border-dashed border-gray-100">
                <p className="text-gray-400 font-medium text-lg">Aucun équipement ou bâtiment trouvé.</p>
                <p className="text-gray-300 text-sm mt-2">Essayez de saisir un numéro de groupe (ex: HP2...) ou un numéro d'UG.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
