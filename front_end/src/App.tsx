import React, { useState, useMemo } from 'react';
import Papa from 'papaparse';
import { motion, AnimatePresence } from 'motion/react';
import { ChevronDown } from 'lucide-react';
import { Job, TabType } from './types';
import { FilterBar } from './components/FilterBar';
import { JobCard } from './components/JobCard';
import { DescriptionPane } from './components/DescriptionPane';
import { ComparisonBoard } from './components/ComparisonBoard';
import { cn } from './lib/utils';

// Dynamic CSV Loader
// This will scan /src/data folder and pick up all files matching matched_master_*.csv
const csvFiles = import.meta.glob('/src/data/matched_master_*.csv', { as: 'raw', eager: true });

const modelsData = Object.entries(csvFiles).map(([path, content]) => {
  const filename = path.split('/').pop() || '';
  const modelName = filename.replace('matched_master_', '').replace('.csv', '');
  
  const results = Papa.parse(content, { header: true, skipEmptyLines: true });
  const jobs = (results.data as any[])
    .map((row, i) => ({
      ...row,
      id: `${modelName}-${i}`,
      match_score: parseInt(row.match_score) || 0,
      model_name: modelName
    }))
    .sort((a, b) => b.match_score - a.match_score) as Job[];

  return { modelName, filename, jobs };
});

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('board');
  const [selectedModelName, setSelectedModelName] = useState<string>(modelsData[0]?.modelName || '');
  const [compModelNameA, setCompModelNameA] = useState<string>(modelsData[0]?.modelName || '');
  const [compModelNameB, setCompModelNameB] = useState<string>(modelsData[1]?.modelName || modelsData[0]?.modelName || '');
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  // Filters
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([]);
  const [selectedDates, setSelectedDates] = useState<string[]>([]);
  const [minScore, setMinScore] = useState<number>(0);

  const currentModel = useMemo(() => modelsData.find(m => m.modelName === selectedModelName), [selectedModelName]);
  const currentJobs = currentModel?.jobs || [];

  const compDataA = useMemo(() => modelsData.find(m => m.modelName === compModelNameA)?.jobs || [], [compModelNameA]);
  const compDataB = useMemo(() => modelsData.find(m => m.modelName === compModelNameB)?.jobs || [], [compModelNameB]);

  // Derived filter options
  const allLocations = useMemo(() => Array.from(new Set(currentJobs.map(j => j.location).filter(Boolean))), [currentJobs]);
  const allCompanies = useMemo(() => Array.from(new Set(currentJobs.map(j => j.company).filter(Boolean))), [currentJobs]);
  const allDates = useMemo(() => Array.from(new Set(currentJobs.map(j => j.processed_date).filter(Boolean))), [currentJobs]);

  // Filtered jobs
  const filteredJobs = useMemo(() => {
    return currentJobs.filter(job => {
      const locationMatch = selectedLocations.length === 0 || selectedLocations.includes(job.location);
      const companyMatch = selectedCompanies.length === 0 || selectedCompanies.includes(job.company);
      const dateMatch = selectedDates.length === 0 || selectedDates.includes(job.processed_date);
      const scoreMatch = job.match_score >= minScore;
      return locationMatch && companyMatch && dateMatch && scoreMatch;
    });
  }, [currentJobs, selectedLocations, selectedCompanies, selectedDates, minScore]);

  const selectedJob = useMemo(() => {
    if (!selectedJobId) return null;
    return currentJobs.find((j: any) => j.id === selectedJobId) || null;
  }, [selectedJobId, currentJobs]);

  const toggleLocation = (loc: string) => {
    setSelectedLocations(prev => prev.includes(loc) ? prev.filter(l => l !== loc) : [...prev, loc]);
  };

  const toggleCompany = (comp: string) => {
    setSelectedCompanies(prev => prev.includes(comp) ? prev.filter(c => c !== comp) : [...prev, comp]);
  };

  const toggleDate = (date: string) => {
    setSelectedDates(prev => prev.includes(date) ? prev.filter(d => d !== date) : [...prev, date]);
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#f8fafc]">
      {/* Top Header */}
      <header className="h-14 flex items-center justify-between px-6 bg-white border-b border-slate-200 shadow-sm shrink-0 z-20">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center text-white font-bold text-sm">JM</div>
            <span className="font-bold text-lg tracking-tight">MatchMaster <span className="text-slate-400 text-xs font-medium ml-1">v2.1</span></span>
          </div>

          <nav className="flex space-x-1">
            <button
              onClick={() => setActiveTab('board')}
              className={cn(
                "px-4 py-1.5 text-sm font-medium rounded-md transition-all",
                activeTab === 'board' ? "bg-blue-50 text-blue-700 border border-blue-100" : "text-slate-500 hover:bg-slate-50"
              )}
            >
              Job Board
            </button>
            <button
              onClick={() => setActiveTab('comparison')}
              className={cn(
                "px-4 py-1.5 text-sm font-medium rounded-md transition-all",
                activeTab === 'comparison' ? "bg-blue-50 text-blue-700 border border-blue-100" : "text-slate-500 hover:bg-slate-50"
              )}
            >
              Comparison Board
            </button>
          </nav>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end mr-4">
            <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Selected Model</span>
            <div className="relative">
              <select
                value={selectedModelName}
                onChange={(e) => setSelectedModelName(e.target.value)}
                className="bg-transparent text-sm font-semibold border-none p-0 focus:ring-0 cursor-pointer appearance-none pr-4"
              >
                {modelsData.map(m => (
                  <option key={m.modelName} value={m.modelName}>{m.filename}</option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>
          <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300"></div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 min-h-0 flex flex-col relative">
        <AnimatePresence mode="wait">
          {activeTab === 'board' ? (
            <motion.div
              key="board"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col h-full overflow-hidden"
            >
              <FilterBar
                locations={allLocations}
                companies={allCompanies}
                dates={allDates}
                selectedLocations={selectedLocations}
                selectedCompanies={selectedCompanies}
                selectedDates={selectedDates}
                minScore={minScore}
                onToggleLocation={toggleLocation}
                onToggleCompany={toggleCompany}
                onToggleDate={toggleDate}
                onScoreChange={setMinScore}
                onClearFilters={() => {
                  setSelectedLocations([]);
                  setSelectedCompanies([]);
                  setSelectedDates([]);
                  setMinScore(0);
                }}
              />

              <div className="flex-1 flex overflow-hidden">
                {/* Left 2/3 - Job Cards */}
                <div className="w-2/3 border-r border-slate-200 bg-slate-50/50 p-4 overflow-y-auto">
                    <div className="flex items-center justify-between mb-4 px-2">
                        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Recent Matches</h2>
                        <div className="text-[10px] text-slate-400 font-medium">
                            Displaying <strong>{filteredJobs.length}</strong> matches
                        </div>
                    </div>
                  <div className="space-y-3 max-w-3xl mx-auto">
                    {filteredJobs.map((job: any) => (
                      <JobCard
                        key={job.id}
                        job={job}
                        isSelected={selectedJobId === job.id}
                        onClick={() => setSelectedJobId(job.id)}
                        onViewDescription={() => setSelectedJobId(job.id)}
                      />
                    ))}
                    {filteredJobs.length === 0 && (
                      <div className="py-20 text-center">
                        <p className="text-slate-400 font-medium">No matches found for the selected filters.</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Right 1/3 - Detail Pane */}
                <div className="w-1/3 bg-white overflow-hidden">
                  <DescriptionPane job={selectedJob} />
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="comparison"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col h-full"
            >
              <div className="bg-white border-b border-slate-200 px-8 py-3 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-4">
                  <div className="flex flex-col">
                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Comp Base (Left)</span>
                    <select 
                      value={compModelNameA} 
                      onChange={(e) => setCompModelNameA(e.target.value)}
                      className="text-xs font-bold text-blue-600 bg-blue-50 border-none rounded px-2 py-1 outline-none appearance-none cursor-pointer"
                    >
                      {modelsData.map(m => (
                        <option key={m.modelName} value={m.modelName}>{m.modelName}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-4 h-px bg-slate-200 mt-4" />
                  <div className="flex flex-col">
                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Differential (Right)</span>
                    <select 
                      value={compModelNameB} 
                      onChange={(e) => setCompModelNameB(e.target.value)}
                      className="text-xs font-bold text-purple-600 bg-purple-50 border-none rounded px-2 py-1 outline-none appearance-none cursor-pointer"
                    >
                      {modelsData.map(m => (
                        <option key={m.modelName} value={m.modelName}>{m.modelName}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="text-[10px] text-slate-400 italic">Comparing delta in analysis patterns</div>
              </div>
              <div className="flex-1 overflow-y-auto bg-gray-50/30">
                <ComparisonBoard
                  model1Jobs={compDataA}
                  model2Jobs={compDataB}
                  model1Name={compModelNameA}
                  model2Name={compModelNameB}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer Status Bar */}
      <footer className="px-6 py-1 bg-slate-900 text-white flex justify-between items-center text-[10px] tracking-wide shrink-0">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Connected to CSV Engine</span>
          </div>
          <span className="opacity-40">|</span>
          <span>Latency: 142ms</span>
        </div>
        <div className="opacity-60 uppercase font-bold tracking-widest text-[9px]">
           MatchMaster v2.1 Terminal
        </div>
      </footer>
    </div>
  );
}
