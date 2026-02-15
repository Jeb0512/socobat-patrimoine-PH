import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { Building2, MapPin, Zap, Loader2, Sun, ClipboardCheck, Calculator } from 'lucide-react';

const FICHIERS_EXCEL = [
  "1-equipements chauffage collectif_novembre 2024.xlsx",
  "2-equipements chauffage individuel_novembre 2024.xlsx",
  "3 - batiments_surfaces_novembre 2024.xlsx",
  "4 - ug surfaces - novembre 2024.xlsx",
  "5 - panneaux solaires_novembre 2024.xlsx"
];

const normalize = (val) => String(val || "").trim().toUpperCase().replace(/\s/g, '');

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const load = async () => {
      let all = [];
      for (const f of FICHIERS_EXCEL) {
        try {
          const res = await fetch(`/${encodeURIComponent(f)}`);
          if (!res.ok) continue;
          const ab = await res.arrayBuffer();
          const wb = XLSX.read(ab, { type: 'array' });
          wb.SheetNames.forEach(sn => {
            // On lit tout en format texte pour ne rien rater
            const json = XLSX.utils.sheet_to_json(wb.Sheets[sn], { defval: "" });
            all.push(...json.map(r => ({ ...r, _F: f, _STRING: Object.values(r).join("|").toUpperCase() })));
          });
        } catch (e) { console.error(e); }
      }
      setData(all);
      setLoading(false);
    };
    load();
  }, []);

  const result = useMemo(() => {
    const s = normalize(search);
    if (s.length < 3) return null;

    // 1. Trouver n'importe quelle ligne qui contient la recherche
    const match = data.find(r => r._STRING.includes(s));
    if (!match) return null;

    // 2. Identifier le code HP2 dans cette ligne (On cherche un motif type 119AL ou 515VA)
    const hp2Candidate = Object.values(match).find(v => {
      const val = normalize(v);
      return val.length >= 4 && val.length <= 7 && /[0-9]/.test(val) && /[A-Z]/.test(val);
    }) || s;

    const hp2 = normalize(hp2Candidate);

    // 3. Récupérer TOUTES les lignes liées à ce HP2
    const groupRows = data.filter(r => r._STRING.includes(hp2));

    // 4. Calcul de la somme des surfaces (On cherche des nombres dans le fichier 4)
    let totalSHA = 0;
    let specificSHA = "--";

    groupRows.forEach(r => {
      if (r._F.includes("4") || r._F.includes("ug")) {
        // On cherche une valeur numérique qui ressemble à une surface (entre 9 et 200)
        const surfaces = Object.values(r).map(v => parseFloat(String(v).replace(',', '.'))).filter(v => v > 5 && v < 500);
        const val = surfaces[0] || 0;
        totalSHA += val;
        // Si c'est la ligne de l'UG cherchée
        if (r._STRING.includes(s)) specificSHA = val;
      }
    });

    const getInfo = (keys) => {
      for (const r of groupRows) {
        for (const [k, v] of Object.entries(r)) {
          if (keys.some(key => k.toUpperCase().includes(key)) && String(v).length > 3) return v;
        }
      }
      return "N/C";
    };

    return {
      hp2,
      nom: getInfo(["NOM", "LIBELLE", "GROUPE"]) || hp2,
      adr: getInfo(["ADRESSE", "RUE", "LOCALISATION"]),
      shaUG: specificSHA,
      shaTotal: totalSHA.toFixed(2),
      equip: getInfo(["EQUIPEMENT", "CHAUFFAGE", "DESIGNATION", "CHAUDIERE"]),
      nrj: getInfo(["ENERGIE", "COMBUSTIBLE", "TYPE"]),
      solaire: groupRows.some(r => r._F.includes("panneaux"))
    };
  }, [data, search]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20 font-sans">
      <header className="bg-blue-700 p-6 shadow-lg flex justify-between items-center text-white">
        <h1 className="font-black uppercase tracking-tighter italic flex items-center gap-2">
          <Building2 /> Socobat PH
        </h1>
        <div className="text-[10px] font-bold bg-white/20 px-3 py-1 rounded-full">{data.length} LIGNES</div>
      </header>

      <main className="max-w-2xl mx-auto px-4 pt-10">
        <div className="bg-white p-6 rounded-[30px] shadow-xl mb-10 border-2 border-blue-100">
          <input 
            placeholder="Tapez l'UG (ex: 151799) ou le HP2 (ex: 515VA)..." 
            className="w-full p-4 bg-slate-50 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold text-lg text-center"
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="text-center py-20 animate-pulse font-bold text-slate-400">CHARGEMENT...</div>
        ) : result ? (
          <div className="bg-white rounded-[40px] shadow-2xl overflow-hidden border-b-8 border-b-blue-700">
            <div className="p-10">
              <span className="bg-slate-900 text-white text-[10px] font-black px-3 py-1 rounded-lg uppercase mb-4 inline-block">ID: {result.hp2}</span>
              <h2 className="text-3xl font-black uppercase mb-2 leading-none">{result.nom}</h2>
              <p className="flex items-center gap-2 text-slate-500 font-bold text-sm mb-10"><MapPin size={16}/> {result.adr}</p>

              <div className="grid gap-6">
                <div className="bg-blue-600 text-white p-8 rounded-[40px] shadow-xl shadow-blue-200">
                  <div className="flex items-center gap-2 mb-6 opacity-80 border-b border-white/20 pb-3 uppercase text-[10px] font-black">
                    <ClipboardCheck size={18}/> Données de Surface (SHA)
                  </div>
                  <div className="flex justify-between items-center mb-6">
                    <p className="text-xs font-bold uppercase">Logement (UG)</p>
                    <p className="text-4xl font-black">{result.shaUG} m²</p>
                  </div>
                  <div className="flex justify-between items-center pt-4 border-t border-white/10">
                    <p className="text-xs font-bold uppercase opacity-80">Total Groupe (Calculé)</p>
                    <p className="text-xl font-black">{result.shaTotal} m²</p>
                  </div>
                </div>

                <div className="bg-slate-50 p-8 rounded-[40px] border border-slate-100">
                  <p className="text-[10px] font-black uppercase text-blue-600 mb-4">Équipement Technique</p>
                  <p className="font-bold text-sm italic mb-6 text-slate-700">{result.equip}</p>
                  <div className="flex justify-between font-black text-[10px] uppercase pt-4 border-t">
                    <span className="text-slate-400">Énergie</span>
                    <span className="text-blue-600">{result.nrj}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : search.length > 2 && (
          <div className="text-center py-20 text-slate-300 font-black uppercase tracking-widest">Aucune correspondance</div>
        )}
      </main>
    </div>
  );
}
