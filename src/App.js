import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Building2, MapPin, Zap, Loader2, ClipboardCheck, Calculator, Home } from 'lucide-react';

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
    const s = search.trim().toUpperCase();
    if (s.length < 3) return null;

    // 1. RECHERCHE DE L'UG (Fichier 4)
    const ugRow = data.find(r => 
      r.file.includes("4") && String(r.cols[0] || "").toUpperCase().includes(s)
    );

    let hp2 = s;
    let shaUG = "--";
    if (ugRow) {
      hp2 = String(ugRow.cols[1] || "").trim().toUpperCase();
      shaUG = ugRow.cols[11] || "--";
    }

    // 2. SOMME SHA DU GROUPE (Fichier 4 - Colonne L)
    const sumSHA = data
      .filter(r => r.file.includes("4") && String(r.cols[1] || "").toUpperCase() === hp2)
      .reduce((acc, r) => {
        const val = parseFloat(String(r.cols[11]).replace(',', '.'));
        return acc + (isNaN(val) ? 0 : val);
      }, 0);

    // 3. RECHERCHE TECHNIQUE (Collectif d'abord, sinon Individuel)
    let techRow = data.find(r => r.file.includes("1") && String(r.cols[0] || "").toUpperCase() === hp2);
    let typeChauffage = "Collectif";

    if (!techRow) {
      techRow = data.find(r => r.file.includes("2") && String(r.cols[0] || "").toUpperCase() === hp2);
      typeChauffage = techRow ? "Individuel" : "Non répertorié";
    }

    // 4. ADRESSE (Chercher dans Fichier 3 ou n'importe quel fichier contenant le HP2)
    const infoRow = data.find(r => !r.file.includes("4") && String(r.cols[0] || "").toUpperCase() === hp2);

    return {
      hp2,
      typeChauffage,
      nom: infoRow ? (infoRow.cols[2] || infoRow.cols[1]) : "Groupe " + hp2,
      adr: infoRow ? (infoRow.cols[5] || infoRow.cols[4]) : "Adresse N/C",
      shaUG,
      shaTotal: sumSHA.toFixed(2),
      // On adapte les colonnes selon le fichier trouvé
      equip: techRow ? (techRow.file.includes("1") ? `${techRow.cols[14] || ""} ${techRow.cols[15] || ""}` : "Installation Individuelle") : "N/C",
      nrj: techRow ? (techRow.file.includes("1") ? techRow.cols[8] : techRow.cols[9]) : "N/C"
    };
  }, [data, search]);

  return (
    <div className="min-h-screen bg-slate-100 font-sans p-4">
      <div className="max-w-xl mx-auto pt-6">
        <div className="bg-blue-900 text-white p-6 rounded-t-[30px] flex justify-between items-center shadow-lg">
          <div className="flex items-center gap-2">
            <Building2 size={20}/>
            <h1 className="font-black uppercase tracking-tight">Socobat DPE</h1>
          </div>
          <span className="text-[10px] font-bold bg-white/10 px-2 py-1 rounded">MULTI-SOURCES</span>
        </div>

        <div className="bg-white p-6 shadow-xl border-x border-slate-200">
          <input 
            placeholder="N° UG ou Code HP2..." 
            className="w-full p-4 bg-slate-50 border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-500 font-black text-center text-lg shadow-inner"
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="bg-white p-12 text-center rounded-b-[30px]"><Loader2 className="animate-spin mx-auto text-blue-600"/></div>
        ) : result ? (
          <div className="bg-white p-8 rounded-b-[30px] border border-slate-200 shadow-2xl space-y-6">
             <div className="border-b pb-4 flex justify-between items-start">
                <div>
                  <span className="text-[10px] font-black bg-blue-100 text-blue-800 px-2 py-1 rounded uppercase">HP2: {result.hp2}</span>
                  <h2 className="text-xl font-black uppercase mt-2 leading-tight">{result.nom}</h2>
                  <p className="text-slate-400 text-xs font-bold mt-1 flex items-center gap-1"><MapPin size={12}/> {result.adr}</p>
                </div>
                <div className={`text-[9px] font-black px-2 py-1 rounded uppercase ${result.typeChauffage === 'Collectif' ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'}`}>
                  {result.typeChauffage}
                </div>
             </div>

             <div className="bg-blue-700 rounded-[25px] p-6 text-white shadow-xl relative overflow-hidden">
                <div className="flex items-center gap-2 mb-4 opacity-70 border-b border-white/20 pb-2 text-[10px] font-black uppercase tracking-widest">
                   <ClipboardCheck size={14}/> Surfaces SHA
                </div>
                <div className="flex justify-between items-center mb-6 bg-white/10 p-4 rounded-xl">
                   <div className="flex items-center gap-2">
                      <Home size={16} className="text-blue-200"/>
                      <p className="text-xs font-bold uppercase">Surface Logement</p>
                   </div>
                   <p className="text-3xl font-black">{result.shaUG} m²</p>
                </div>
                <div className="flex justify-between items-center px-2">
                   <div className="flex items-center gap-2">
                      <Calculator size={14} className="opacity-50"/>
                      <p className="text-[10px] font-bold uppercase tracking-widest">Somme Groupe (Col L)</p>
                   </div>
                   <p className="text-xl font-black">{result.shaTotal} m²</p>
                </div>
             </div>

             <div className="bg-slate-50 p-5 rounded-[25px] border border-slate-200">
                <p className="text-[10px] font-black text-blue-600 uppercase mb-2 flex items-center gap-1"><Zap size={12}/> Infos Techniques</p>
                <p className="font-bold text-xs italic text-slate-700">{result.equip}</p>
                <div className="mt-4 pt-3 border-t border-slate-200 flex justify-between items-center">
                   <span className="text-[10px] font-black uppercase text-slate-400 italic">Énergie</span>
                   <span className="text-[10px] font-black uppercase text-blue-700 bg-blue-50 px-2 py-1 rounded">{result.nrj}</span>
                </div>
             </div>
          </div>
        ) : search.length > 2 && (
          <div className="bg-white p-12 text-center rounded-b-[30px] text-slate-300 font-black uppercase text-xs">Aucun résultat pour "{search}"</div>
        )}
      </div>
    </div>
  );
}
