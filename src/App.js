import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Building2, MapPin, Zap, Loader2, ClipboardCheck, Calculator, Home, AlertCircle } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

// Fonction de nettoyage extrême : enlève tout sauf lettres et chiffres
const superClean = (v) => String(v || "").toLowerCase().replace(/[^a-z0-9]/g, '');

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const loadData = async () => {
      let tempAll = [];
      for (const f of FICHIERS_EXCEL) {
        try {
          const res = await fetch(`/${encodeURIComponent(f)}`);
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          wb.SheetNames.forEach(sn => {
            const rows = XLSX.utils.sheet_to_json(wb.Sheets[sn], { header: 1 });
            tempAll.push(...rows.map(r => ({ cols: r, file: f })));
          });
        } catch (e) { console.error(e); }
      }
      setData(tempAll);
      setLoading(false);
    };
    loadData();
  }, []);

  const result = useMemo(() => {
    const s = superClean(search);
    if (s.length < 3) return null;

    // 1. CHERCHER L'UG PARTOUT (Scan de toutes les colonnes)
    const ugRow = data.find(r => 
      r.cols.some(cell => superClean(cell) === s || (s.length >= 5 && superClean(cell).endsWith(s)))
    );

    let hp2 = "";
    let shaUG = "--";

    if (ugRow) {
      // On cherche le HP2 dans la ligne trouvée (souvent colonne B ou index 1)
      hp2 = superClean(ugRow.cols[1] || ugRow.cols[0]);
      shaUG = ugRow.cols[11] || ugRow.cols[12] || "--"; // Colonne L ou M
    } else {
      // Si pas d'UG trouvée, on teste si la recherche est elle-même un HP2
      hp2 = s;
    }

    // 2. SOMME SHA (Fichier 4 - Colonne L)
    const sumSHA = data
      .filter(r => (r.file.includes("4") || r.file.includes("ug")) && r.cols.some(c => superClean(c) === hp2))
      .reduce((acc, r) => {
        const val = parseFloat(String(r.cols[11] || 0).replace(',', '.'));
        return acc + (isNaN(val) ? 0 : val);
      }, 0);

    // 3. RECUPERER INFOS TECHNIQUES (Scan multicritères)
    const techRows = data.filter(r => r.cols.some(c => superClean(c) === hp2));
    
    const findCell = (keywords, minLen = 4) => {
      for (const r of techRows) {
        const lineStr = r.cols.join(" ").toUpperCase();
        if (keywords.some(k => lineStr.includes(k))) {
          return r.cols.find(c => String(c).length >= minLen && superClean(c) !== hp2) || "N/C";
        }
      }
      return "N/C";
    };

    if (techRows.length === 0 && !ugRow) return null;

    return {
      hp2: hp2.toUpperCase(),
      nom: findCell(["ALSACE", "VAUGIRARD", "AUBERVILLIERS", "SOLIDARI", "NOM"], 6),
      adr: findCell(["RUE", "AVENUE", "BOULEVARD", "PASSAGE", "ADRESSE"], 8),
      shaUG,
      shaTotal: sumSHA.toFixed(2),
      equip: findCell(["CHAUDIERE", "ECHANGEUR", "CPCU", "GAZ", "BALLON", "EQUIPEMENT"], 10),
      nrj: findCell(["GAZ", "CPCU", "FIOUL", "ELEC"], 3)
    };
  }, [data, search]);

  return (
    <div className="min-h-screen bg-slate-100 font-sans p-4">
      <div className="max-w-xl mx-auto pt-6">
        <header className="bg-slate-900 text-white p-6 rounded-t-[30px] flex justify-between items-center shadow-lg">
          <div className="flex items-center gap-2">
            <Building2 className="text-blue-400" />
            <h1 className="font-black uppercase tracking-tighter">Socobat PH</h1>
          </div>
          <span className="text-[10px] font-bold bg-white/10 px-3 py-1 rounded-full">{data.length} LIGNES</span>
        </header>

        <div className="bg-white p-6 shadow-xl border-x border-slate-200">
          <div className="relative">
            <input 
              placeholder="Tapez l'UG (ex: 151799)..." 
              className="w-full p-5 bg-slate-50 border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-500 font-black text-center text-xl shadow-inner"
              onChange={e => setSearch(e.target.value)}
            />
            {search.length > 0 && search.length < 3 && (
              <p className="text-[9px] text-orange-500 font-bold mt-2 text-center uppercase">Entrez au moins 3 caractères</p>
            )}
          </div>
        </div>

        {loading ? (
          <div className="bg-white p-12 text-center rounded-b-[30px] border border-slate-200">
            <Loader2 className="animate-spin mx-auto text-blue-600 mb-2" />
            <p className="text-[10px] font-black uppercase text-slate-400 tracking-widest">Initialisation des 5 bases...</p>
          </div>
        ) : result ? (
          <div className="bg-white p-8 rounded-b-[30px] border border-slate-200 shadow-2xl space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
             <div className="border-b pb-5">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-black bg-blue-600 text-white px-2 py-1 rounded uppercase">HP2: {result.hp2}</span>
                </div>
                <h2 className="text-2xl font-black uppercase leading-tight mt-3 text-slate-800">{result.nom}</h2>
                <div className="flex items-start gap-2 text-slate-400 font-bold text-xs mt-2">
                  <MapPin size={14} className="mt-0.5 text-blue-500" />
                  <span>{result.adr}</span>
                </div>
             </div>

             <div className="bg-blue-600 rounded-[30px] p-7 text-white shadow-xl relative overflow-hidden">
                <div className="flex items-center gap-2 mb-5 opacity-70 border-b border-white/20 pb-2 text-[10px] font-black uppercase tracking-[0.2em]">
                   <ClipboardCheck size={16}/> Synthèse DPE
                </div>
                
                <div className="flex justify-between items-center mb-6 bg-white/10 p-4 rounded-2xl border border-white/5">
                   <div>
                      <p className="text-[10px] font-black uppercase text-blue-100">Surface Logement</p>
                      <p className="text-[9px] opacity-70 italic font-medium">Colonne L (SHA)</p>
                   </div>
                   <p className="text-4xl font-black tracking-tighter">{result.shaUG} m²</p>
                </div>

                <div className="flex justify-between items-center px-4">
                   <div className="flex items-center gap-2">
                      <Calculator size={14} className="opacity-50"/>
                      <p className="text-[10px] font-black uppercase text-blue-100">Cumul Groupe</p>
                   </div>
                   <p className="text-xl font-black tracking-tighter">{result.shaTotal} m²</p>
                </div>
             </div>

             <div className="bg-slate-50 p-6 rounded-[25px] border border-slate-200">
                <div className="flex items-center gap-2 mb-4">
                  <Zap size={16} className="text-blue-600" />
                  <p className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Infos Techniques</p>
                </div>
                <p className="font-bold text-sm italic text-slate-700 leading-snug">{result.equip}</p>
                <div className="mt-5 pt-4 border-t border-slate-200 flex justify-between items-center">
                   <span className="text-[10px] font-black uppercase text-slate-300">Combustible</span>
                   <span className="text-[10px] font-black uppercase text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">{result.nrj}</span>
                </div>
             </div>
          </div>
        ) : search.length >= 3 && (
          <div className="bg-white p-12 text-center rounded-b-[30px] border border-slate-200 flex flex-col items-center gap-3">
             <AlertCircle className="text-slate-200" size={40} />
             <p className="text-slate-400 font-black uppercase text-[10px] tracking-widest">Aucune donnée trouvée pour "{search}"</p>
             <p className="text-[9px] text-slate-300 italic">Vérifiez le numéro d'UG ou le code Groupe.</p>
          </div>
        )}
      </div>
    </div>
  );
}
