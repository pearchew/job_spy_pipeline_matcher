import React from 'react';
import { Job } from '../types';
import { ArrowRight, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '../lib/utils';

interface ComparisonBoardProps {
  model1Jobs: Job[];
  model2Jobs: Job[];
  model1Name: string;
  model2Name: string;
}

export const ComparisonBoard: React.FC<ComparisonBoardProps> = ({
  model1Jobs,
  model2Jobs,
  model1Name,
  model2Name
}) => {
  // Merge jobs by title/company to compare
  const mergedJobs = model1Jobs.map(job => {
    const matchingJob = model2Jobs.find(m2j => m2j.title === job.title && m2j.company === job.company);
    return {
      title: job.title,
      company: job.company,
      description: job.description,
      m1: job,
      m2: matchingJob
    };
  });

  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="max-w-[1600px] mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-black text-slate-800 tracking-tight uppercase">Cross-Model Comparison</h1>
          <p className="text-slate-400 mt-1 text-sm font-medium tracking-wide">Differential analysis between {model1Name} and {model2Name}</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
           {/* Table Header */}
          <div className="grid grid-cols-[1fr_1fr_1fr] bg-slate-900 text-white font-bold text-[10px] uppercase tracking-[0.2em] sticky top-0 z-10">
            <div className="p-4 border-r border-slate-800">Job Metadata</div>
            <div className="p-4 border-r border-slate-800 flex justify-between items-center px-6">
               <div className="flex items-center gap-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                 <span>{model1Name}</span>
               </div>
               <span className="opacity-40 font-mono tracking-normal">ENGINE_A</span>
            </div>
            <div className="p-4 flex justify-between items-center px-6">
               <div className="flex items-center gap-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                 <span>{model2Name}</span>
               </div>
               <span className="opacity-40 font-mono tracking-normal">ENGINE_B</span>
            </div>
          </div>

          {mergedJobs.map((item, idx) => {
            const scoreDiff = item.m2 ? item.m2.match_score - item.m1.match_score : 0;

            return (
              <div key={idx} className="grid grid-cols-[1fr_1fr_1fr] border-b border-slate-100 hover:bg-slate-50/50 transition-colors group">
                {/* Description Column */}
                <div className="p-5 border-r border-slate-100 bg-white group-hover:bg-slate-50/50">
                  <h4 className="font-bold text-slate-800 text-sm leading-tight mb-1">{item.title}</h4>
                  <p className="text-[10px] font-bold text-blue-600 uppercase tracking-wider mb-3 leading-none">{item.company}</p>
                  <div className="text-[11px] text-slate-500 line-clamp-[5] leading-relaxed">
                    {item.description}
                  </div>
                </div>

                {/* Model 1 Column */}
                <div className="p-5 border-r border-slate-100 space-y-4">
                  <div className="flex justify-between items-end">
                    <span className="text-2xl font-mono font-black text-slate-900">{item.m1.match_score}<span className="text-[10px] font-bold text-slate-300 ml-0.5">%</span></span>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <p className="text-[9px] font-black text-blue-600 uppercase tracking-widest mb-1.5">Skills</p>
                      <p className="text-[10px] leading-relaxed text-slate-600 line-clamp-3">{item.m1.matched_skills}</p>
                    </div>
                    <div>
                      <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Gaps</p>
                      <p className="text-[10px] leading-relaxed text-slate-500 line-clamp-3">{item.m1.gaps_in_skill}</p>
                    </div>
                  </div>
                </div>

                {/* Model 2 Column */}
                <div className="p-5 space-y-4">
                  <div className="flex justify-between items-end">
                    <span className="text-2xl font-mono font-black text-slate-900">
                      {item.m2?.match_score ?? 'N/A'}<span className="text-[10px] font-bold text-slate-300 ml-0.5">%</span>
                    </span>
                    {item.m2 && (
                      <div className={cn(
                        "flex items-center text-[10px] font-black mb-1.5",
                        scoreDiff > 0 ? "text-emerald-500" : scoreDiff < 0 ? "text-rose-500" : "text-slate-300"
                      )}>
                        {scoreDiff > 0 ? <TrendingUp className="w-2.5 h-2.5 mr-1" /> : scoreDiff < 0 ? <TrendingDown className="w-2.5 h-2.5 mr-1" /> : <Minus className="w-2.5 h-2.5 mr-1" />}
                        {Math.abs(scoreDiff)}pts
                      </div>
                    )}
                  </div>
                  <div className="space-y-3">
                    <div>
                      <p className="text-[9px] font-black text-blue-600 uppercase tracking-widest mb-1.5">Skills</p>
                      <p className="text-[10px] leading-relaxed text-slate-600 line-clamp-3">{item.m2?.matched_skills ?? '-'}</p>
                    </div>
                    <div>
                      <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Gaps</p>
                      <p className="text-[10px] leading-relaxed text-slate-500 line-clamp-3">{item.m2?.gaps_in_skill ?? '-'}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
