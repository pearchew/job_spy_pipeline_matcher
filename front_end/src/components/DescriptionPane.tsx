import React from 'react';
import { Job } from '../types';
import { Target, AlertCircle, Sparkles, Files } from 'lucide-react';

interface DescriptionPaneProps {
  job: Job | null;
}

export const DescriptionPane: React.FC<DescriptionPaneProps> = ({ job }) => {
  if (!job) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-slate-300 p-8 text-center bg-white">
        <Files className="w-12 h-12 mb-4 opacity-10" />
        <p className="text-sm font-medium">Select a candidate match to view full profile insights</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      <div className="p-6 border-b border-slate-100 flex items-center justify-between shrink-0">
        <div>
           <h2 className="text-sm font-bold text-slate-900 uppercase tracking-tight">Description Details</h2>
           <p className="text-[10px] text-slate-400 font-bold mt-0.5">{job.company}</p>
        </div>
        <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono uppercase">ID: {Math.random().toString(36).substring(7).toUpperCase()}</span>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <section className="space-y-4">
          <div>
            <div className="flex items-center text-[10px] font-bold text-blue-600 uppercase tracking-widest mb-2">
              Matched Skills
            </div>
            <div className="flex flex-wrap gap-1">
              {job.matched_skills.split(',').map(skill => (
                <span key={skill} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-[10px] font-medium border border-blue-100">
                  {skill.trim()}
                </span>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">
              Requirements & Skill Gaps
            </div>
            <ul className="text-[11px] space-y-1.5 text-slate-600 list-disc pl-4">
              {job.gaps_in_skill.split(',').map((gap, i) => (
                <li key={i}>{gap.trim()}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="pt-6 border-t border-slate-50">
          <div className="flex items-center text-[10px] font-bold text-slate-900 uppercase tracking-widest mb-3">
            Role Description
          </div>
          <div className="text-[11px] leading-relaxed text-slate-600 whitespace-pre-wrap font-sans">
            {job.description || "No description provided."}
          </div>
        </section>
      </div>
    </div>
  );
};
