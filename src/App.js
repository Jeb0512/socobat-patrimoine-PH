import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Building2, MapPin, Zap, Loader2, ClipboardCheck, Calculator } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

export default function App() {
  const [allCells, setAllCells] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const loadData = async () => {
      let tempCells = [];
      for (const f of FICHIERS_EXCEL) {
        try {
          const res = await fetch(`/${encodeURIComponent(f)}`);
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          wb.SheetNames.forEach(sn => {
            // header: 1 force la lecture en tableau de tableaux (brut)
            const rows = XLSX.utils.sheet_to_json(wb.Sheets[sn], { header: 1 });
            rows.forEach((row, rowIndex) => {
              if (row.length > 0) {
                tempCells.push({
                  content: row.map(c => String(c || "").trim()),
                  file: f
                });
              }
            });
          });
        } catch (e) { console.error(`Erreur sur ${f}`, e); }
      }
      setAllCells(tempCells);
      setLoading(false);
    };
    loadData();
  }, []);

  const result = useMemo(() => {
    const s = search.trim().toUpperCase();
    if (s.length < 3) return null;

    // 1. Trouver la ligne qui contient exactement ou partiellement la recherche
    const matchLine = allCells.find(line => 
      line.content.some(cell => cell.toUpperCase().includes(s))
    );

    if (!matchLine) return null;

    // 2. Identifier le Code HP2 (souvent 4 à 6 caractères, lettres et chiffres)
    // On cherche dans la ligne trouvée ce qui ressemble à un code groupe
    const hp2 = matchLine.content.find(cell => 
      cell.length >= 4 && cell.length <= 7 && /[0-9]/.test(cell) && /[A-Z]/.test(cell)
    ) || s;

    // 3. Récupérer toutes les lignes liées à ce HP2 dans tous les fichiers
    const relatedLines = allCells.filter(line => 
      line.content.some(cell => cell.toUpperCase() === hp2.toUpperCase())
    );

    // 4. Calcul de la somme des SHA (Fichier 4 - Colonne L = Index 11)
    let sumSHA = 0;
    let specificSHA = "--";

    relatedLines.forEach(line => {
      if (line.file.includes("4") || line.file.includes("ug")) {
        // Dans le fichier 4, la SHA est en colonne L (index 11)
        const val = parseFloat(String(line.content[11] || 0).replace(',', '.'));
        if (!isNaN(val) && val > 0) sumSHA += val;
        
        // Si c'est la ligne précise de l'UG cherchée
        if (line.content.some(cell => cell.toUpperCase().includes(s))) {
          specificSHA = val || "--";
        }
      }
    });

    // 5. Trouver les infos (Adresse, Equipement)
    const findInArray = (keywords) => {
      for (const line of relatedLines) {
        const text = line.content.join(" ").toUpperCase();
        if (keywords.some(kw => text.includes(kw))) {
          return line.content.find(c => c.length > 5 && !c.includes(hp2)) || "";
        }
      }
      return "N/C";
    };

    return {
      hp2,
      nom: findInArray(["ALSACE", "VAUGIRARD", "AUBERVILLIERS", "SOLIDARITE"]),
      adr: findInArray(["RUE", "AVENUE", "BOULEVARD", "PASSAGE"]),
      shaUG: specificSHA,
      shaTotal: sumSHA.toFixed(2),
      equip: findInArray(["CHAUDIERE", "ECHANGEUR", "CPCU", "GAZ", "BALLON"]),
      nrj: findInArray(["GAZ", "CPCU", "FIOUL", "ELEC"])
    };
  }, [allCells, search]);

  return (
    <div className="min-h-screen bg-slate-100 font-sans p-4">
      <div className="max-w-xl mx-auto pt-10">
        <div className="bg-blue-600 text-white p-6 rounded-t-[30px] flex justify-between items-center shadow-lg">
          <h1 className="font-black uppercase italic tracking-tighter">Socobat PH</h1>
          <span className="text-[10px] font-bold bg-white/20 px-2 py-1 rounded">{allCells.length} Lignes</span>
        </div>

        <div className="bg-white p-6 shadow-xl border-x border-slate-200">
          <input 
            placeholder="Tapez l'UG (ex: 151799) ou le HP2..." 
            className="w-full p-4 bg-slate-50 border-2 border-slate-100 rounded-2xl outline-none focus:border-blue-500 font-black text-center text-lg"
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="bg-white p-10 text-center rounded-b-[30px] border border-slate-200">
            <Loader2 className="animate-spin mx-auto text-blue-600 mb-2" />
            <p className="text-[10px] font-black uppercase text-slate-400">Analyse du patrimoine...</p>
          </div>
        ) : result ? (
          <div className="bg-white p-8 rounded-b-[30px] border border-slate-200 shadow-2xl space-y-6">
             <div className="border-b pb-4">
                <span className="text-[10px] font-black bg-slate-100 px-2 py-1 rounded text-slate-500 uppercase">Groupe {result.hp2}</span>
                <h2 className="text-2xl font-black uppercase leading-tight mt-2">{result.nom || result.hp2}</h2>
                <p className="text-slate-400 text-xs font-bold mt-1 flex items-center gap-1"><MapPin size={12}/> {result.adr}</p>
             </div>

             <div className="bg-blue-600 rounded-[25px] p-6 text-white shadow-inner">
                <div className="flex items-center gap-2 mb-4 opacity-70 border-b border-white/20 pb-2">
                   <ClipboardCheck size={16}/>
                   <span className="text-[10px] font-black uppercase tracking-widest">Surfaces HabitaBles</span>
                </div>
                <div className="flex justify-between items-center mb-4">
                   <p className="text-xs font-bold uppercase">UG Logement</p>
                   <p className="text-3xl font-black">{result.shaUG} m²</p>
                </div>
                <div className="flex justify-between items-center pt-4 border-t border-white/10">
                   <div className="flex items-center gap-2">
                      <Calculator size={14} className="opacity-50"/>
                      <p className="text-[10px] font-bold uppercase">Total Groupe (L)</p>
                   </div>
                   <p className="text-xl font-black">{result.shaTotal} m²</p>
                </div>
             </div>

             <div className="bg-slate-50 p-5 rounded-[25px] border border-slate-100">
                <p className="text-[10px] font-black text-blue-600 uppercase mb-2">Technique</p>
                <p className="font-bold text-sm italic text-slate-700 leading-snug">{result.equip}</p>
                <p className="text-[10px] font-black text-blue-400 uppercase mt-4">Énergie: {result.nrj}</p>
             </div>
          </div>
        ) : search.length > 2 && (
          <div className="bg-white p-10 text-center rounded-b-[30px] text-slate-300 font-black uppercase text-xs tracking-widest">
             Aucune donnée trouvée
          </div>
        )}
      </div>
    </div>
  );
}
